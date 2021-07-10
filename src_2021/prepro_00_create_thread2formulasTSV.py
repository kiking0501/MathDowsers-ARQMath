"""
Create mappings for thread_id-formulas related information

Prerequisite:
    formula representation tsvs are downloaded at the designated path

Effect:
    thread2formula-related jsons are created
    ("thread2formulasTSV.json", "thread2formulasIds.json")

Run by "python <name of this python file>.py"
"""


import json
from tqdm import tqdm
import csv
import sys
from config import ARQM_FORMULAS_PATH, FORMULA_FOLDER_CONFIG
import os
from utility.dao import dump_json


csv.field_size_limit(sys.maxsize)


def create_thread2formulasTSV(folder_config=FORMULA_FOLDER_CONFIG):
    """
        create a thread2formulasTSV-dict
            to quickly locate in which TSV(s) the formulas with a specific thread_id are being stored

        Return:
            {thread-id: {"latex": ["XXX.tsv"], "slt": ["XXX.tsv"], "opt": ["XXX.tsv"]}}

    """
    thread2formulasTSV = {}

    print("[create_thread2formulasTSV] Start:")
    for formula_type in ["latex", "opt", "slt"]:
        folder_name, ind_list = folder_config[formula_type]
        print("[%s]: " % formula_type)
        folder_path = os.path.join(ARQM_FORMULAS_PATH, folder_name)

        for ind in tqdm(ind_list):
            tsv_name = "%s.tsv" % ind
            with open(os.path.join(folder_path, tsv_name)) as f:
                reader = csv.DictReader(f, dialect='excel-tab')
                for row in reader:
                    thread_id = int(row['thread_id'])
                    if thread_id not in thread2formulasTSV:
                        thread2formulasTSV[thread_id] = {}
                    if formula_type not in thread2formulasTSV[thread_id]:
                        thread2formulasTSV[thread_id][formula_type] = set()
                    thread2formulasTSV[thread_id][formula_type].add(tsv_name)

    for thread_id, content in thread2formulasTSV.items():
        for formula_type in content.keys():
            thread2formulasTSV[thread_id][formula_type] = sorted(
                list(thread2formulasTSV[thread_id][formula_type]))

    print("[create_thread2formulasTSV] Finish.")
    return thread2formulasTSV


def create_thread2formulaId_map(folder_config=FORMULA_FOLDER_CONFIG):
    """
        create a thread2formulaId-dict
            to quickly identify the range of formula-ids involved in a thread

        Return:
            {thread-id: (min-formula-id, max-formula-id)}
    """
    thread2formulaIds = {}

    print("[create_thread2formulaId_map] Start:")
    folder_name, ind_list = folder_config["latex"]  # consider only latex file
    folder_path = os.path.join(ARQM_FORMULAS_PATH, folder_name)

    for ind in tqdm(ind_list):
        tsv_name = "%s.tsv" % ind
        with open(os.path.join(folder_path, tsv_name)) as f:
            reader = csv.DictReader(f, dialect='excel-tab')
            for row in reader:
                thread_id = int(row['thread_id'])
                if thread_id not in thread2formulaIds:
                    thread2formulaIds[thread_id] = [int(row['id']), int(row['id'])]
                prev_min, prev_max = thread2formulaIds[thread_id]
                thread2formulaIds[thread_id] = [min(prev_min, int(row['id'])), max(prev_max, int(row['id']))]
    return thread2formulaIds


if __name__ == '__main__':
    from config import ARQM_PREPRO_PATH
    thread2formulasTSV = create_thread2formulasTSV()
    dump_json(thread2formulasTSV,
              os.path.join(ARQM_PREPRO_PATH, "thread2formulasTSV.json"))
    thread2formulaIds = create_thread2formulaId_map()
    dump_json(thread2formulaIds,
              os.path.join(ARQM_PREPRO_PATH, "thread2formulaIds.json"))
