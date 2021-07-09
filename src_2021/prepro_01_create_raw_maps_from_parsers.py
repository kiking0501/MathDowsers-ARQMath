"""
Save selected raw information from each parser
    as separate json files in the "map_raw" folder.

Prerequisite:
    parser pkl files have been created at the prepro folder

Effect:
    raw map-related json files are created at the "map_raw" folder

Run by "python <name of this python file>.py"
"""


from Entity_Parser_Record.comment_parser_record import CommentParser
from Entity_Parser_Record.post_link_parser_record import PostLinkParser
from Entity_Parser_Record.user_parser_record import UserParser
from Entity_Parser_Record.vote_parser_record import VoteParser
from Entity_Parser_Record.post_parser_record import PostParser
from config import MAP_RAW_PATH
from utility.dao import dump_json
import os


def create_raw_map_from_comment_parser():
    """
        Create raw map of {post_id -> comment content}
    """
    print("reading comments")
    comment_parser = CommentParser.load(None)

    map_of_comments_for_post = {}
    for k, v in comment_parser.map_of_comments_for_post.items():
        map_of_comments_for_post[k] = [vv.__dict__ for vv in v]

    dump_json(
        map_of_comments_for_post,
        os.path.join(MAP_RAW_PATH, "map_of_comments_for_post.json")
    )


def create_raw_map_from_postlink_parser():
    """
        Create raw map of {post-id -> list of duplicate post-ids}
        Create raw map of {post-id -> list of related post-ids}

        The linkages are in their raw form, i.e. can be single linked
        (A is related to B but B might not be related to A)
    """
    print("reading post links")
    post_link_parser = PostLinkParser.load(None)

    map_related_posts = {}
    for k, v in post_link_parser.map_related_posts.items():
        map_related_posts[k] = [vv for vv in v]

    dump_json(
        map_related_posts,
        os.path.join(MAP_RAW_PATH, "map_related_posts.json")
    )

    map_duplicate_posts = {}
    for k, v in post_link_parser.map_duplicate_posts.items():
        map_duplicate_posts[k] = [vv for vv in v]

    dump_json(
        map_duplicate_posts,
        os.path.join(MAP_RAW_PATH, "map_duplicate_posts.json")
    )


def create_raw_map_from_vote_parser():
    """
        Create raw map of {post-id -> vote content}
    """
    print("reading votes")
    vote_parser = VoteParser.load(None)

    map_of_votes = {}
    for k, v in vote_parser.map_of_votes.items():
        map_of_votes[k] = [vv.__dict__ for vv in v]

    dump_json(
        map_of_votes,
        os.path.join(MAP_RAW_PATH, "map_of_votes.json")
    )


def create_raw_map_from_user_parser():
    """
        Create raw map of {user_id -> user content}
    """
    print("reading users")
    user_parser = UserParser.load(None, None)

    map_of_user = {}
    for k, v in user_parser.map_of_user.items():
        map_of_user[k] = v.__dict__

    dump_json(
        map_of_user,
        os.path.join(MAP_RAW_PATH, "map_of_user.json")
    )


def create_raw_map_from_post_parser():
    """
        Create raw map of {year -> list of thread-ids created at that year}
        Create raw map of {post-id (quesiton only) -> question content}
        Create raw map of {post-id (quesiton only) -> list of answer content}
        Create raw map of {post-id (answer only) -> answer content}
    """
    attrs = [
        'post_id',
        'creation_date',
        'body',
        'view_count',
        'score',
        'comment_count',
        'owner_user_id',
        'last_edit_date',
        'last_activity_date',
        'last_editor_user_id',
        'community_owned_date',
        'last_editor_display_name',
    ]

    question_attrs = [
        'title',
        'comment_count',
        'answer_count',
        'favourite_count',
        'accepted_answer_id',
        'closed_date',
        'tags',
    ]

    answer_attrs = [
        'parent_id'
    ]

    print("reading posts")
    post_parser = PostParser.load(
        None, None, None, None, None, None, None)

    # {year -> list of thread_ids}
    dump_json(
        post_parser.creation_year_map,
        os.path.join(MAP_RAW_PATH, "creation_year_map.json")
    )

    # {post_id -> Question dict}; post_id = thread_id
    map_questions = {}
    for k, v in post_parser.map_questions.items():
        map_questions[k] = {kk: vv for kk, vv in v.__dict__.items()
                            if kk in attrs + question_attrs}
    dump_json(
        map_questions,
        os.path.join(MAP_RAW_PATH, "map_questions.json")
    )

    # {parent(post)_id -> Answer dict}; post_id = thread_id
    map_answers = {}
    for k, v in post_parser.map_answers.items():
        map_answers[k] = [{kk: vv for kk, vv in vvv.__dict__.items()
                          if kk in attrs + answer_attrs}
                          for vvv in v]
    dump_json(
        map_answers,
        os.path.join(MAP_RAW_PATH, "map_answers.json")
    )

    # {post_id -> Answer dict}; post_id = answer_id
    map_just_answers = {}
    for k, v in post_parser.map_just_answers.items():
        map_just_answers[k] = {kk: vv for kk, vv in v.__dict__.items()
                               if kk in attrs + answer_attrs}
    dump_json(
        map_just_answers,
        os.path.join(MAP_RAW_PATH, "map_just_answers.json")
    )


if __name__ == '__main__':
    create_raw_map_from_comment_parser()
    create_raw_map_from_postlink_parser()
    create_raw_map_from_vote_parser()
    create_raw_map_from_user_parser()
    create_raw_map_from_post_parser()
