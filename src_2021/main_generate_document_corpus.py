"""
    The main file to genereate the document corpus (html pages that are to be indexed by the search engine).
        All formulas in each html page is converted to  their Presentation MathML format (by default)

        Two style of html pages can be generated:
            - [thread] Each html page is a thread, with a single question and all its answers)
            - [minimal] Each html page is a question-answer pair with enriched details

        The [minimal] style is used for the MathDowsers' submissions.


    Prerequisite:
         Original thread HTML files has been downloaded at <ARQM_THREADS_YEAR_PATH>.

         To run style [thread],
            "html_minifest.txt" at the prepro folder is required (see prepro_00_create_html_manifest.py)
         To run style [minimal],
            all prepro files are required to run beforehand (see main_preprocessing.sh)

    Examples:

        Create demo pages for style [thread]:
            $ python main_generate_docment_corpus.py --style thread

        Create demo pages for style [minimal]:
            $ python main_generate_docment_corpus.py  --style minimal

        Create pages for year 2010 and 2011:
            $ python main_generate_docment_corpus.py  --style <style> --year 2010,2011

        Create pages for all available years:
            $ python main_generate_docment_corpus.py  --style <style> --year all

        Create pages for selected thread ids 1 & 5:
            $ python main_generate_docment_corpus.py  --style <style> --thread_id 1,5"

        Specify output folder other than the default path:
            add "--output_folder <path of output_folder>"

        Keep latex formulas instead of converting to Presentation MathML:
            add "--keep_latex"

        See all options:
            $ python main_generate_docment_corpus.py  -h
"""

from config import (
    ARQM_PREPRO_PATH, MAP_RAW_PATH, ARQM_OUTPUT_HTML_FOLDER, ARQM_DATA_PATH,
    ARQM_OUTPUT_HTML_MINIMAL_PATH, ARQM_THREADS_YEAR_PATH,
    FINAL_MAP_OF_COMMENTS_FOR_QUESTION, FINAL_MAP_OF_COMMENTS_FOR_JUST_ANSWER
)
from utility.dao import load_json, get_recursive_paths
from utility.datetime_util import str2dt

from preload import DATE2FOLDER_MAP
from dao_replace_formula import (
    FormulaProcessor, FormulaHTMLConvertor
)
import os
from tqdm import tqdm


VERBOSE = False
MINIMAL_HTML = "template_minimal_v2.html"


def read_html(html_template):
    file = open(html_template)
    line = file.readline()
    content = ""
    while line:
        content += line
        line = file.readline()
    return content


class HTMLThreadCreator:
    def __init__(self, source_folder=ARQM_THREADS_YEAR_PATH, keep_latex=False, verbose=True):
        if not os.path.exists(source_folder):
            raise IOError("The source folder for html conversion %s is missing!" % source_folder)
        self.source_folder = source_folder
        self.verbose = verbose
        self.formula_convertor = FormulaHTMLConvertor(verbose=verbose)
        self.keep_latex = keep_latex

    def convert_thread_html(self, thread_id, html_path):
        """
            Given the Lab-provided thread html (in html path),
                convert latex formulas into their Presentation MathMl using the formula representation tsvs

            Note:
                Since the original THREAD file contains malfunctioned math-container,
                    using BeautifulSoup to read the html **might** ruin the file
                (might need to use only RE to extract formula patterns)
        """
        def _clean_html(text):
            # fix malfunctioned math-container
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

        original_thread_html = read_html(html_path)
        html = _clean_html(original_thread_html)
        html = _remove_arqmath_header(html)
        if self.keep_latex:
            return html

        html = _remove_mathjax(html)
        html = _replace_TexAMS(html)
        latex_title = _get_title_string(html)

        self.formula_convertor.lazy_update(thread_id)
        if self.formula_convertor.has_formula_convert_map():
            new_html = self.formula_convertor.latex2slt(html)
            # new_html = self.formula_convertor.latex2slt(html, replace_by_bs4=False)  # seems fixed
        else:
            new_html = html

        new_html = new_html.replace(_get_title_string(new_html), latex_title)
        return new_html

    def generate_htmls_by_year(
            self,
            year,
            output_folder,
            create_html_func="convert_thread_html"):
        """
            Only convert the formulas given the thread htmls from the source folder
        """
        os.makedirs(output_folder, exist_ok=True)

        print("[create_year_thread_collections] Start:")
        print("Year", year)

        for month, folder_suffix in sorted(DATE2FOLDER_MAP[year].items()):
            print("Month", month)

            year_folder = output_folder + folder_suffix.rpartition("/")[0]
            os.makedirs(year_folder, exist_ok=True)
            month_folder = output_folder + folder_suffix
            os.makedirs(month_folder, exist_ok=True)

            html_paths = get_recursive_paths(
                self.source_folder + folder_suffix, extension=".html")

            for html_path in tqdm(sorted(html_paths)):
                thread_id = int(html_path.rpartition("/")[2].partition(".")[0])
                new_html = getattr(self, create_html_func)(thread_id, html_path)
                output_path = os.path.join(month_folder, "%d.html" % thread_id)
                with open(output_path, "w") as f:
                    f.write(new_html)

    def generate_htmls(
            self,
            selected_thread_ids,
            output_folder,
            create_html_func="convert_thread_html"):
        from preload import html_folder_lookup
        os.makedirs(output_folder, exist_ok=True)

        for thread_id in tqdm(sorted([int(x) for x in selected_thread_ids])):
            html_path = html_folder_lookup(thread_id, directory=self.source_folder, is_folder=False)
            if html_path is None:
                raise ValueError("thread_id %d not found in the source folder %s!" % (thread_id, self.source_folder))

            new_html = getattr(self, create_html_func)(thread_id, html_path)
            output_path = os.path.join(output_folder, "%d.html" % thread_id)
            with open(output_path, "w") as f:
                f.write(new_html)


