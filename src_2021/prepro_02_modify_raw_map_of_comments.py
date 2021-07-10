"""
Modify the map_of_comment_for_post.json file, so that
- it has the most updated comments
    (combining Comment.V1.0.xml and Comment.V1.2.xml)
- formulas with invalid ids are removed

This is done because of the problems of the Lab-provided Comment files
It can be skipped if the Lab-provided Comment xml file has become bug-free in the future version.
(More explanation can be found at the bottom of this file).

Prerequisite:
    "map_of_comments_for_post.json" has been created at the map_raw folder
    "thread2formulaIds.json" has been created at the prepro folder

Effect:
    <REGENERATED_MAP_OF_COMMENTS_FILE> is created at the map_raw folder

** NOTE **
    if this file is skipped,
    at config.py, FINAL_MAP_OF_COMMENTS_FILE should be set to DEFAULT_MAP_OF_COMMENTS_FILE

Run by "python <name of this python file>.py"

"""

import os
from config import MAP_RAW_PATH, ARQM_PREPRO_PATH, REGENERATED_MAP_OF_COMMENTS_FILE, FINAL_MAP_OF_COMMENTS_FILE
from utility.dao import load_json, dump_json, multiple_str_replace
from dao_replace_formula import MATH_CONTAINER_PATTERNS, FormulaProcessor


VERBOSE = True


def create_extra_map_of_comments(version="V1.2"):
    """
        Create an extra map of comments for update
    """
    from Entity_Parser_Record.comment_parser_record import CommentParser
    from config import ARQM_XML_PATH
    extra_comment_parser = CommentParser(
        os.path.join(ARQM_XML_PATH, "Comments.%s.xml" % version)
    )
    map_of_comments_for_post = {}
    for k, v in extra_comment_parser.map_of_comments_for_post.items():
        map_of_comments_for_post[k] = [vv.__dict__ for vv in v]

    dump_json(
        map_of_comments_for_post,
        os.path.join(MAP_RAW_PATH, "map_of_comments_for_post_%s.json" % version)
    )


def merge_map_of_comments(
        original_file="map_of_comments_for_post.json",
        update_file="map_of_comments_for_post_V1.2.json",
        output_file="map_of_comments_for_post_V1012.json"):
    """
        Update the comments in the <original_file> by those in the <update_file> (if same comment id)
        Save the new mapping to <output_file>
    """
    def thread2commentdict(thread_dict):
        comment_dict = {}
        for comment_list in thread_dict.values():
            for comment in comment_list:
                comment_dict[comment['id']] = comment
        return comment_dict

    ver_original = load_json(
        os.path.join(MAP_RAW_PATH, original_file), keys=[int], verbose=VERBOSE)

    ver_update = load_json(
        os.path.join(MAP_RAW_PATH, update_file), keys=[int], verbose=VERBOSE)
    update_comment_dict = thread2commentdict(ver_update)

    num_updated = 0
    for thread_id, comment_list in ver_original.items():
        update_comments = []
        for comment in comment_list:
            if update_comment_dict.get(comment['id']):
                update_comments.append(update_comment_dict[comment['id']])
                num_updated += 1
            else:
                update_comments.append(comment)
        ver_original[thread_id] = update_comments

    print("#Comments updated: %d" % num_updated)
    dump_json(
        ver_original,
        os.path.join(MAP_RAW_PATH, output_file)
    )


def clean_formulas_in_comments(
        comment_file="map_of_comments_for_post_V1012.json",
        output_file=REGENERATED_MAP_OF_COMMENTS_FILE):
    """
        Remove math-containers that have invalid formula ids
        Number of removal: 95784
    """

    map_of_comments_for_post = load_json(
        os.path.join(MAP_RAW_PATH, comment_file), keys=[int], verbose=True)

    thread2formulaIds = load_json(
        os.path.join(ARQM_PREPRO_PATH, "thread2formulaIds.json"),
        keys=[int]
    )

    num_updated = 0
    for thread_id, comment_list in map_of_comments_for_post.items():
        if thread_id not in thread2formulaIds:
            continue

        min_formula_id, max_formula_id = thread2formulaIds[thread_id]

        update_list = []
        for comment in comment_list:
            replacement_dict = {}
            for pattern in MATH_CONTAINER_PATTERNS:
                for (str_formula_id, formula), math_container in FormulaProcessor.extract_formulas(comment['text'], [pattern]):
                    if int(str_formula_id) not in range(min_formula_id, max_formula_id + 1):
                        replacement_dict[math_container] = formula
            if replacement_dict:
                comment['text'] = multiple_str_replace(replacement_dict, comment['text'])
                num_updated += 1
            update_list.append(comment)
        map_of_comments_for_post[thread_id] = update_list

    print("#Comments updated: %d" % num_updated)
    dump_json(
        map_of_comments_for_post,
        os.path.join(MAP_RAW_PATH, FINAL_MAP_OF_COMMENTS_FILE)
    )


if __name__ == '__main__':
    create_extra_map_of_comments()
    merge_map_of_comments()
    clean_formulas_in_comments()


"""
The comment files for a single version is incomplete

=== Checkings for map_of_comments_for_post.json

1. Comment_V1.0 has much more comments than Comment_V1.2

    Checking 1: V12 has 4,864 missing threads (of comments) (~0.3% of V10)
    V10 #threads: 1,362,555, V12 #threads: 1,357,691

    Checking 2: V12 has total 3,121,194 missing comments under the same thread
    V10 total comments: 4,497,070  (~69% missing)

2. some formulas in commentV10 are better represented in commentV12,
    V10 #affected comments: 690


=== Checkings for map_of_comments_for_question.json
(a subset of map_of_comments_for_post.json where post_ids are all question ids)

1. comment_V1.0 has much more comments than comment_V1.2

    Checking 1: V12 has 2,239 missing threads (of comments)  (~0.3% of V10)
    V10 #threads: 698,299, V12 #threads: 696,060

    Checking 2: V12 has total 1,749,573 missing comments under the same thread
    V10 total comments: 2,450,778  (~71% missing)

2. some formulas in commentV10 are better represented in commentV12,
    V10 #affected comments: 374


=== In this case, we use V10 as our major source of comments, V12 as updates,
    plus formula cleansing (since fromulas from V10 are mor malfunctioned)

    The final generated comment file is named as <REGENERATED_MAP_OF_COMMENTS_FILE> from config.py
    If this file is skipped,
    at config.py, FINAL_MAP_OF_COMMENTS_FILE should be set to DEFAULT_MAP_OF_COMMENTS_FILE
"""
