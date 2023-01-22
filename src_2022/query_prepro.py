"""
A preprocessing step for task topics before generating search queries
    - convert given XML file to JSON files, with simple HTML cleansing
    - save copies that already convert contained formulas to SLT

Prerequisite:
    topic files has been downloaded according to <TASK_FORMULA_FOLDER_CONFIG> in config.py

Effect:
    cleaned task topic files are created at <ARQM_EXPERIMENTS_PATH>/topics

Run by "python <name of this python file>.py"

"""


import os
from config import ARQM_EXPERIMENTS_PATH, TASK_FORMULA_FOLDER_CONFIG, ARQM_TASK1_PATH, ARQM_TASK2_PATH
import xml.etree.ElementTree as ET
from utility.dao import dump_json, load_json, sort_topic_ids, sort_formula_ids
from dao_read_formula_tsv import read_task_formula_tsv
from dao_replace_formula import create_formula_map, html_latex2slt, html_escape
from tqdm import tqdm


### OUTPUT destinations
TASK1_TOPICS = {
    2020: os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "task1-topics-2020.json"),
    2021: os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "task1-topics-2021.json"),
    2022: os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "task1-topics-2022.json")
}

TASK2_TOPICS = {
    2020: os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "task2-formula-2020.json"),
    2021: os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "task2-formula-2021.json"),
    2022: os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2022", "task2-formula-2022.json")
}

def topics_xml2json(xml_path, output_file):
    """ Convert topic XML file to JSON file """
    topics_ET = ET.parse(xml_path)

    topics_dict = {}

    for topic in topics_ET.getroot():
        topic_id = topic.attrib['number']
        topics_dict[topic_id] = {}
        for sect in topic:
            topics_dict[topic_id][sect.tag] = sect.text

    dump_json(topics_dict, output_file)
    return topics_dict


def _clean_title_html(title):
    s = title.replace("<html><body>", "").replace("</body></html>", "")
    return s


def create_converted_slt_representation(year):
    """ Simple cleansing for easier RE processing later """
    from prepro_00_modify_formula_representation import FormulaConvertByNaiveMatching
    slt_tsv = read_task_formula_tsv(year, "slt_original", groupby_list=["id"])

    total = 0
    num_updated = 0
    updated_items = []
    for formula_id in tqdm(sort_formula_ids(slt_tsv.keys())):
        total += 1
        item = slt_tsv[formula_id][0]

        item['formula'] = item['formula'].strip()
        d, r = FormulaConvertByNaiveMatching.get_replacement_regex()
        update_slt = FormulaConvertByNaiveMatching.naive_clean_pmml(item['formula'].replace("  ", "").replace("> <", "><"),d,r)
        if update_slt:
            num_updated += 1
            item['formula'] = update_slt

        updated_items.append(item)

    print("Updated %d/%d (%.2f%%) items." % (num_updated, total, num_updated*100/total))
    headers = ["id", "topic_id", "thread_id", "type", "formula"]
    with open(TASK_FORMULA_FOLDER_CONFIG[year]["slt"], "w") as f:
        f.write("\t".join(headers) + "\n")
        for item in updated_items:
            f.write("\t".join([str(item[k]) for k in headers]) + "\n")
        print("%s saved." % f.name)


def create_task1_topics_slt(year):
    """ Replace latex formulas in Task 1 topics to SLT """
    task1_topics = load_json(TASK1_TOPICS[year], verbose=True)
    formulaTSVs = {
        formula_type: read_task_formula_tsv(
            year, formula_type, groupby_list=["topic_id", "id"])
        for formula_type in ("latex", "slt")
    }
    for topic_id in tqdm(sort_topic_ids(task1_topics.keys())):
        latex2slt_formulas = create_formula_map(
            formulaTSVs["latex"].get(topic_id, {}), formulaTSVs["slt"].get(topic_id, {})
        )
        for k in ("Title", "Question"):
            slt_html = html_latex2slt(
                task1_topics[topic_id][k].strip(), topic_id, formulaTSVs, latex2slt_formulas
            )
            task1_topics[topic_id][k] = _clean_title_html(slt_html)

    dump_json(task1_topics, TASK1_TOPICS[year].partition('.')[0] + "-slt" + ".json")


def create_task2_topics_slt(year):
    """ Replace latex formulas in Task 2 topics to SLT """
    task2_topics = load_json(TASK2_TOPICS[year], verbose=True)
    formulaTSVs = {
        formula_type: read_task_formula_tsv(
            year, formula_type, groupby_list=["topic_id", "id"])
        for formula_type in ("latex", "slt")
    }
    for task2_topic_id in tqdm(sort_topic_ids(task2_topics.keys())):
        topic_id = task2_topic_id.replace("B", "A")
        # use formulas provided in Task 1 for convenience

        latex2slt_formulas = create_formula_map(
            formulaTSVs["latex"].get(topic_id, {}), formulaTSVs["slt"].get(topic_id, {})
        )

        for k in ("Title", "Question"):
            slt_html = html_latex2slt(
                task2_topics[task2_topic_id][k].strip(), topic_id, formulaTSVs, latex2slt_formulas
            )
            task2_topics[task2_topic_id][k] = _clean_title_html(slt_html)

        query_formula_id = task2_topics[task2_topic_id]["Formula_Id"]
        task2_topics[task2_topic_id]["Query_Formula"] = html_escape(formulaTSVs["slt"][topic_id][query_formula_id][0]["formula"])

    dump_json(task2_topics, TASK2_TOPICS[year].partition('.')[0] + "-slt" + ".json")


if __name__ == '__main__':
    #### Task1
    for xml_path, output_path in (
        (os.path.join(ARQM_TASK1_PATH, "ARQMath_2020", "Topics", "Topics_V2.0.xml"), TASK1_TOPICS[2020]),
        (os.path.join(ARQM_TASK1_PATH, "ARQMath_2021", "Topics", "Topics_Task1_2021_V1.1.xml"), TASK1_TOPICS[2021]),
        (os.path.join(ARQM_TASK1_PATH, "ARQMath_2022", "Topics", "Topics_Task1_2022_V0.1.xml"), TASK1_TOPICS[2022]),
    ):
        topics_xml2json(xml_path, output_path)
    create_converted_slt_representation(2020)
    for year in (2020, 2021, 2022):
        create_task1_topics_slt(year)


    #### Task2
    for xml_path, output_path in (
        (os.path.join(ARQM_TASK2_PATH, "ARQMath_2020", "Topics", "Topics_V1.1.xml"), TASK2_TOPICS[2020]),
        (os.path.join(ARQM_TASK2_PATH, "ARQMath_2021", "Topics", "Topics_Task2_2021_V1.1.xml"), TASK2_TOPICS[2021]),
        (os.path.join(ARQM_TASK2_PATH, "ARQMath_2022", "Topics", "Topics_Task2_2022_V0.1.xml"), TASK2_TOPICS[2022]),
    ):
        topics_xml2json(xml_path, output_path)
    for year in (2020, 2021, 2022):
        create_task2_topics_slt(year)

