"""
    Functions to select seach query keywords and formulas
"""

import re
import os
from dao_replace_formula import FormulaProcessor, MATH_CONTAINER_PATTERNS
from query_filters import (
    STEMMER, TOKENIZER, is_stopword, tokenize, is_hyphenated_token, remove_punctuation,
    STEMMED_TAG_KEYWORDS, STEMMED_WIKI_KEYWORDS)
from utility.dao import load_json


def is_stopword_formula(formula):
    alttext = FormulaProcessor.extract_alttext(formula)
    if alttext:
        if len(alttext) == 1:
            return True
        try:
            float(alttext)
            return True
        except Exception:
            return False
    return True

LATEX_STOPWORD = {"\\big", "\\text"}


######## Apply to raw text
def remove_xml_syntax(text):
    return text.replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip()


def remove_html_tags(text):
    return re.sub("<.*?>", "", text, flags=re.DOTALL)


def remove_formulas(text):
    for pattern in MATH_CONTAINER_PATTERNS:
        for (str_formula_id, formula), math_container in FormulaProcessor.extract_formulas(text, [pattern]):
            text = text.replace(math_container, " ")
    return text


def get_query_formulas(question_content, keep_math_container=False, filter_formula=True):
    """ Select & Filter Formulas """
    query_dict = {}

    for field in ['Title', 'Question']:
        query_dict[field] = []
        text = question_content[field]

        for pattern in MATH_CONTAINER_PATTERNS:
            for (str_formula_id, formula), math_container in FormulaProcessor.extract_formulas(text, [pattern]):
                    query_dict[field].append((str_formula_id, remove_xml_syntax(formula)))

    query_dict['Question'] = [
        (formula_id, x) for formula_id, x in query_dict['Question']
        if not filter_formula or (filter_formula and not is_stopword_formula(x))]

    return query_dict


def get_query_keywords(question_content, keyword_type="MSEWiki"):
    """ Select & Filter Keywords """
    query_dict = {}

    for field in ['Title', 'Question', 'Tags']:
        if field == "Tags":
            text = question_content[field].replace(",", " ")
        else:
            # text = remove_html_tags(remove_formulas(question_content[field]).strip())
            text = remove_html_tags((question_content[field]).strip())
        query_dict[field] = []

        for tag in tokenize(text):

            if keyword_type == "MSEWiki":
                if is_stopword(tag.lower()):
                    continue
                stem_tag = STEMMER.stem(tag.lower())
                if is_hyphenated_token(stem_tag):
                    query_dict[field].append(tag)
                elif stem_tag in STEMMED_TAG_KEYWORDS or stem_tag in STEMMED_WIKI_KEYWORDS:
                    query_dict[field].append(tag)
                else:
                    if stem_tag in LATEX_STOPWORD:
                        continue

                    stem_tag = remove_punctuation(stem_tag)
                    if is_stopword(stem_tag):
                        continue
                    if stem_tag in STEMMED_TAG_KEYWORDS or stem_tag in STEMMED_WIKI_KEYWORDS:
                        query_dict[field].append(remove_punctuation(tag))

            elif keyword_type == "plain":
                query_dict[field].append(tag)

            elif keyword_type == "remove_stopword":
                if is_stopword(tag.lower()):
                    continue
                query_dict[field].append(tag)

            elif keyword_type == "MSE":
                if is_stopword(tag.lower()):
                    continue
                stem_tag = STEMMER.stem(tag.lower())
                if is_hyphenated_token(stem_tag):
                    query_dict[field].append(tag)
                elif stem_tag in STEMMED_TAG_KEYWORDS:
                    query_dict[field].append(tag)
                else:
                    if stem_tag in LATEX_STOPWORD:
                        continue

                    stem_tag = remove_punctuation(stem_tag)
                    if is_stopword(stem_tag):
                        continue
                    if stem_tag in STEMMED_TAG_KEYWORDS:
                        query_dict[field].append(remove_punctuation(tag))

            elif keyword_type == "Wiki":
                if is_stopword(tag.lower()):
                    continue
                stem_tag = STEMMER.stem(tag.lower())
                if is_hyphenated_token(stem_tag):
                    query_dict[field].append(tag)
                elif stem_tag in STEMMED_WIKI_KEYWORDS:
                    query_dict[field].append(tag)
                else:
                    if stem_tag in LATEX_STOPWORD:
                        continue

                    stem_tag = remove_punctuation(stem_tag)
                    if is_stopword(stem_tag):
                        continue
                    if stem_tag in STEMMED_WIKI_KEYWORDS:
                        query_dict[field].append(remove_punctuation(tag))

    return query_dict


def get_query_list(question_content,
                   formula_unique=False,
                   keyword_unique=False,
                   get_formula=True,
                   get_keyword=True,
                   filter_formula=True,
                   keyword_type="MSEWiki",
                   verbose=False,
                   **kwargs):
    """ Get a list of keywords and formulas as a search query """

    def get_unique_terms(li):
        unique_set = set()
        res = []
        for x in li:
            if x.lower() not in unique_set:
                res.append(x)
                unique_set.add(x.lower())
        return res

    result_list = []

    if get_formula:
        query_formulas = get_query_formulas(question_content, filter_formula=filter_formula)

        if verbose:
            for field in ['Title', 'Question']:
                print("%s: " % field)
                print(','.join([formula_id + ": " + FormulaProcessor.extract_alttext(formula) for formula_id, formula in query_formulas[field]]))

        formula_list = [formula for formula_id, formula in query_formulas['Title'] + query_formulas['Question']]
        if formula_unique:
            formula_list = get_unique_terms(formula_list)

        result_list += formula_list

    if get_keyword:
        query_keywords = get_query_keywords(question_content, keyword_type=keyword_type)

        if verbose:
            for field in ['Title', 'Question', 'Tags']:

                print("%s: " % field)
                print(','.join(query_keywords[field]))

        keyword_list = query_keywords['Title'] + query_keywords['Question'] + query_keywords['Tags']
        if keyword_unique:
            keyword_list = get_unique_terms(keyword_list)

        result_list += keyword_list

    return result_list


def get_queries(query_method, question_content, **kwargs):
    if query_method == "rewrite":
        return get_query_list(question_content, **kwargs)  # equals filter_formula=True, keyword_type="MSEWiki"
