"""
Modify the formula representation tsvs, so that
- PresentationMathml (the slt folder) contains more accurate presenations

This is done because of the problems of the Lab-provided formula representation tsv files
It can be skipped if the Lab-provided files have become bug-free in the future version.

Prerequisite:
    formula representation tsvs are downloaded at the designated path

Effect:
    A new folder of formula representation tsvs for Presentation Mathml (the slt folder),
        that contains only the adjusted items, will be created

    A final folder of formula representation tsvs for Presentation Mathml (the slt folder),
        that contains all the items most updated, will be created

** NOTE **
    if this file is skipped,
    at config.py, FORMULA_FOLDER_CONFIG["slt"] should be changed to match FORMULA_FOLDER_CONFIG["original_slt"]

Run by "python <name of this python file>.py"

"""


from config import FORMULA_FOLDER_CONFIG, ARQM_FORMULAS_PATH
from utility.dao import (
    HTML_CHAR_MAP, clean_escape_html, multiple_str_sub, multiple_str_regex
)
from dao_read_formula_tsv import read_formula_tsv, read_formula_tsv_by_path
import os
from tqdm import tqdm
import subprocess


HEADERS = ["id", "post_id", "thread_id", "type", "visual_id", "formula"]


class FormulaConvertByNaiveMatching:
    """
        For a formula representation tsv,
            detect specific patterns from the Presentation Mathml which involved escaped html characters
                (e.g. "&lt;" instead of "<"),
            and convert them into the correct pattern

        Return only affect items

        *** Naive matching recovered ~3.92% formulas (1107920 / 28282477) for all 6 patterns
            If not using the latter 2 &amp patterns: ~3.07% formulas (869074 / 28282477)

    """
    REPLACEMENT_LIST = [
        {
            '<mo>⁢</mo><mi mathvariant=\"normal\">&amp;</mi><mo>⁢</mo><mi>%s</mi></mrow><mo>;</mo>' % k:
            '<mo>&%s;</mo></mrow>' % k
            for k in ('lt', 'gt')
        },
        {
            '<mo>⁢</mo><mi mathvariant=\"normal\">&amp;</mi><mo>⁢</mo><mi>%s</mi></mrow></mrow><mo>;</mo>' % k:
            '<mo>&%s;</mo></mrow></mrow>' % k
            for k in ('lt', 'gt')
        },

        {
            '<mo>⁢</mo><mi mathvariant=\"normal\">&amp;</mi><mo>⁢</mo><mi>%s</mi><mo>⁢</mo><mi>%s</mi></mrow><mo>;</mo>' % (k[0], k[1]):
            '<mo>&%s;</mo></mrow>' % k
            for k in ('lt', 'gt')
        },
        {
            '<mo>⁢</mo><mi mathvariant=\"normal\">&amp;</mi><mo>⁢</mo><mi>%s</mi><mo>⁢</mo><mi>%s</mi></mrow></mrow><mo>;</mo>' % (k[0], k[1]):
            '<mo>&%s;</mo></mrow></mrow>' % k
            for k in ('lt', 'gt')
        },

        # {
        #     '<mi mathvariant=\"normal\">&amp;</mi><mi>a</mi><mi>m</mi><mi>p</mi><mo>;</mo>':
        #     '<mi mathvariant=\"normal\">&amp;</mi><mo>⁢</mo>'
        # },
        # {
        #     '<mi mathvariant=\"normal\">&amp;</mi><mrow><mi>a</mi><mo>⁢</mo><mi>m</mi><mo>⁢</mo><mi>p</mi></mrow><mo>;</mo>':
        #     '<mi mathvariant=\"normal\">&amp;</mi><mo>⁢</mo>'
        # }
    ]
    UPDATE_HEADERS = ["pmml"]

    @staticmethod
    def naive_clean_pmml(formula, REPLACEMENT_DICT, REPLACEMENT_REGEX):
        clean_pmml = multiple_str_sub(REPLACEMENT_REGEX, REPLACEMENT_DICT, formula)
        if clean_pmml == formula:
            return None
        return clean_pmml

    @classmethod
    def get_replacement_regex(cls):
        REPLACEMENT_DICT = {}
        for r_dict in cls.REPLACEMENT_LIST:
            REPLACEMENT_DICT = dict(REPLACEMENT_DICT, **r_dict)

        REPLACEMENT_REGEX = multiple_str_regex(REPLACEMENT_DICT)
        return REPLACEMENT_DICT, REPLACEMENT_REGEX

    @classmethod
    def main(cls, tsv_name):

        def _add_naive_clean_pmml(items):
            REPLACEMENT_DICT, REPLACEMENT_REGEX = cls.get_replacement_regex()

            update_items = []
            for item in tqdm(items):
                pmml = cls.naive_clean_pmml(item['formula'], REPLACEMENT_DICT, REPLACEMENT_REGEX)
                if pmml is not None:
                    item["pmml"] = pmml
                    update_items.append(item)
            return update_items

        slt_tsv = read_formula_tsv(
            "original_slt", [tsv_name], groupby_list=["id"]
        )
        custom_items = [formula_content[0] for formula_content in slt_tsv.values()]
        custom_items = _add_naive_clean_pmml(custom_items)
        return custom_items


