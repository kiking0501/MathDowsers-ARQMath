from config import (
    ARQM_PREPRO_PATH, MAP_RAW_PATH, ARQM_OUTPUT_HTML_FOLDER
    ARQM_OUTPUT_HTML_MINIMAL_PATH, ARQM_THREADS_YEAR_PATH
)
from utility.dao import load_json, get_recursive_paths
from utility.datetime_util import str2dt

from preload import DATE2FOLDER_MAP
from dao_replace_formula import (
    FormulaProcessor, FormulaHTMLConverter
)
import os
from tqdm import tqdm

###### PRELOAD ######
VERBOSE = True

thread2formulasTSV = load_json(
    os.path.join(ARQM_PREPRO_PATH, "thread2formulasTSV.json"), keys=[int], verbose=VERBOSE
)
map_of_comments_for_question = load_json(
    os.path.join(MAP_RAW_PATH, "map_of_comments_for_question.json"), keys=[int], verbose=VERBOSE
)
map_of_comments_for_just_answer = load_json(
    os.path.join(MAP_RAW_PATH, "map_of_comments_for_just_answer.json"), keys=[int], verbose=VERBOSE
)
related_post_bimap = load_json(
    os.path.join(ARQM_PREPRO_PATH, "related_post_bimap.json"), keys=[int], verbose=VERBOSE
)
duplicate_post_bimap = load_json(
    os.path.join(ARQM_PREPRO_PATH, "duplicate_post_bimap.json"), keys=[int], verbose=VERBOSE
)
question2title_latex2slt = load_json(
    os.path.join(ARQM_PREPRO_PATH, "question2title_latex2slt.json"), keys=[int], verbose=VERBOSE
)

#####################
TRANSFORM_FUNCTIONS = {
    'latex_title': lambda title: FormulaProcessor.remove_math_container(title),

    'title': lambda title: title,

    'body': lambda body: body,

    'tags': lambda tags:
        ''.join(['<span> %s </span>' % tag for tag in tags]),

    'qcomments': lambda qcomments:
        ''.join(['<tr><td comment_id="%d"> %s </td></tr>' % (c['id'], c['text']) for c in qcomments]),

    'duplicate_posts': lambda duplicate_posts:
        ''.join(['<tr><td post_id="%d"> %s </td></tr>' % (post_id, question2title_latex2slt[post_id])
                 for post_id in duplicate_posts]),

    'related_posts': lambda related_posts:
        ''.join(['<tr><td post_id="%d"> %s </td></tr>' % (post_id, question2title_latex2slt[post_id])
                 for post_id in related_posts]),

    'answer': lambda answer: answer['body'],
    'acomments': lambda answer:
        ''.join(['<tr><td comment_id="%d"> %s </td></tr>' % (c['id'], c['text']) for c in answer['acomments']]),
}


def read_html(html_template):
    file = open(html_template)
    line = file.readline()
    content = ""
    while line:
        content += line
        line = file.readline()
    return content


def create_html_minimal(
        thread_id,
        question_content,
        answers_content,
        formula_convertor,
        transform_functions=TRANSFORM_FUNCTIONS,
        html_template="template_html_minimal.html"):

    formula_convertor.update_with_thread_id(thread_id)

    html = read_html(html_template)
    for q_field in ('title', 'body', 'tags', 'qcomments',
                    'duplicate_posts', 'related_posts'):
        html = html.replace(
            "#%s#" % q_field.upper(),
            transform_functions[q_field](question_content[q_field])
        )
    html = html.replace("#QID#", str(thread_id))

    for answer in answers_content:
        try:
            new_html = html
            new_html = new_html.replace(
                "#AID#", str(answer['post_id'])
            )
            for a_field in ('answer', 'acomments'):
                new_html = new_html.replace(
                    "#%s#" % a_field.upper(),
                    transform_functions[a_field](answer))

            if formula_convertor.has_formula_convert_map():
                new_html = formula_convertor.latex2slt(new_html)

            new_html = new_html.replace(
                "#LATEX_TITLE#",
                transform_functions["latex_title"](question_content['latex_title'])
            )
            yield answer['post_id'], new_html

        except Exception as e:
            print("[ERROR] Thread_id: %d, Answer_id: %d" % (thread_id, answer['post_id']))
            raise Exception(e)


