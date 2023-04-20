#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import csv
import sys
import re

trunc = 2 # need more than trunc chars to keep term
ignore = r'\W|_'

def stop_text(str):
    return " ".join(list(filter(lambda x: len(x)>trunc, re.split(ignore,str))))

def read_latex_files(formula_index_directory_path):
    dictionary_formula_id = {}
    for filename in os.listdir(formula_index_directory_path):
        #print("loading data "+filename, file=sys.stderr)
        with open(formula_index_directory_path + "/" + filename, newline='', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            next(csv_reader)
            for row in csv_reader:
                formula_id = int(row[0])
                formula = row[8]
                st = stop_text(formula.strip())
                if (st != ""):
                    dictionary_formula_id[formula_id] = st
                    #print("["+str(formula_id)+"]"+ st)
    return dictionary_formula_id

def main():
    """
    Sample command:
    python3 latex_filter_stopwords.py < input.xml > output.xml
    -tsv "qrel_task2_2022.tsv"|inline
    """
    parser = argparse.ArgumentParser(description='adds stopped latex to task2 math input files')

    parser.add_argument('-tsv', help='Directory path in which there are the latex tsv files', required=True)
    args = vars(parser.parse_args())

    tsv_dir = args['tsv']  #
    #dictionary_formula_id = {2:"X"}
    inline = False
    if (tsv_dir == "inline"):
        inline = True;
    else:
        dictionary_formula_id = read_latex_files(tsv_dir)

    if (not inline):
        with sys.stdin as fin:
            for line in fin:
                print(line, end='')
                if (line.startswith("<DOCNO>")):
                    formula_id = int(re.split('<DOCNO>([0-9]*)_',line)[1])
                    #print(formula_id)
                    if (formula_id in dictionary_formula_id):
                        print(dictionary_formula_id[formula_id])
    else:
        with sys.stdin as fin:
            for line in fin:
                splits = re.findall('alttext="(([^"]|\\")*?)" ',line)
                for sp in splits:
                     sp = stop_text(sp[0].strip())
                     if (sp != ""):
                          print(sp)
                print(line, end='')
    #print(stop_text(line.strip()))


if __name__ == "__main__":
    main()
