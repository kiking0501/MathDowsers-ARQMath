"""
    Functions for post-processing generated search queries
"""
from query_model import get_queries
import xml.etree.ElementTree as ET
import json
from config import ARQM_TASK1_PATH, ARQM_EXPERIMENTS_PATH
import os
import re
from tqdm import tqdm
from utility.dao import load_json, dump_json
import pandas as pd
from pandas import DataFrame as df


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    for elem in elem:
        indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
        elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def create_query_file(question_dict, query_method, output_xml):
    """ Print generated search queries in a proper XML file """
    root = ET.Element("Topics")

    topic_ids = sorted(question_dict.keys(), key=lambda x: int(x.partition('.')[2]))
    for ind in tqdm(range(len(topic_ids))):
        topic_id = topic_ids[ind]
        queries = get_queries(query_method, question_dict[topic_id], topic_id=topic_id)

        query_node = ET.SubElement(root, "Query", topic=topic_id)
        for ind, term in enumerate(queries):
            if term.startswith("<math"):
                ET.SubElement(query_node, "input", id=str(ind), type="formula").text = term
            else:
                ET.SubElement(query_node, "input", id=str(ind), type="keyword").text = term

    tmp_xml = output_xml.rpartition('.')[0] + '_validText.xml'
    indent(root)
    tree = ET.ElementTree(root)
    tree.write(tmp_xml)

    with open(tmp_xml) as inp_f:
        with open(output_xml, "w") as output_f:
            data = inp_f.read().replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            output_f.write(data)
            print("%s saved." % output_f.name)


def read_query_file(xml_path):
    """ Read the above generated XML file back to search queries in Dictionary object"""
    topics_ET = ET.parse(xml_path)

    query_dict = {}
    for query in topics_ET.getroot():
        topic_id = query.attrib['topic']
        query_dict[topic_id] = {
            'formula': [],
            'keyword': [],
        }
        for inp in query:
            query_dict[topic_id][inp.attrib['type']].append(inp.text)
    return query_dict


def create_term_freq_json(question_dict, query_method, output_json):
    """ Get Term Frequencies """

    term_freq_dict = {}

    topic_ids = sorted(question_dict.keys(), key=lambda x: int(x.partition('.')[2]))
    for ind in tqdm(range(len(topic_ids))):
        topic_id = topic_ids[ind]
        term_freq_dict[topic_id] = {}

        queries = get_queries(query_method, question_dict[topic_id], topic_id=topic_id)
        for term in queries:
            if term.lower() not in term_freq_dict[topic_id]:
                term_freq_dict[topic_id][term.lower()] = 0
            term_freq_dict[topic_id][term.lower()] += 1

    dump_json(term_freq_dict, output_json)


def create_description_stats(question_dict, query_methods, output_csv):
    """ Get Description Stats for Search Queries """
    topic_ids = sorted(question_dict.keys(), key=lambda x: int(x.partition('.')[2]))

    result_dict = {}
    for query_method in query_methods:

        result_dict[query_method] = {
           "topic_id": [], "keyword_count": [], "formula_count": [], "formula-to-keyword": []}

        for ind in tqdm(range(len(topic_ids))):
            topic_id = topic_ids[ind]
            result_dict[query_method]["topic_id"].append(topic_id)

            queries = get_queries(query_method, question_dict[topic_id], topic_id=topic_id)
            keyword_ct, formula_ct = 0, 0
            for term in queries:
                if term.startswith("<"):
                    formula_ct += 1
                else:
                    keyword_ct += 1

            result_dict[query_method]["keyword_count"].append(keyword_ct)
            result_dict[query_method]["formula_count"].append(formula_ct)
            result_dict[query_method]["formula-to-all"].append(float(formula_ct) / (formula_ct + keyword_ct))

    all_df = None
    for ind, query_method in enumerate(query_methods):
        res_df = df.from_dict(result_dict[query_method])
        adj_df = res_df[["keyword_count", "formula_count", "formula-to-keyword"]].describe().T
        if all_df is None:
            all_df = adj_df
            all_df = all_df.set_index([
                [query_method, query_method, query_method],
                ["keyword_count", "formula_count", "formula-to-keyword"] * (ind + 1)
            ])
        else:
            row_index = []
            for qm in query_methods[:ind+1]:
                row_index.extend([qm, qm, qm])
            all_df = all_df.append(adj_df).set_index(
                [row_index,
                    ["keyword_count", "formula_count", "formula-to-keyword"] * (ind + 1)
                ]
            )
    all_df.to_csv(output_csv, sep = '\t')
    print("%s saved." % output_csv)


if __name__ == '__main__':
    ### Verified the same with last year
    # task1_json = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2020", "task1-topics-slt.json")
    # output_xml = os.path.join(ARQM_TASK1_PATH, "ARQMath_2020", "Topics", "MathDowsers_Queries_V1_0_regenerate.xml")
    ####

    ### Print Query File for "unique"
    # query_method = "unique"
    # year = 2021
    # task1_json = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2021", "task1-topics-%d-slt.json" % year)
    # output_xml = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2021", "MathDowsers_Queries_task1-topics-%d-%s.xml" % (year, query_method))

    # question_dict = load_json(task1_json)
    # create_query_file(
    #     question_dict, query_method, output_xml)
    ####

    ### Study Search Query for "rewrite"
    # query_method = "rewrite"
    # for year in [2020, 2021]:
    #     task1_json = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2021", "task1-topics-%d-slt.json" % year)
    #     question_dict = load_json(task1_json)
    #     output_json = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2021", "task1-termCount-%d-%s.json" % (year, query_method))
    #     create_term_freq_json(question_dict, query_method, output_json)
    ####

    for year in [2020]:
        task1_json = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2021", "task1-topics-%d-slt.json" % year)
        question_dict = load_json(task1_json)
        output_tsv = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2021", "thesis-task1-query_methods-descriptive-stats-%d.tsv" % (year))
        create_description_stats(
            question_dict,
            ["human_translated_2020_break", "plain", "remove_stopword_ff", "MSE_ff", "Wiki_ff", "rewrite"],
            output_tsv
        )
