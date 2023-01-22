"""
    Functions to process formulas and text that contains formulas

    Major classes:

    - FormulaProcessor:
        a collection of helper functions to process formulas

    - FormulaHTMLConvertor:
        help convert latex formulas in a html file to their Presentatino MathML representation
            using the Lab-provided formula representation tsv files

"""

from bs4 import BeautifulSoup
import re
import os
from utility.dao import multiple_str_replace, clean_escape_html, load_json
from dao_read_formula_tsv import read_formula_tsv
from config import ARQM_PREPRO_PATH


FORMULA_PATTERNS = [
    ('\$\$(.+?)\$\$', '\$\$.+?\$\$'),
    ('\$(.+?)\$', '\$.+?\$')
]

MATH_CONTAINER_PATTERNS = [
    # extract both formula id and the formula itself
    ('<span class="math-container" id="(.+?)">(.+?)</span>', '<span class="math-container" id=".+?">.+?</span>'),
]
VISUAL_CONTAINER_PATTERNS = [
    # extract both formula id and the formula itself
    ('<span class="math-container" id="(.+?)".+?visual_id="(.+?)">(.+?)</span>', '<span class="math-container" id=".+?".+?visual_id=".+?">.+?</span>'),
    # ('<span class="math-container" id="(.+?)".+?visual_id=\'(.+?)\'>(.+?)</span>', '<span class="math-container" id=".+?".+?visual_id=\'.+?\'>.+?</span>'),
]


ALTTEXT_PATTERN = '.+?alttext="(.+?)".+?'


class FormulaProcessor:
    """
        A family of functions that process formula / text contains formulas
    """
    @staticmethod
    def extract_formulas(text, patterns):
        """ use re.DOTALL to include "\n" in formula!
        """
        raw_text = r"{}".format(text)

        extracted_list = []
        for formula_pattern, whole_pattern in patterns:
            extracted_list += [
                (formula_text, whole_exp)
                for formula_text, whole_exp in zip(
                    re.findall(formula_pattern, raw_text, re.DOTALL), re.findall(whole_pattern, raw_text, re.DOTALL))
            ]
        return extracted_list

    @staticmethod
    def extract_alttext(math_container):
        """ use re.DOTALL to include "\n" in formula!
        """
        alttext = re.findall(ALTTEXT_PATTERN, r'{}'.format(math_container), re.DOTALL)
        if alttext:
            return alttext[0]
        return None

    @staticmethod
    def extract_visual_formulas(text):
        """ use re.DOTALL to include "\n" in formula!
        """
        raw_text = r"{}".format(text)

        extracted_list = []
        for formula_pattern, whole_pattern in VISUAL_CONTAINER_PATTERNS:
            extracted_list += [
            (formula_id, visual_id, formula_text, whole_exp)
                for (formula_id, visual_id, formula_text), whole_exp in zip(
                    re.findall(formula_pattern, raw_text, re.DOTALL), re.findall(whole_pattern, raw_text, re.DOTALL))
            ]
        return extracted_list

    @classmethod
    def remove_math_container(cls, text, wrap_chars="$"):
        replacement_dict = {}
        for pattern in MATH_CONTAINER_PATTERNS:
            for (str_formula_id, formula), math_container in cls.extract_formulas(text, [pattern]):
                replacement_dict[math_container] = wrap_chars + formula + wrap_chars
        if replacement_dict:
            text = multiple_str_replace(replacement_dict, text)
        return text


