"""
    Functions to help read a formula tsv file
"""
import os
import csv
import sys
from config import ARQM_FORMULAS_PATH, FORMULA_FOLDER_CONFIG, TASK_FORMULA_FOLDER_CONFIG
from dao import clean_escape_html


csv.field_size_limit(sys.maxsize)


def simple_transform_slt(text):
    return text.strip().replace("display=\"block\"", "display=\"inline\"")


def list2dict_groupby(li, groupby_field, html_escape=True, int_convert=True):
    """
        return {groupby_field: list of correpsonding items}
        id fields are converted to integers
    """
    d = {}
    for row in li:
        int_row = {
            k: int(v) if k.endswith('id') and int_convert
            else clean_escape_html(v) if k == "formula" and html_escape
            else v for k, v in row.items() if v    # only record non-empty fields in V3
        }
        if "formula" in int_row:
            int_row["formula"] = simple_transform_slt(int_row["formula"])

        groupby_id = int_row[groupby_field]
        if groupby_id not in d:
            d[groupby_id] = []
        d[groupby_id].append(int_row)
    return d


def recursive_list2dict_groupby(li, groupby_list, html_escape=True, int_convert=True):
    """
        groupby_list is a list of fields
        if gropuby_list is empty, return the original list of items
        otherwise, return a dict of
            {groupby_field1: {groupby_field2: {... groupby_field_n: list of items}}
    """
    if not groupby_list:
        return li
    d = list2dict_groupby(li, groupby_list[0], html_escape, int_convert)
    for k, sub_li in d.items():
        d[k] = recursive_list2dict_groupby(sub_li, groupby_list[1:], html_escape=html_escape, int_convert=int_convert)
    return d


def recursive_combine_dict(dict1, dict2):
    """
        add content of dict2 to dict1
    """
    for k, v in dict2.items():
        if k not in dict1:
            dict1[k] = v
        else:
            if isinstance(v, dict):
                dict1[k] = recursive_combine_dict(dict1[k], v)
            else:
                dict1[k] += v
    return dict1



def read_formula_tsv(formula_type, tsv_names, groupby_list, folder_config=FORMULA_FOLDER_CONFIG, html_escape=False):
    """
        Read a formula tsv file by formula_type[slt/latex] and then by its tsv_name[XXX.tsv]
         Return a Python dictionary object which is grouped by the field names in the groupby_list

        E.g. a tsv with columns "id", "thread_id", post_id", "formula"
            setting groupby_list=["thread_id", post_id"] will return a map of
            {thread_id -> {post_id: [list of formula items that have the same thread-id and post-id]}}
    """
    folder_name, _ = folder_config[formula_type]

    overall_dict = {}
    for tsv_name in tsv_names:
        tsv_path = os.path.join(ARQM_FORMULAS_PATH, folder_name, tsv_name)
        with open(tsv_path) as f:
            reader = csv.DictReader(f, dialect='excel-tab')
            tsv_dict = recursive_list2dict_groupby(reader, groupby_list, html_escape=html_escape)
            overall_dict = recursive_combine_dict(overall_dict, tsv_dict)

    return overall_dict


def read_task_formula_tsv(year, formula_type, groupby_list, html_escape=False):
    """
        Read a tas formula tsv file by year [2020/2021] and then by its formula_type[slt/latex]
         Return a Python dictionary object which is grouped by the field names in the groupby_list

        See read_formula_tsv
    """
    overall_dict = {}
    tsv_path = TASK_FORMULA_FOLDER_CONFIG[year][formula_type]
    with open(tsv_path) as f:
        reader = csv.DictReader(f, dialect='excel-tab', fieldnames=("id", "topic_id", "thread_id", "type", "formula"))
        reader = [x for x in reader if x["id"] != "id"]
        tsv_dict = recursive_list2dict_groupby(reader, groupby_list, html_escape=html_escape, int_convert=False)
        overall_dict = recursive_combine_dict(overall_dict, tsv_dict)
    return overall_dict
