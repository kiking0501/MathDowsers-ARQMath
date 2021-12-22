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
from config import ARQM_EXPERIMENTS_PATH


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

HUMAN_TRANSLATED = load_json(
    os.path.join(ARQM_EXPERIMENTS_PATH, "topics", "ARQMath_2021", "task1-2020-human_translated.json"))


def get_human_translated_2020(topic_id, **kwargs):
    return HUMAN_TRANSLATED[topic_id]


def get_human_translated_2020_break(topic_id, **kwargs):
    result_list = []
    for query in HUMAN_TRANSLATED[topic_id]:
        if query.startswith("<math"):
            result_list.append(query)
        else:
            result_list.extend([x for x in query.split(" ") if x])
    return result_list


def get_single_formula(question_content, **kwargs):
    return [remove_xml_syntax(question_content["Query_Formula"])]


def get_formula_store_visual(
        question_content,
        topF=10,
        year=2020,
        formula_unique=False,
        keyword_unique=False,
        get_formula=True,
        get_keyword=True,
        **kwargs):

    """ For Holistic Formula Search """
    from main_search_dict2tsv import REF_FOLDER, RANK_REF

    def create_pseudo_math_container(visual_id, score, formula_id):
        return '<span visual_id="%s" formula_similarity="%.3f" class="math-container">%s</span>' % (
            visual_id, score, formula_id)

    def get_unique_terms(li):
        unique_set = set()
        res = []
        for x in li:
            if x.lower() not in unique_set:
                res.append(x)
                unique_set.add(x.lower())
        return res

    result_list = []

    if get_keyword:
        query_keywords = get_query_keywords(question_content)
        keyword_list = query_keywords['Title'] + query_keywords['Question'] + query_keywords['Tags']
        if keyword_unique:
            keyword_list = get_unique_terms(keyword_list)
        result_list += keyword_list

    if get_formula:
        query_formulas = get_query_formulas(question_content)
        visual_score_map = load_json(
            os.path.join(REF_FOLDER, RANK_REF["visual_map"]["formula_as_topic_%s" % year]))

        formula_list = []
        for formula_id, formula in query_formulas["Title"] + query_formulas["Question"]:
            if formula_id not in visual_score_map:  # some formulas cannot be queried, e.g. q_969
                continue
            visual_id_pairs = sorted(visual_score_map[formula_id].items(), key=lambda x: (-x[1], x[0]))[:topF]
            formula_list += [
                create_pseudo_math_container(visual_id, score, formula_id)
                for visual_id, score in visual_id_pairs
            ]
        if formula_unique:
            formula_list = get_unique_terms(formula_list)
        result_list += formula_list

    return result_list


def get_queries(query_method, question_content, **kwargs):
    #######################
    #### ARQMath 2021

    if query_method == "rewrite":
        return get_query_list(question_content, **kwargs)  # equals filter_formula=True, keyword_type="MSEWiki"

    elif query_method == "human_translated_2020":
        return get_human_translated_2020(kwargs["topic_id"])

    elif query_method == "unique":
        return get_query_list(question_content, keyword_unique=True, **kwargs)

    elif query_method == "single_formula":
        return get_single_formula(question_content, **kwargs)

    elif query_method == "formula_as_topic":
        return get_query_list(question_content, formula_unique=True, get_keyword=False, **kwargs)

    elif query_method == "formula_store_visual":
        return get_formula_store_visual(
            question_content, keyword_unique=True, formula_unique=True, topF=kwargs["formula_store_visual"], **kwargs)

    elif query_method == "keywords_only":
        return get_query_list(question_content, keyword_unique=True, get_formula=False, **kwargs)

    #######################
    #### Study
    elif query_method == "plain":
        return get_query_list(
            question_content, filter_formula=False, keyword_type="plain"
        )

    elif query_method == "ff":
        return get_query_list(
            question_content, keyword_type="plain"
        )

    elif query_method == "remove_stopword":
        return get_query_list(
            question_content, filter_formula=False, keyword_type="remove_stopword"
        )

    elif query_method == "remove_stopword_ff":
        return get_query_list(
            question_content, keyword_type="remove_stopword"
        )

    elif query_method == "MSE":
        return get_query_list(
            question_content, filter_formula=False, keyword_type="MSE"
        )
    elif query_method == "Wiki":
        return get_query_list(
            question_content, filter_formula=False, keyword_type="Wiki"
        )
    elif query_method == "MSEWiki":
        return get_query_list(
            question_content, filter_formula=False, keyword_type="MSEWiki"
        )

    elif query_method == "MSE_ff":
        return get_query_list(
            question_content, keyword_type="MSE"
        )
    elif query_method == "Wiki_ff":
        return get_query_list(
            question_content, keyword_type="Wiki"
        )

    elif query_method == "human_translated_2020_break":
        return get_human_translated_2020_break(kwargs["topic_id"])