class HTMLMinimalCreator:

    def __init__(self, keep_latex=False, verbose=True):
        self.verbose = verbose

        self.creation_year_map = load_json(
            os.path.join(MAP_RAW_PATH, "creation_year_map.json"), keys=[int], verbose=verbose
        )
        self.creation_year_map = {k: set(v) for k, v in self.creation_year_map.items()}

        self.thread2formulasTSV = load_json(
            os.path.join(ARQM_PREPRO_PATH, "thread2formulasTSV.json"), keys=[int], verbose=verbose
        )
        self.map_of_comments_for_question = load_json(
            os.path.join(MAP_RAW_PATH, FINAL_MAP_OF_COMMENTS_FOR_QUESTION), keys=[int], verbose=verbose
        )
        self.map_of_comments_for_just_answer = load_json(
            os.path.join(MAP_RAW_PATH, FINAL_MAP_OF_COMMENTS_FOR_JUST_ANSWER), keys=[int], verbose=verbose
        )
        self.related_post_bimap = load_json(
            os.path.join(ARQM_PREPRO_PATH, "related_post_bimap.json"), keys=[int], verbose=verbose
        )
        self.duplicate_post_bimap = load_json(
            os.path.join(ARQM_PREPRO_PATH, "duplicate_post_bimap.json"), keys=[int], verbose=verbose
        )
        if keep_latex:
            self.question2title = load_json(
                os.path.join(ARQM_PREPRO_PATH, "question2title.json"), keys=[int], verbose=verbose
            )
        else:
            self.question2title = load_json(
                os.path.join(ARQM_PREPRO_PATH, "question2title_latex2slt.json"), keys=[int], verbose=verbose
            )

        self.transform_functions = {
            'latex_title': lambda title: FormulaProcessor.remove_math_container(title),

            'title': lambda title: title,

            'body': lambda body: body,

            'tags': lambda tags:
                ''.join(['<span> %s </span>' % tag for tag in tags]),

            'qcomments': lambda qcomments:
                ''.join(['<tr><td comment_id="%d"> %s </td></tr>' % (
                    c['id'], c['text']) for c in qcomments]),

            'duplicate_posts': lambda duplicate_posts:
                ''.join(['<tr><td post_id="%d"> %s </td></tr>' % (
                    post_id, self.question2title[post_id])
                    for post_id in sorted(duplicate_posts)]),

            'related_posts': lambda related_posts:
                ''.join(['<tr><td post_id="%d"> %s </td></tr>' % (
                    post_id, self.question2title[post_id])
                    for post_id in sorted(related_posts)]),

            'answer': lambda answer: answer['body'],
            'acomments': lambda answer:
                ''.join(['<tr><td comment_id="%d"> %s </td></tr>' % (
                    c['id'], c['text'])
                    for c in answer['acomments']]),
        }

        self.map_questions = {}
        self.map_answers = {}
        self.formula_convertor = FormulaHTMLConvertor(verbose=verbose)
        self.keep_latex = keep_latex

    def lazy_update(self, thread_id=None, map_questions=None, map_answers=None):
        if map_questions is not None:
            self.map_questions = map_questions
        if map_answers is not None:
            self.map_answers = map_answers

        if thread_id is not None:
            if thread_id not in self.map_questions:
                for year, set_thread_ids in self.creation_year_map.items():
                    if thread_id in set_thread_ids:
                        self.map_questions = load_json(
                            os.path.join(MAP_RAW_PATH, "map_questions_by_year", "map_questions_%d.json" % year),
                            keys=[int]
                        )
                        self.map_answers = load_json(
                            os.path.join(MAP_RAW_PATH, "map_answers_by_year", "map_answers_%d.json" % year),
                            keys=[int]
                        )
                        if self.verbose:
                            print("[Thread_id %d] map_questions and map_answers updated to year %d." % (thread_id, year))
                        break
            if thread_id not in self.map_questions:
                raise ValueError("Thread %d is not found among questions!" % thread_id)

    def create_html_minimal(
            self,
            thread_id,
            html_template=MINIMAL_HTML):

        def _get_question_answers_content():
            question_content = self.map_questions[thread_id]
            question_content.update({
                'latex_title': question_content['title'],
                "qcomments": self.map_of_comments_for_question.get(thread_id, []),
                "duplicate_posts": self.duplicate_post_bimap.get(thread_id, []),
                "related_posts": [x for x in self.related_post_bimap.get(thread_id, [])
                                  if x not in self.duplicate_post_bimap.get(thread_id, [])],
            })
            answers_content = self.map_answers[thread_id]
            for answer in answers_content:
                answer["acomments"] = self.map_of_comments_for_just_answer.get(answer["post_id"], [])
            return question_content, answers_content

        self.lazy_update(thread_id=thread_id)
        self.formula_convertor.lazy_update(thread_id)
        question_content, answers_content = _get_question_answers_content()

        html = read_html(html_template)
        for q_field in ('title', 'body', 'tags', 'qcomments',
                        'duplicate_posts', 'related_posts'):
            html = html.replace(
                "#%s#" % q_field.upper(),
                self.transform_functions[q_field](question_content[q_field])
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
                        self.transform_functions[a_field](answer))

                if not self.keep_latex and self.formula_convertor.has_formula_convert_map():
                    new_html = self.formula_convertor.latex2slt(new_html)

                new_html = new_html.replace(
                    "#LATEX_TITLE#",
                    self.transform_functions["latex_title"](question_content['latex_title'])
                )
                yield answer['post_id'], new_html

            except Exception as e:
                print("[ERROR] Thread_id: %d, Answer_id: %d" % (thread_id, answer['post_id']))
                raise Exception(e)

    def generate_htmls_by_year(
            self,
            year,
            output_folder=ARQM_OUTPUT_HTML_MINIMAL_PATH,
            create_html_func="create_html_minimal",
            selected_thread_ids=None):

        def _generate_html_path(thread_id, answer_id, creation_date):
            folder_path = DATE2FOLDER_MAP[creation_date.year][creation_date.month]
            html_folder = os.path.join(output_folder + folder_path, str(thread_id))
            os.makedirs(html_folder, exist_ok=True)
            return os.path.join(html_folder, "%s_%s.html" % (thread_id, answer_id))

        def _generate_selected_path(thread_id, answer_id):
            html_folder = os.path.join(output_folder + "/../selected", str(thread_id))
            os.makedirs(html_folder, exist_ok=True)
            return os.path.join(html_folder, "%s_%s.html" % (thread_id, answer_id))

        os.makedirs(output_folder, exist_ok=True)
        print("[create_year_htmls] Start:")
        if selected_thread_ids is not None:
            print("== Selected Thread Ids: ", len(selected_thread_ids))

        print("Year", year)
        map_questions = load_json(
            os.path.join(MAP_RAW_PATH, "map_questions_by_year", "map_questions_%d.json" % year),
            keys=[int]
        )
        map_answers = load_json(
            os.path.join(MAP_RAW_PATH, "map_answers_by_year", "map_answers_%d.json" % year),
            keys=[int]
        )
        self.lazy_update(map_questions=map_questions, map_answers=map_answers)

        for thread_id in tqdm(sorted(map_questions.keys())):
            if thread_id not in map_answers:
                continue
            if selected_thread_ids is not None and thread_id not in selected_thread_ids:
                continue

            for answer_id, new_html in getattr(self, create_html_func)(thread_id):
                if selected_thread_ids is not None:
                    output_path = _generate_selected_path(thread_id, answer_id)
                else:
                    output_path = _generate_html_path(
                        thread_id, answer_id, str2dt(map_questions[thread_id]['creation_date']))
                with open(output_path, "w") as f:
                        f.write(new_html)

    def generate_htmls(
            self,
            selected_thread_ids,
            output_folder=ARQM_OUTPUT_HTML_FOLDER + "/selected",
            create_html_func="create_html_minimal"):

        def _generate_html_path(thread_id, answer_id):
            html_folder = os.path.join(output_folder, str(thread_id))
            os.makedirs(html_folder, exist_ok=True)
            return os.path.join(html_folder, "%s_%s.html" % (thread_id, answer_id))

        for thread_id in tqdm(sorted([int(x) for x in selected_thread_ids])):
            self.lazy_update(thread_id=thread_id)
            for answer_id, new_html in getattr(self, create_html_func)(thread_id):
                output_path = _generate_html_path(thread_id, answer_id)
                with open(output_path, "w") as f:
                    f.write(new_html)