def generate_year_thread_collections(
        year,
        output_folder,
        source_folder=ARQM_THREADS_YEAR_PATH):
    """
        Only convert the formulas given the htmls from the source folder
    """
    from preload import get_date2folder_map

    def create_html(original_html, thread_id, formula_convertor):
        """
            The original THREAD file contains malfunctioned math-container
            use BeautifulSoup will ruin the file
            only use RE to extract patterns
        """
        def _clean_html(text):
            text = text.replace("span\"", "span")
            return text

        def _get_title_string(text):
            start = "<title>"
            end = "</title>"
            return start + text.partition(start)[2].partition(end)[0] + end

        def _remove_arqmath_header(text):
            start = "<header class=\"site-header\">"
            end = "</header>"
            return text.partition(start)[0] + text.partition(end)[2]

        def _remove_mathjax(text):
            start = '<script type="text/x-mathjax-config">'
            end = "</script>"
            return text.partition(start)[0] + text.partition(end)[2]

        def _replace_TexAMS(text):
            ori = '<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS_HTML-full"></script>'
            new = '<script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_SVG.js"> </script>'
            return text.replace(ori, new)

        html = _clean_html(original_html)
        html = _remove_arqmath_header(html)
        html = _remove_mathjax(html)
        html = _replace_TexAMS(html)
        latex_title = _get_title_string(html)

        formula_convertor.update_with_thread_id(thread_id)
        if formula_convertor.has_formula_convert_map():
            new_html = formula_convertor.latex2slt(html)

        new_html = new_html.replace(_get_title_string(new_html), latex_title)
        return new_html

    date2folder_map = get_date2folder_map()

    print("[create_year_thread_collections] Start:")
    print("Year", year)

    formula_convertor = FormulaHTMLConverter(verbose=VERBOSE)
    for month, folder_suffix in sorted(date2folder_map[year].items()):
        print("Month", month)

        year_folder = output_folder + folder_suffix.rpartition("/")[0]
        os.makedirs(year_folder, exist_ok=True)
        month_folder = output_folder + folder_suffix
        os.makedirs(month_folder, exist_ok=True)

        html_paths = get_recursive_paths(
            source_folder + folder_suffix, extension=".html")

        for html_path in tqdm(sorted(html_paths)):
            html = read_html(html_path)
            thread_id = int(html_path.rpartition("/")[2].partition(".")[0])
            try:
                new_html = create_html(html, thread_id, formula_convertor)
            except Exception as e:
                print(thread_id, e)
                break

            output_path = os.path.join(month_folder, "%d.html" % thread_id)
            with open(output_path, "w") as f:
                f.write(new_html)


def generate_year_htmls(
        year,
        create_html_func=create_html_minimal,
        output_folder=ARQM_OUTPUT_HTML_MINIMAL_PATH,
        filter_thread_ids=None):

    def _generate_html_path(answer_id, creation_date):
        folder_path = DATE2FOLDER_MAP[creation_date.year][creation_date.month]
        html_folder = os.path.join(output_folder + folder_path, str(thread_id))
        os.makedirs(html_folder, exist_ok=True)
        return os.path.join(html_folder, "%s_%s.html" % (thread_id, answer_id))

    print("[create_year_htmls] Start:")

    if filter_thread_ids is not None:
        print("== Filtered Thread Ids: ", len(filter_thread_ids))

    print("Year", year)

    map_questions = load_json(
        os.path.join(MAP_RAW_PATH, "map_questions_by_year", "map_questions_%d.json" % year),
        keys=[int]
    )
    map_answers = load_json(
        os.path.join(MAP_RAW_PATH, "map_answers_by_year", "map_answers_%d.json" % year),
        keys=[int]
    )

    formula_convertor = FormulaHTMLConverter(verbose=VERBOSE)
    for thread_id in tqdm(sorted(map_questions.keys())):
        if thread_id not in map_answers:
            continue
        if filter_thread_ids is not None and thread_id not in filter_thread_ids:
            continue

        question_content = map_questions[thread_id]
        question_content.update({
            'latex_title': question_content['title'],
            "qcomments": map_of_comments_for_question.get(thread_id, []),
            "duplicate_posts": duplicate_post_bimap.get(thread_id, []),
            "related_posts": [x for x in related_post_bimap.get(thread_id, [])
                              if x not in duplicate_post_bimap.get(thread_id, [])],
        })
        answers_content = map_answers[thread_id]
        for answer in answers_content:
            answer["acomments"] = map_of_comments_for_just_answer.get(answer["post_id"], [])

        for answer_id, new_html in create_html_func(
            thread_id,
            question_content,
            answers_content,
            formula_convertor
        ):
            output_path = _generate_html_path(
                answer_id, str2dt(question_content['creation_date']))
            with open(output_path, "w") as f:
                    f.write(new_html)
            if filter_thread_ids is not None:
                filter_folder = output_folder + "/../filtered"
                with open(os.path.join(filter_folder, "%s_%s.html" % (thread_id, answer_id)), "w") as f:
                    f.write(new_html)


if __name__ == '__main__':
    os.makedirs(ARQM_OUTPUT_HTML_FOLDER, exist_ok=True)
    for year in range(2010, 2019):
        generate_year_htmls(
            year,
            output_folder=ARQM_OUTPUT_HTML_MINIMAL_PATH
        )
