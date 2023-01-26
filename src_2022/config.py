import os
from utility.cache import CACHE as _CACHE

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.dirname(SRC_PATH)
EVAL_PATH = os.path.join(BASE_PATH, "eval")

DATA_PATH = os.path.join(BASE_PATH, "data")
STORAGE_DATA_PATH = DATA_PATH

### raw data
ARQM_DATA_PATH = os.path.join(DATA_PATH, "ARQMath")
STORAGE_ARQM_DATA_PATH = os.path.join(ARQM_DATA_PATH, "data-original")
WIKI_DATA_PATH = os.path.join(DATA_PATH, "Wikipedia")

ARQM_XML_PATH = os.path.join(STORAGE_ARQM_DATA_PATH, "Collections")
ARQM_FORMULAS_PATH = os.path.join(STORAGE_ARQM_DATA_PATH, "Formulas")
ARQM_THREADS_YEAR_PATH = os.path.join(STORAGE_ARQM_DATA_PATH, "Thread_Files", "Collection_By_Year")
ARQM_TASK1_PATH = os.path.join(STORAGE_ARQM_DATA_PATH, "Task1")
ARQM_TASK2_PATH = os.path.join(STORAGE_ARQM_DATA_PATH, "Task2")


### generated data
ARQM_PREPRO_PATH = os.path.join(ARQM_DATA_PATH, "prepro_2022")
ARQM_PREPRO_FILTERS_PATH = os.path.join(ARQM_DATA_PATH, "prepro_2021")


MAP_RAW_PATH = os.path.join(ARQM_PREPRO_PATH, "map_raw")
os.makedirs(MAP_RAW_PATH, exist_ok=True)
PKL_PATH = os.path.join(ARQM_PREPRO_PATH, "pkl")


LOG_PATH = os.path.join(SRC_PATH, "log")
os.makedirs(LOG_PATH, exist_ok=True)
ARQM_OUTPUT_HTML_FOLDER = os.path.join(ARQM_DATA_PATH, "html_minimal_2022")
ARQM_OUTPUT_HTML_MINIMAL_PATH = os.path.join(ARQM_OUTPUT_HTML_FOLDER, "2010-2018_local")
# ARQM_OUTPUT_FORMULAS_PATH = os.path.join(ARQM_OUTPUT_HTML_FOLDER, "formulas_2010-2018_local")
ARQM_FINAL_HTML_MINIMAL_PATH = os.path.join(ARQM_OUTPUT_HTML_FOLDER, "2010-2018_3patterns")

# ARQM_OUTPUT_QUESTION_FOLDER = os.path.join(ARQM_DATA_PATH, "html_question_2021")
# ARQM_OUTPUT_QUESTION_HTML_PATH = os.path.join(ARQM_OUTPUT_QUESTION_FOLDER, "2010-2018_local")


ARQM_EXPERIMENTS_PATH = os.path.join(ARQM_DATA_PATH, "experiments")


### Formula folders
FORMULA_FOLDER_CONFIG = {
    "latex": ("latex_representation_v3", range(1, 102)),
    "opt": ("opt_representation_v3", range(1, 102)),
    "slt": ("slt_representation_v3", range(1, 102)),
}

TASK_FORMULA_FOLDER_CONFIG = {
    2020: {
        "latex": os.path.join(ARQM_TASK1_PATH, "ARQMath_2020", "Topics", "Formula_topics_latex_V2.0.tsv"),
        "slt_original": os.path.join(ARQM_TASK1_PATH, "ARQMath_2020", "Topics", "Formula_topics_slt_V2.0.tsv"),
        "slt": os.path.join(ARQM_TASK1_PATH, "ARQMath_2021", "Topics", "Topics_2020_converted_Formula_slt_V2.0.tsv"),
    },
    2021: {
        "latex": os.path.join(ARQM_TASK1_PATH, "ARQMath_2021", "Formulas", "Topics_2021_Formulas_Latex_V1.1.tsv"),
        "slt": os.path.join(ARQM_TASK1_PATH, "ARQMath_2021", "Formulas", "Topics_2021_Formulas_SLT_V1.1.tsv"),
    },
    2022: {
        "latex": os.path.join(ARQM_TASK1_PATH, "ARQMath_2022", "Formulas", "Topics_Formulas_Latex.V0.1.tsv"),
        "slt": os.path.join(ARQM_TASK1_PATH, "ARQMath_2022", "Formulas", "Topics_Formulas_SLT.V0.1.tsv"),
    }
}


### for generating parser pkl

def CACHE(name):
    return _CACHE(name, dir_path=PKL_PATH)

RECORD_NUM = {
    'comment': None,
    'post_history': None,  # ignore by default
    'post_link': None,
    'post': None,
    'user': None,
    'badge': None,
    'vote': None,
}

COLLECTION_VERSION = "V1.3"
COMMENT_FILE_VERSION = "V1.0"

PARSER_PKL = {
    'comment': "comment_parser.%s.pkl" % COMMENT_FILE_VERSION,
    'post_history': "post_history_parser.%s.pkl" % COLLECTION_VERSION,  # ignore by default
    'post_link': "post_link_parser.%s.pkl" % COLLECTION_VERSION,
    'post': "post_parser.%s.pkl" % COLLECTION_VERSION,
    'user': "user_parser.%s.pkl" % COLLECTION_VERSION,
    'vote': "vote_parser.%s.pkl" % COLLECTION_VERSION,
}

DATA_VERSIONS = {
    'post': 'Posts.%s.xml' % COLLECTION_VERSION,
    'badge': 'Badges.%s.xml' % COLLECTION_VERSION,
    'comment': 'Comments.%s.xml' % COMMENT_FILE_VERSION,
    'vote': 'Votes.%s.xml' % COLLECTION_VERSION,
    'user': 'Users.%s.xml' % COLLECTION_VERSION,
    'post_link': 'PostLinks.%s.xml' % COLLECTION_VERSION,
    'post_history': 'PostHistory.%s.xml' % COLLECTION_VERSION,
    "tags": "Tags.%s.xml" % COLLECTION_VERSION,
}

DEFAULT_MAP_OF_COMMENTS_FILE = "map_of_comments_for_post.json"
REGENERATED_MAP_OF_COMMENTS_FILE = "map_of_comments_for_post_V1013_cleaned.json"

FINAL_MAP_OF_COMMENTS_FILE = REGENERATED_MAP_OF_COMMENTS_FILE
# FINAL_MAP_OF_COMMENTS_FILE = DEFAULT_MAP_OF_COMMENTS_FILE

FINAL_MAP_OF_COMMENTS_FOR_QUESTION = "map_of_comments_for_question_V1013_cleaned.json"
FINAL_MAP_OF_COMMENTS_FOR_JUST_ANSWER = "map_of_comments_for_just_answer_V1013_cleaned.json"