if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser(description="Generate HTMLs for indexing.")
    argparser.add_argument(
        "--style", choices=["minimal", "thread"],
        help="The style of the generated html page, 'minimal' for quesiton-answer pair, 'thread' for the whole thread"
    )
    argparser.add_argument(
        "--output_folder", default=None,
        help="(Optional) The path of the output folder (where the htmls will be generated). Default paths will be used if not supplied."
    )
    argparser.add_argument(
        "--year", default=None,
        help="Generate the htmls by their creation year. The years should be a list separated by commas, e.g. [2010,2011]. Default is None (creating demo pages instead)."
    )
    argparser.add_argument(
        "--thread_id", default=None,
        help="Generate the htmls by their thread id. The thread_ids should be a list separated by commas, e.g. [1,2]. Default is None (creating demo pages instead)."
    )
    argparser.add_argument(
        "--keep_latex", action="store_true",
        help="Do not convert latex formulas to their Presentation MathML format."
    )

    args = argparser.parse_args()

    if args.style == "minimal":
        html_creator = HTMLMinimalCreator(keep_latex=args.keep_latex, verbose=VERBOSE)
        if args.output_folder is None:
            if args.year:
                output_folder = ARQM_OUTPUT_HTML_MINIMAL_PATH
            elif args.thread_id:
                output_folder = ARQM_OUTPUT_HTML_FOLDER + "/selected"
            else:
                output_folder = ARQM_OUTPUT_HTML_FOLDER
        else:
            output_folder = args.output_folder
    elif args.style == "thread":
        html_creator = HTMLThreadCreator(keep_latex=args.keep_latex, verbose=VERBOSE)
        if args.output_folder is None:
            if args.year:
                output_folder = os.path.join(ARQM_DATA_PATH, "html_thread_2021", "2010-2018_local")
            elif args.thread_id:
                output_folder = os.path.join(ARQM_DATA_PATH, "html_thread_2021", "selected")
            else:
                output_folder = os.path.join(ARQM_DATA_PATH, "html_thread_2021")
        else:
            output_folder = args.output_folder

    print("Succesfully load HTML creator for style [%s] (keep_latex=%s)" % (args.style, str(args.keep_latex)))
    print("Output Folder: %s" % output_folder)

    if args.year:
        if args.year == "all":
            years = range(2010, 2019)
        else:
            try:
                years = sorted([int(y) for y in args.year.split(",")])
                for year in years:
                    if year not in range(2010, 2019):
                        raise ValueError("Year %d is invalid (can only in range 2010-2018)! " % year)

            except Exception as e:
                raise IOError("Invalid input: year can only be in the range from 2010 to 2018!")

        for year in years:
            html_creator.generate_htmls_by_year(year, output_folder=output_folder)

    elif args.thread_id:
        thread_ids = sorted([int(tid) for tid in args.thread_id.split(",")])
        html_creator.generate_htmls(thread_ids, output_folder=output_folder)
    else:
        print("Generating demo html pages for the style [%s] (keep_latex=%s)..." % (args.style, str(args.keep_latex)))
        demo_ids = [5]
        try:
            demo_folder = output_folder + "/demo"
            html_creator.generate_htmls(
                demo_ids,
                output_folder=demo_folder
            )
            print("Demo pages successfully created at %s." % demo_folder)
        except Exception as e:
            print("[ERROR] Cannot create demo pages: %s" % e)
