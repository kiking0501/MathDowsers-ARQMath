"""
Create more map-related json files from existing raw map files
    to allow quick access for particular information


Prerequisite:
    raw map-related json files have been created at the "map_raw" folder
    "map_of_comments_for_post.json" at the "map_raw" folder have been cleaned and is most-updated

Effect:
    More map-related files will be created at the "prepro" folder and "map_raw" folder

Run by "python <name of this python file>.py"

"""

import os
from config import (
    ARQM_PREPRO_PATH, MAP_RAW_PATH,
    FINAL_MAP_OF_COMMENTS_FILE, FINAL_MAP_OF_COMMENTS_FOR_QUESTION, FINAL_MAP_OF_COMMENTS_FOR_JUST_ANSWER
)
from tqdm import tqdm
from utility.dao import load_json, dump_json, get_all_post_ids
import copy


creation_year_map = load_json(
    os.path.join(MAP_RAW_PATH, "creation_year_map.json"), keys=[int], verbose=True)


def create_from_map_questions():
    """
        Create a map of {question-id -> latex title}
            to quickly access a title of a given question id

        Create folders, separated by creation year, the map of {question-id -> question content}
            to quickly access questions for a given year
    """
    map_questions = load_json(
        os.path.join(MAP_RAW_PATH, "map_questions.json"), keys=[int], verbose=True)

    question2title = {thread_id: content['title'] for thread_id, content in map_questions.items()}
    dump_json(question2title,
              os.path.join(ARQM_PREPRO_PATH, "question2title.json"))

    map_questions_by_year = {year: {} for year in range(2010, 2019)}

    for year, value in creation_year_map.items():
        print("year", year)
        for thread_id in tqdm(value):
            map_questions_by_year[year][thread_id] = map_questions[thread_id]

    for year in range(2010, 2019):
        dump_json(map_questions_by_year[year],
                  os.path.join(MAP_RAW_PATH, "map_questions_by_year", "map_questions_%d.json" % year))


def create_from_map_answers():
    """
        Create folders, separated by creation year, the map of {question-id -> list of answer contents}
            to quickly access answers for a given year
    """
    map_answers = load_json(
        os.path.join(MAP_RAW_PATH, "map_answers.json"), keys=[int], verbose=True)

    map_answers_by_year = {year: {} for year in range(2010, 2019)}

    for year, value in creation_year_map.items():
        print("year", year)
        for thread_id in tqdm(value):
            if thread_id in map_answers:
                map_answers_by_year[year][thread_id] = map_answers[thread_id]

    for year in range(2010, 2019):
        dump_json(map_answers_by_year[year],
                  os.path.join(MAP_RAW_PATH, "map_answers_by_year", "map_answers_%d.json" % year))


def create_post_bidirectional_map():
    """
        Create map of {post-id -> list of duplicate post-ids}
        Create map of {post-id -> list of related post-ids}

        the linkage are processed so that they are bidirectionally linked
        (if A is related to B, then B is also related to A)
    """

    def create_filtered_bidirectional_map(map_raw, all_post_ids):
        def _filter_post_id():
            d = {}
            for thread_id, v in map_raw.items():
                if thread_id in all_post_ids:
                    d[thread_id] = set([x for x in v if x in all_post_ids])
            return d

        def _create_bidirectional_map(d):
            bimap = copy.deepcopy(d)
            for thread_id, v in d.items():
                for post_id in v:
                    if post_id not in bimap:
                        bimap[post_id] = set()
                    if thread_id not in bimap[post_id]:
                        bimap[post_id].add(thread_id)
            for thread_id, v in bimap.items():
                bimap[thread_id] = list(v)
            return bimap

        new_map = _filter_post_id()
        new_map = _create_bidirectional_map(new_map)
        return new_map

    map_related_posts = load_json(
        os.path.join(MAP_RAW_PATH, "map_related_posts.json"), keys=[int], verbose=True)

    map_duplicate_posts = load_json(
        os.path.join(MAP_RAW_PATH, "map_duplicate_posts.json"), keys=[int], verbose=True)

    all_post_ids = get_all_post_ids(creation_year_map)

    related_post_bimap = create_filtered_bidirectional_map(map_related_posts, all_post_ids)
    dump_json(related_post_bimap,
              os.path.join(ARQM_PREPRO_PATH, "related_post_bimap.json"))

    duplicate_post_bimap = create_filtered_bidirectional_map(map_duplicate_posts, all_post_ids)
    dump_json(duplicate_post_bimap,
              os.path.join(ARQM_PREPRO_PATH, "duplicate_post_bimap.json"))


def separate_comments_for_question_answer():
    """
        Separate the map_of_comments_for_post according to post_id type (question / answer)
    """
    map_of_comments_for_post = load_json(
        os.path.join(MAP_RAW_PATH, FINAL_MAP_OF_COMMENTS_FILE), keys=[int], verbose=True)

    for json_file, output_file in (
        ("map_questions.json", FINAL_MAP_OF_COMMENTS_FOR_QUESTION),
        ("map_just_answers.json", FINAL_MAP_OF_COMMENTS_FOR_JUST_ANSWER),
    ):
        map_json = load_json(
            os.path.join(MAP_RAW_PATH, json_file), keys=[int], verbose=True)

        map_of_comments = {
            k: v for k, v in map_of_comments_for_post.items() if k in map_json}

        dump_json(
            map_of_comments,
            os.path.join(MAP_RAW_PATH, output_file))


if __name__ == '__main__':
    create_from_map_questions()
    create_from_map_answers()
    create_post_bidirectional_map()
    separate_comments_for_question_answer()
