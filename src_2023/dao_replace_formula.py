"""
    Functions to process formulas and text that contains formulas
"""

from bs4 import BeautifulSoup
from dao import multiple_str_replace, clean_escape_html


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
