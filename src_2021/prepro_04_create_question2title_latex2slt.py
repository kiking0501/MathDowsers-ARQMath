"""
Replace latex formulas in question titles by slt (presentation MathML)
    using the given formula representation TSVs

Prerequisite:
    question2title.json has been created at the prepro folder
    formula representation TSVs files are most-updated

Effect:
    a {question_id -> title} map is created at the prepro folder,
        in which formulas from the titles are converted from latex to slt (presentation MathML)

Run by "python <name of this python file>.py"


*** NOTE ***
    This is also a relatevly light-weighted file to check for the sanity of the formula convertor
        (whether formulas in latex can be converted to to their provided slt represntation successfully)
        before proceeding to generate all the HTML files with latex formulas replaced by slt

"""


import os
from config import ARQM_PREPRO_PATH
from tqdm import tqdm
from utility.dao import load_json, dump_json
from dao_replace_formula import FormulaHTMLConverter


VERBOSE = True


def create_question2title_latex2slt(output_file):

    def _clean_title_html(title):
        s = title.replace("<html><body>", "").replace("</body></html>", "")
        if s.startswith('<p>') and s.endswith('</p>'):
            s = s[3:-4]
        return s

    question2title = load_json(
        os.path.join(ARQM_PREPRO_PATH, "question2title.json"), keys=[int], verbose=VERBOSE)

    convertor = FormulaHTMLConverter(verbose=VERBOSE)
    question2title_latex2slt = {}

    for thread_id in tqdm(sorted(question2title.keys())):
        title = question2title[thread_id]

        convertor.update_with_thread_id(thread_id)
        if not convertor.has_formula_convert_map():
            question2title_latex2slt[thread_id] = title
            continue

        title_html = convertor.latex2slt(title)
        question2title_latex2slt[thread_id] = _clean_title_html(title_html)

    dump_json(question2title_latex2slt,
              os.path.join(ARQM_PREPRO_PATH, output_file))


if __name__ == '__main__':
    create_question2title_latex2slt("question2title_latex2slt.json")