class FormulaConvertByLatex2MathML:
    """
        For a formula representation tsv,
            detect all Presentation Mathml formulas which have escaped html characters (e.g. "&lt;" instead of "<"),
            re-convert those html characters, and then convert to pmml again using the Python library latexmathml

        Return only affected items

        Prerequisites:
            sudo apt-get install latexml
            sudo apt get install libtext-unidecode-perl
    """

    UPDATE_HEADERS = ["cleaned_formula", "pmml"]

    @staticmethod
    def latex2pmml(formula):
        def _clean_pmml(pmml):
            pmml = pmml.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
            pmml = pmml.replace("display=\"block\"", "display=\"inline\"")
            pmml = pmml.replace("\n", "")
            return pmml

        p = subprocess.run(
            ["latexmlmath", "-"],
            input=formula.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if p.returncode == 0:
            return _clean_pmml(p.stdout.decode("utf-8"))
        return None

    @classmethod
    def main(cls, tsv_name):

        def _get_html_escaped_items(formula_tsv):
            items = []
            for formula_id, formula_content in formula_tsv.items():
                if any([k in formula_content[0]['formula'] for k in HTML_CHAR_MAP.keys()]):
                    items.append(formula_content[0])
            return items

        def _add_unescaped_formulas(items):
            update_items = []
            for item in items:
                item['cleaned_formula'] = clean_escape_html(item['formula'])
                update_items.append(item)
            return update_items

        def _add_latex2pmml(items):
            update_items = []
            for ind, item in enumerate(tqdm(items)):
                pmml = cls.latex2pmml(item['cleaned_formula'])
                if pmml is not None:
                    item["pmml"] = pmml
                    update_items.append(item)
            return update_items

        latex_tsv = read_formula_tsv(
            "latex", [tsv_name], groupby_list=["id"]
        )
        custom_items = _get_html_escaped_items(latex_tsv)
        custom_items = _add_unescaped_formulas(custom_items)
        custom_items = _add_latex2pmml(custom_items)

        return custom_items


def create_custom_formula_convert_map(formulaConvertClass):
    """
        Create a folder of custom formula representation tsvs used for mapping
        Contain only formula items that have been converted

        formulaConvertClass can be either
            - FormulaConvertByNaiveMatching  (faster, but detect only certain patterns)
            - FormulaConvertByLatex2MathML (slower but detect all malfunctioned formulas)
    """

    CUSTOM_MAP_FOLDER = os.path.join(ARQM_FORMULAS_PATH, FORMULA_FOLDER_CONFIG["slt_convert_map"][0])
    os.makedirs(CUSTOM_MAP_FOLDER, exist_ok=True)

    _, ind_list = FORMULA_FOLDER_CONFIG["original_slt"]

    for ind in tqdm(ind_list):
        tsv_name = "%s.tsv" % ind
        custom_items = formulaConvertClass.main(tsv_name)

        with open(os.path.join(CUSTOM_MAP_FOLDER, tsv_name), "w") as f:
            f.write("\t".join(HEADERS + formulaConvertClass.UPDATE_HEADERS) + "\n")
            for item in custom_items:
                f.write("\t".join([str(item[k]) for k in HEADERS + formulaConvertClass.UPDATE_HEADERS]) + "\n")

    print("Finish saving converted formula items at %s." % CUSTOM_MAP_FOLDER)


def _get_affected_thread_ids(folder_name=FORMULA_FOLDER_CONFIG["slt_convert_map"]):
    """ Get affected thread-ids within the convert-map file
    """
    _, ind_list = FORMULA_FOLDER_CONFIG["original_slt"]
    folder_path = os.path.join(ARQM_FORMULAS_PATH, folder_name)

    affected_ids = set()
    for ind in tqdm(ind_list):
        tsv_name = "%s.tsv" % ind
        convert_map = read_formula_tsv_by_path(
            os.path.join(folder_path, tsv_name), groupby_list=["thread_id"]
        )
        affected_ids.update(convert_map.keys())
    return affected_ids


def create_final_converted_slt_representation():
    """
        Update the original formulas by the the customized formulas
            and save the overall converted formula represntation tsvs to a new folder
    """
    CONVERTED_FOLDER = os.path.join(ARQM_FORMULAS_PATH, FORMULA_FOLDER_CONFIG["slt"][0])
    os.makedirs(CONVERTED_FOLDER, exist_ok=True)

    _, ind_list = FORMULA_FOLDER_CONFIG["original_slt"]

    num_updated = 0
    total = 0
    for ind in tqdm(ind_list):
        tsv_name = "%s.tsv" % ind

        slt_tsv = read_formula_tsv(
            "original_slt", [tsv_name], groupby_list=["id"]
        )
        custom_convert_map = read_formula_tsv(
            "slt_convert_map", [tsv_name], groupby_list=["id"]
        )

        updated_items = []
        for formula_id, formula_content in slt_tsv.items():
            total += 1
            item = formula_content[0]
            if formula_id in custom_convert_map:
                item['formula'] = custom_convert_map[formula_id][0]['pmml']
                num_updated += 1
            updated_items.append(item)

        with open(os.path.join(CONVERTED_FOLDER, tsv_name), "w") as f:
            f.write("\t".join(HEADERS) + "\n")
            for item in updated_items:
                f.write("\t".join([str(item[k]) for k in HEADERS]) + "\n")

    print("Finish saving final converted representation tsv at %s." % CONVERTED_FOLDER)
    print("Updated formulas: %d / %d (%.2f %%)" % (num_updated, total, num_updated*100/total))


if __name__ == '__main__':
    create_custom_formula_convert_map(FormulaConvertByNaiveMatching)
    create_final_converted_slt_representation()
