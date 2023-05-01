"""

Functions to create and read list of stopwords and ``mathy'' words
    (for filtering and selecting keywords for search queries)

    Source of (English) stopwords:
        Python NLTK library, Lucene Snowball and some manual input

    Source of mathy words:
        NTCIR-12 MathIR task - titles of Wikipedia articles
        MathStackExchange Tags


Prerequisite & Effect for creating the word lists from scratch:

    First, uncomment the if-main functions.

    The stopwords will be created at the folder "data/stopwords".
        Download the NLTK library corpus for creating the NLTK stopwords as "nltk_stopwords.txt".
        Snowball stopwords "lucene_snowball_english_stop.txt" are manually extracted from the Lucene package.
        "manual_stopwords.txt" records stopwords from manual inspection.

    The mathy words will be created at the folder <ARQM_PREPRO_PATH>.
        Download the NTCIR-12 task data at https://ntcir-math.nii.ac.jp/data/ to create "wiki_keywords.txt" (details skipped)
        Put the MSE Tag xml file at <ARQM_XML_PATH> to create "MSE_tag_keywords.txt"

    Run by "python <name of this python file>.py"
"""

import os
from config import DATA_PATH, ARQM_PREPRO_FILTERS_PATH, WIKI_DATA_PATH
from nltk.stem import PorterStemmer
from nltk.tokenize import TreebankWordTokenizer

STEMMER = PorterStemmer()
TOKENIZER = TreebankWordTokenizer()
PUNCTUATIONS = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
PUNC_TABLE = str.maketrans({key: None for key in PUNCTUATIONS})  # string.punctuation


#########  Apply to token / string
def is_hyphenated_token(token):
    strip_token = token.strip("–-")
    return "–" in strip_token or "-" in strip_token


def remove_hyphens(s):
    return s.replace("–", " ").replace("-", " ")


def tokenize(text):
    """
        word with hyphens will be split as separate tokens
    """
    hyphen_list = [x for x in TOKENIZER.tokenize(text) if is_hyphenated_token(x)]
    token_list = [x for x in TOKENIZER.tokenize(remove_hyphens(text))]
    tokens = [x for x in token_list + hyphen_list if x]
    return tokens


def remove_punctuation(text):
    return text.translate(PUNC_TABLE).strip()


#### STOPWORDS
STOPWORD_PATH = os.path.join(DATA_PATH, "stopwords")


def create_nltk_stopwords(output_file="nltk_stopwords.txt"):
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
    with open(os.path.join(STOPWORD_PATH, output_file), "w") as f:
        for x in sorted(stop_words):
            f.write(x + "\n")
        print("%s saved." % f.name)


def read_nltk_stopwords(input_file="nltk_stopwords.txt"):
    stopwords = []
    with open(os.path.join(STOPWORD_PATH, input_file)) as f:
        for l in f.readlines():
            stopwords.append(l.strip())
    return stopwords


def read_lucene_stopwords(input_file="lucene_snowball_english_stop.txt"):
    stopwords = []
    with open(os.path.join(STOPWORD_PATH, input_file)) as f:
        for l in f.readlines():
            word = l.split('|')[0].strip()
            if word:
                stopwords.append(word)
    return stopwords


def read_manual_stopwords(input_file="manual_stopwords.txt"):
    stopwords = []
    with open(os.path.join(STOPWORD_PATH, input_file)) as f:
        for l in f.readlines():
            word = l.split('#')[0].strip()
            if word:
                stopwords.append(word)
    return stopwords

STOPWORDS = set(read_nltk_stopwords() + read_lucene_stopwords() + read_manual_stopwords())


def is_stopword(word):
    if word in STOPWORDS:
        return True
    if not word:
        return True
    if len(word) == 1:
        return True
        # if word in PUNCTUATIONS or word.isalpha():
        #     return True
    try:
        int(remove_punctuation(word))
        return True
    except Exception:
        if any([x.isdigit() for x in remove_punctuation(word)]):
            return True
    return False


