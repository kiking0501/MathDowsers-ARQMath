"""
Modify the formula representation tsvs, so that
- PresentationMathml (the slt folder) contains more accurate presenations

This is done because of the problems of the Lab-provided formula representation tsv files
It can be skipped if the Lab-provided files have become bug-free in the future version.

Prerequisite:
    formula representation tsvs are downloaded at <ARQM_FORMULAS_PATH>

Effect:
    A new folder of formula representation tsvs for Presentation Mathml ("custom_slt_convert_map_v2_patterns"),
        that contains only the adjusted items, will be created

    A final folder of formula representation tsvs for Presentation Mathml ("slt_representation_v2_converted"),
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