class FormulaHTMLConvertor:
    """
        This class helps convert latex formulas in a html file to their Presentatino MathML representation
            using the provided formula representation tsv files

        The convertor object stores the content of a formula representation tsv file one at a time,
            performs an lazy update of the content of the tsv file
            only when the target thread_id does not exist
    """

    def __init__(self, verbose=True):
        self.formula_types = ["latex", "slt"]
        self.formulaTSVs = {formula_type: {} for formula_type in self.formula_types}
        self.verbose = verbose

        self.thread2formulasTSV = load_json(
            os.path.join(ARQM_PREPRO_PATH, "thread2formulasTSV.json"),
            keys=[int], verbose=self.verbose)
        self.latex2slt_formulas = None
        self.thread_id = None

    def lazy_update(self, thread_id):
        update_formulaTSVs(
            thread_id,
            self.formula_types,
            self.formulaTSVs,
            self.thread2formulasTSV,
            groupby_list=["thread_id", "id"],
            verbose=self.verbose
        )
        self.latex2slt_formulas = create_formula_map(
            self.formulaTSVs["latex"].get(thread_id, {}), self.formulaTSVs["slt"].get(thread_id, {})
        )
        self.thread_id = thread_id
        return self.has_formula_convert_map()

    def has_formula_convert_map(self):
        return bool(self.latex2slt_formulas)

    def latex2slt(self, html, replace_by_RE=True, replace_by_bs4=True):
        if not self.has_formula_convert_map:
            raise ValueError(
                "No formula convert map is founded for this html file;"
                " either 'lazy_update' of the target thread-id has not been called"
                " or this html does not have any formulas to be converted!")
        return html_latex2slt(
            html, self.thread_id, self.formulaTSVs, self.latex2slt_formulas,
            replace_by_RE=replace_by_RE, replace_by_bs4=replace_by_bs4
        )


def create_formula_map(latex_post_map, slt_post_map):
    """
        latex_post_map, slt_post_map are dict {formual_id: [single formula item]}
        Return a map of {latex-formula: slt-formula-content}
    """
    d = {}
    for formula_id in sorted(latex_post_map):
        if formula_id not in slt_post_map:
            continue
        latex_content = latex_post_map[formula_id][0]
        slt_content = slt_post_map[formula_id][0]
        if not slt_content.get('formula'):  # Skip SLT Empty Formulas in V3
            continue
        if "formula" not in latex_content:  # Skip Latex Empty Formulas in V3
            continue
        d[latex_content["formula"]] = {
            k: v for k, v in latex_content.items()
            if k != "formula"
        }
        d[latex_content["formula"]].update({
            "formula": slt_content["formula"],
        })
    return d


def update_formulaTSVs(thread_id, formula_types, formulaTSVs, thread2formulasTSV,
                       groupby_list=None, verbose=True):
    """
        formulaTSVs is a placeholder dict of {formula_type: formula-tsv}
        This function do a lazy update of formulaTSVs,
            so that it stores the formula tsv content that contain all formula items with the specified thread_id

        Input:
            thread_id: the specified thread_id
            formula_types: e.g. ["slt", "latex"]
            formulaTSVs: the place holder dict
            thread2formulasTSV: the map of {thread_id: [list of formula_tsv names]}
            groupby_list: e.g. ["thread_id", "id"], arg for read_formula_tsv

        Return:
            True if the formulaTSVs has been updated for the given thread_id, otherwise False

    """
    if groupby_list is None:
        raise IOError("Indicate groupby_list! e.g. ['thread_id', 'id']")
    has_updated = {k: False for k in formula_types}
    for formula_type in formula_types:
        formulaTSV = formulaTSVs.get(formula_type, {})
        if thread_id not in formulaTSV:
            if thread_id in thread2formulasTSV and formula_type in thread2formulasTSV[thread_id]:
                tsv_names = thread2formulasTSV[thread_id][formula_type]
                formulaTSVs[formula_type] = read_formula_tsv(
                    formula_type, tsv_names, groupby_list=groupby_list)
                has_updated[formula_type] = True

    # thread_id might exists in only either one, e.g. thread_id = 1814 exists in latex only
    if all([thread_id in formulaTSVs.get(formula_type, {}) for formula_type in formula_types]):
        if any([has_updated[formula_type] for formula_type in formula_types]):
            if verbose:
                print("[Thread_id %d] formulaTSVs updated." % thread_id)
            return True
    return False


