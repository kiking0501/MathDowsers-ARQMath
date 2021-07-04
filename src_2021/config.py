import os
from utility.cache import CACHE as _CACHE

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.dirname(SRC_PATH)
DATA_PATH = os.path.join(BASE_PATH, "data")
EVAL_PATH = os.path.join(BASE_PATH, "eval")

### raw data
ARQM_DATA_PATH = os.path.join(DATA_PATH, "ARQMath")
WIKI_DATA_PATH = os.path.join(DATA_PATH, "Wikipedia")

ARQM_XML_PATH = os.path.join(ARQM_DATA_PATH, "Collections")
ARQM_FORMULAS_PATH = os.path.join(ARQM_DATA_PATH, "Formulas")


### generated data
ARQM_PREPRO_PATH = os.path.join(ARQM_DATA_PATH, "prepro_2021")
ARQM_EXPERIMENTS_PATH = os.path.join(ARQM_DATA_PATH, "experiments")


### for generating parser pkl

def CACHE(name):
    return _CACHE(name, dir_path=ARQM_PREPRO_PATH)

RECORD_NUM = {
    'comment': None,
    'post_history': None,  # ignore by default
    'post_link': None,
    'post': None,
    'user': None,
    'badge': None,
    'vote': None,
}

COLLECTION_VERSION = "V1.2"

PARSER_PKL = {
    'comment': os.path.join(ARQM_PREPRO_PATH, "comment_parser.V1.0.pkl" % COLLECTION_VERSION),
    'post_history': os.path.join(ARQM_PREPRO_PATH, "post_history_parser.%s.pkl" % COLLECTION_VERSION),  # ignore by default
    'post_link': os.path.join(ARQM_PREPRO_PATH, "post_link_parser.%s.pkl" % COLLECTION_VERSION),
    'post': os.path.join(ARQM_PREPRO_PATH, "post_parser.%s.pkl" % COLLECTION_VERSION),
    'user': os.path.join(ARQM_PREPRO_PATH, "user_parser.%s.pkl" % COLLECTION_VERSION),
    'vote': os.path.join(ARQM_PREPRO_PATH, "vote_parser.%s.pkl" % COLLECTION_VERSION),
}

DATA_VERSIONS = {
    'post': 'Posts.%s.xml' % COLLECTION_VERSION,
    'badge': 'Badges.%s.xml' % COLLECTION_VERSION,
    'comment': 'Comments.V1.0.xml' % COLLECTION_VERSION,
    # NOTE: V1.0 has 1.0 GB with more comments, e.g. different: 16020_2011/36106_05/36187/36187_36190.html
    # Doesn't matter when this file being used for initializing other parsers
    'vote': 'Votes.%s.xml' % COLLECTION_VERSION,
    'user': 'Users.%s.xml' % COLLECTION_VERSION,
    'post_link': 'PostLinks.%s.xml' % COLLECTION_VERSION,
    'post_history': 'PostHistory.%s.xml' % COLLECTION_VERSION,
    "tags": "Tags.%s.xml" % COLLECTION_VERSION,
}
