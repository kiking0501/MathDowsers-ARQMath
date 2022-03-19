"""
Modify the map_of_comment_for_post.json file, so that
- it has the most updated comments
    (combining Comment.V1.0.xml and Comment.V1.3.xml)
- formulas with invalid ids are removed

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


def create_extra_map_of_comments(version="V1.3"):
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
        update_file="map_of_comments_for_post_V1.3.json",
        output_file="map_of_comments_for_post_V1013.json"):
    """
        Update the comments in the <original_file> by those in the <update_file> (if same comment id)
        Save the new mapping to <output_file>

        V1.3 Updated: 1357691
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
        comment_file="map_of_comments_for_post_V1013.json",
        output_file=REGENERATED_MAP_OF_COMMENTS_FILE):
    """
        Remove math-containers that have invalid formula ids
        Number of removal: 95784 (V1.2)  Updated: 94553 (V1.3)
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
"""