def html_latex2slt(html, thread_id, formulaTSVs, latex2slt_formulas,
                   replace_by_RE=True,
                   replace_by_bs4=True):
    """
        formulaTSVs should be in the format of:
        {
            "latex": {thread_id: formula_id: [list of formula-items]}
            "slt":   {thread_id: formula_id: [list of formula-items]}
        }, created by the update_formulaTSVs function

        latex2slt_formulas should be a map of {latex-formula: slt-formula-content}
            created by the create_formula_map function
    """
    def _build_replacement_dict(latex2slt_formulas, wrap_chars):
        replacement_dict, clean_replacement_dict = {}, {}
        for latex_formula, slt_content in latex2slt_formulas.items():
            clean_slt_formula = _clean_slt_formula(slt_content["formula"], slt_content)

            replacement_dict[wrap_chars + latex_formula + wrap_chars] = clean_slt_formula
            clean_formula = clean_escape_html(latex_formula)
            if clean_formula != latex_formula:
                clean_replacement_dict[wrap_chars + clean_formula + wrap_chars] = clean_slt_formula
        return replacement_dict, clean_replacement_dict

    def _clean_math_container_string(text):
        # special case for 1_2453.html, formula_id = 11
        return text.strip("$").replace(r"\{", "{").replace(r"\}", "}")

    def _clean_slt_formula(slt_formula, slt_content):
        if "visual_id" in slt_content:
            replace_text = '<span class="math-container" id="%s" visual_id=%s>%s</span>' % (
                slt_content["id"], slt_content["visual_id"], slt_content["formula"]
            )
        else:
            replace_text = '<span class="math-container" id="%s">%s</span>' % (
                slt_content["id"], slt_content["formula"]
            )
        return replace_text

    def _check_formula_twice(original_formula, source):
        clean_formula = clean_escape_html(original_formula)
        if original_formula in source:
            return original_formula
        if clean_formula in source:
            return clean_formula
        return None

    def _update_math_container(slt_content, math_container):
        if not slt_content.get("formula"):  # Skip SLT Empty Formulas in V3
            return
        if "visual_id" in slt_content:
            math_container["visual_id"] = slt_content["visual_id"]
        math_container.string = ""
        math_container.append(BeautifulSoup(slt_content["formula"], "html.parser"))

    if thread_id not in formulaTSVs["slt"] or thread_id not in formulaTSVs["latex"]:
        return html

    text = html

    if replace_by_RE:
        for wrap_chars in ("$$", "$"):
            replacement_dict, clean_replacement_dict = _build_replacement_dict(latex2slt_formulas, wrap_chars)
            text = multiple_str_replace(replacement_dict, text)
            if clean_replacement_dict:
                # map after the original --
                # since these SLTs might be malfunctioned (these latex formula can be cleaned = has html escaping characters)
                text = multiple_str_replace(clean_replacement_dict, text)

    if replace_by_bs4:
        soup = BeautifulSoup(text, "html.parser")

        for math_container in soup.find_all("span", {"class": "math-container"}):
            if math_container.has_attr("id") and not math_container.has_attr("visual_id"):
                try:
                    formula_id = int(math_container["id"])
                except ValueError:
                    formula_id = math_container["id"]
                if formula_id not in formulaTSVs["slt"][thread_id]:
                    continue
                slt_content = formulaTSVs["slt"][thread_id][formula_id][0]
                _update_math_container(slt_content, math_container)
            elif not math_container.has_attr("id") and math_container.string is not None:  # e.g. /1_2010/3758_09/4467/4467_4585.html: FIXME
                clean_string = _clean_math_container_string(math_container.string)
                matched_string = _check_formula_twice(clean_string, latex2slt_formulas)
                if matched_string is not None:
                    slt_content = latex2slt_formulas[matched_string]
                    math_container["id"] = slt_content["id"]
                    _update_math_container(slt_content, math_container)

        text = str(soup)

    return text

def html_escape(text):
    return str(BeautifulSoup(text, "html.parser"))