#### MSE TAGS
def create_MSE_tags(output_file="MSE_tags.txt"):
    from config import ARQM_XML_PATH, DATA_VERSIONS
    import xml.etree.ElementTree as ET

    tag_xml = os.path.join(ARQM_XML_PATH, DATA_VERSIONS["tags"])
    tree = ET.parse(tag_xml)
    tag_root = tree.getroot()

    count_pairs = []
    for row in tag_root:
        count, full_tag = int(row.attrib['Count']), row.attrib['TagName']
        count_pairs.append((count, full_tag))

    with open(os.path.join(ARQM_PREPRO_FILTERS_PATH, output_file), "w") as f:
        for count, word in sorted(count_pairs, key=lambda x: -x[0]):
            f.write("%s\t%s\n" % (count, word))
        print("%s saved." % f.name)


def create_tag_keywords(input_file="MSE_tags.txt", output_file="MSE_tag_keywords.txt"):
    """
        record counts,
        comment out stopwords,
        store stemmed word
    """
    count_pairs = []
    with open(os.path.join(ARQM_PREPRO_FILTERS_PATH, input_file)) as f:
        for l in f.readlines():
            count, full_tag = l.strip().split('\t')
            count_pairs.append((int(count), full_tag))

    tag_dict = {}
    for count, full_tag in count_pairs:
        for tag in full_tag.split('-'):
            if tag not in tag_dict:
                tag_dict[tag] = 0
            tag_dict[tag] += count

    with open(os.path.join(ARQM_PREPRO_FILTERS_PATH, output_file), "w") as f:
        for tag, count in sorted(tag_dict.items(), key=lambda x: -x[1]):
            if is_stopword(tag):
                f.write("#\t")
            f.write("%s\t%s\t%s\n" % (count, tag, STEMMER.stem(tag)))
        print("%s saved." % f.name)


def read_stemmed_tag_keywords(input_file="MSE_tag_keywords.txt"):
    tag_keywords = []
    with open(os.path.join(ARQM_PREPRO_FILTERS_PATH, input_file)) as f:
        for l in f.readlines():
            if not l.startswith('#'):
                count, tag, stem_tag = l.strip().split('\t')
                tag_keywords.append(stem_tag)
    return tag_keywords

STEMMED_TAG_KEYWORDS = set(read_stemmed_tag_keywords())


#### Wiki Tag Words
def create_wiki_keywords(output_file="wiki_keywords.txt"):

    tag_dict = {}

    with open(os.path.join(WIKI_DATA_PATH, "Wiki12-file-locator.txt")) as f:
        for l in f.readlines():
            _, html_title = l.strip().split()
            text = html_title.replace(".html", "").replace("_", " ")
            text = text.replace("(", "").replace(")", "")

            text = text.lower()
            for tag in tokenize(text):
                if not is_hyphenated_token(tag):
                    tag = remove_punctuation(tag)
                if not tag:
                    continue
                if tag not in tag_dict:
                    tag_dict[tag] = 0
                tag_dict[tag] += 1

    with open(os.path.join(ARQM_PREPRO_FILTERS_PATH, output_file), "w") as f:
        for tag, count in sorted(tag_dict.items(), key=lambda x: -x[1]):
            if is_stopword(tag):
                f.write("#\t")
            f.write("%s\t%s\t%s\n" % (count, tag, STEMMER.stem(tag)))
        print("%s saved." % f.name)


def read_stemmed_wiki_keywords(input_file="wiki_keywords.txt"):
    wiki_keywords = []
    with open(os.path.join(ARQM_PREPRO_FILTERS_PATH, input_file)) as f:
        for l in f.readlines():
            if not l.startswith('#'):
                count, tag, stem_tag = l.strip().split('\t')
                wiki_keywords.append(stem_tag)
    return wiki_keywords

STEMMED_WIKI_KEYWORDS = set(read_stemmed_wiki_keywords())


if __name__ == '__main__':
    # create_nltk_stopwords()
    # create_MSE_tags()
    # create_tag_keywords()
    # create_wiki_keywords()
    pass  # enable the above to create the word lists from scratch
