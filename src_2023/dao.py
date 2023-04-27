import json
import re
import os
import gzip


HTML_CHAR_MAP = {
    "&nbsp;": " ",
    "&lt;": "<",
    "&gt;": ">",
    "&amp;": "&",
    "&quot;": "\"",
    "&apos;": "\'",
}

ESCAPE_HTML_CHAR_MAP = {
    v: k for k, v in HTML_CHAR_MAP.items()
    if k != "&amp;"}  # NOTE: try to deal with mixed escaping (some text are escaped)


def multiple_str_regex(dictionary):
    return re.compile("(%s)" % "|".join(map(re.escape, dictionary.keys())))


def multiple_str_sub(regex, dictionary, text):
    return regex.sub(lambda mo: dictionary[mo.string[mo.start():mo.end()]], text)
    # trying adding re.DOTALL after ARQMath 2021, but fail, etc 1_2010/12550_12/13094.html


def multiple_str_replace(dictionary, text):
    """
        Warning: will break if a dict key is a prefix of others
        Reference:
        https://stackoverflow.com/questions/15175142/how-can-i-do-multiple-substitutions-using-regex
        https://code.activestate.com/recipes/81330-single-pass-multiple-replace/
    """

    # Create a regular expression from the dictionary keys
    regex = multiple_str_regex(dictionary)

    # For each match, look-up corresponding value in dictionary
    return multiple_str_sub(regex, dictionary, text)


HTML_CHAR_MAP_REGEX = multiple_str_regex(HTML_CHAR_MAP)
ESCAPE_HTML_CHAR_MAP_REGEX = multiple_str_regex(ESCAPE_HTML_CHAR_MAP)


def clean_escape_html(text):
    """
        need to escape since "&amp;gt;" exists in tsv file
    """
    while "&amp;" in text:
        text = text.replace("&amp;", "&")

    text = multiple_str_sub(HTML_CHAR_MAP_REGEX, HTML_CHAR_MAP, text)
    return text


def escape_html(text):
    """
        escape text for html file e.g. comment file
    """
    text = multiple_str_sub(ESCAPE_HTML_CHAR_MAP_REGEX, ESCAPE_HTML_CHAR_MAP, text)
    return text


def load_json(file_path, keys=None, verbose=False):
    """
        Load the json file as a Python dictionary object
        Additionally, convert the dictionary keys to types declared in the keys parameter
        (by default, all dict keys would be in str type)

        keys should be a list of types, corresponding to each layer of key in a dictionary object
        e.g. keys=[int]: convert the first layer of key to int type {key(int) -> content}
             keys=[int, int]: convert the first and second layer of key to int type {key(int) -> key(int) -> content}

    """
    def convert_keys(d, remain_keys):
        if not isinstance(d, dict) or not remain_keys:
            return d
        func = remain_keys[0]
        return {func(k): convert_keys(v, remain_keys[1:])
                for k, v in d.items()}

    if verbose:
        print("Loading %s..." % file_path)
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            d = json.load(f)
    else:
        with gzip.open(file_path+".gz", "rt") as f:
            d = json.load(f)
    return convert_keys(d, keys)


def dump_json(d, file_path, verbose=True):
    if os.path.isfile(file_path):
        os.remove(file_path)
    with gzip.open(file_path+".gz", "wt") as f:
        json.dump(d, f, indent=2)
    if verbose:
        print("Finish dumping %s." % file_path)


def sort_topic_ids(topic_ids):
    """
        topic_id: A.XXX / B.XXX
    """
    return sorted(topic_ids, key=lambda x: int(x.partition('.')[2]))


def sort_formula_ids(formula_ids):
    """
        task1 formula_id: q_XXX
    """
    return sorted(formula_ids, key=lambda x: int(x.partition('_')[2]))
