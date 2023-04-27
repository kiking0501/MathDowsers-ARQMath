"""
    Functions for post-processing generated search queries
"""
import os
import xml.etree.ElementTree as ET
from config import ARQM_PREPRO_PATH
from tqdm import tqdm
from dao import load_json, dump_json


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

        query_node = ET.SubElement(root, "Query", topic=topic_id)

        # AK: dump without processing
        for field, text in question_dict[topic_id].items():
            ET.SubElement(query_node, field).text = text

    indent(root)
    tree = ET.ElementTree(root)
    data = ET.tostring(tree.getroot(), encoding='unicode').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    with open(output_xml, "w") as output_f:
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

    indent(root)
    tree = ET.ElementTree(root)
    data = ET.tostring(tree.getroot(), encoding='unicode').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    with open(output_xml, "w") as output_f:
        output_f.write(data)
        print("%s saved." % output_f.name)


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(description="Generate data for indexing.")
    argparser.add_argument(
        "--output_folder", default=None,
        help="(Optional) The path of the output folder (where the output file will be generated). Default paths will be used if not supplied."
    )
    args = argparser.parse_args()

    if args.output_folder is None:
        location = ARQM_PREPRO_PATH
    else:
        location = args.output_folder

    ### task1
    query_method = "rewrite"
    for year in (2020,2021,2022):
        task1_json = os.path.join(ARQM_PREPRO_PATH, "task1-topics-%d-slt.json" % year)
        output_xml = os.path.join(location, "topics-task1-s23-%d.xml" % year)

        question_dict = load_json(task1_json)
        create_query_file(question_dict, query_method, output_xml)

    ### task2
    query_method = "rewrite"
    for year in (2020,2021,2022):
        task2_json = os.path.join(ARQM_PREPRO_PATH, "task2-formula-%d-slt.json" % year)
        output_xml = os.path.join(location, "topics-task2-s23-%d.xml" % year)

        question_dict = load_json(task2_json)
        create_query_file_task2(question_dict, query_method, output_xml)

