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


def create_query_file_task2(question_dict, query_method, output_xml):
    """ Print generated search queries in a proper XML file """
    root = ET.Element("Topics")

    topic_ids = sorted(question_dict.keys(), key=lambda x: int(x.partition('.')[2]))
    for ind in tqdm(range(len(topic_ids))):
        topic_id = topic_ids[ind]
        query_node = ET.SubElement(root, "Query", topic=topic_id)
        ET.SubElement(query_node, "input", id=str(0), type="formula").text = question_dict[topic_id]["Query_Formula"]
        #ET.SubElement(query_node, "input", id=str(1), type="keyword").text = question_dict[topic_id]["Tags"] # AK:

    tmp_xml = output_xml.rpartition('.')[0] + '_validText.xml'
    indent(root)
    tree = ET.ElementTree(root)
    tree.write(tmp_xml)

    with open(tmp_xml) as inp_f:
        with open(output_xml, "w") as output_f:
            data = inp_f.read().replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            output_f.write(data)
            print("%s saved." % output_f.name)


if __name__ == '__main__':

    ### task1
    query_method = "rewrite"
    for year in (2020,2021,2022):
        task1_json = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "task1-topics-%d-slt.json" % year)
        output_xml = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "MathDowsers_Queries_task1-topics-%d-%s.xml" % (year, query_method))

        question_dict = load_json(task1_json)
        create_query_file(question_dict, query_method, output_xml)

    ### task2
    query_method = "rewrite"
    for year in (2020,2021,2022):
        task2_json = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "task2-formula-%d-slt.json" % year)
        output_xml = os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "MathDowsers_Queries_task2-topics-%d-%s.xml" % (year, query_method))

        question_dict = load_json(task2_json)
        create_query_file_task2(question_dict, query_method, output_xml)

