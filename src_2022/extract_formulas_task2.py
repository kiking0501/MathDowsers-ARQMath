"""
    Read in all formulas from slt_representation_v3 convert to TRECDOC format and output to gzip file.
"""

import os
import csv
import sys
import re
import gzip
from config import ARQM_OUTPUT_HTML_MINIMAL_PATH, ARQM_FORMULAS_PATH
from dao_replace_formula import html_escape
from dao_read_formula_tsv import simple_transform_slt

csv.field_size_limit(sys.maxsize)

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(description="Generate data for indexing.")
    argparser.add_argument(
        "--output_folder", default=None,
        help="(Optional) The path of the output folder (where the output file will be generated). Default paths will be used if not supplied."
    )
    args = argparser.parse_args()

    seen = set()
    sltdir = os.path.join(ARQM_FORMULAS_PATH, "slt_representation_v3/")
    if args.output_folder is None:
        extfile = ARQM_OUTPUT_HTML_MINIMAL_PATH+"/task2_2022_data.xml.gz"
    else:
        extfile = args.output_folder+"/task2_2022_data.xml.gz"
    print("output to "+extfile, file=sys.stderr)
    out = gzip.open(extfile, "wt")
    #out = open(sys.stdout.fileno(), mode='w', encoding='utf8')
    for p in os.listdir(sltdir):
        with open(sltdir+p) as f:
            print(sltdir+p, file=sys.stderr)
            reader = csv.DictReader(f,dialect='excel-tab')
            for row in reader:
                if ((row["type"] == "answer" or row["type"] == "question") and row["visual_id"] not in seen):
                    seen.add(row["visual_id"])
                    print("<DOC>", file=out)
                    print("<DOCNO>",row["id"],"_",row["post_id"],"_",row["visual_id"],"</DOCNO>", sep='', file=out)
                    print(simple_transform_slt(html_escape(row["formula"])), file=out) 
                    print("</DOC>", file=out)
