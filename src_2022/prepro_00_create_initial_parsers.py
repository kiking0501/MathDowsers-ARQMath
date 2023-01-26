"""
Create initial parsers for each MSE entity in pkl format.
These pkl files store selected information from the raw XML files.

Prerequisite:
    data xml files are downloaded at <ARQM_XML_PATH>

Effect:
    parser pkl files are created at the prepro folder
    ("<XXX>_parser.pkl" for Comment, PostLink, Vote, User and Post)

Run by "python <name of this python file>.py"
"""

from Entity_Parser_Record.comment_parser_record import CommentParser
from Entity_Parser_Record.post_history_parser_record import PostHistoryParser
from Entity_Parser_Record.post_link_parser_record import PostLinkParser
from Entity_Parser_Record.post_parser_record import PostParser
from Entity_Parser_Record.user_parser_record import UserParser
from Entity_Parser_Record.vote_parser_record import VoteParser

from config import DATA_VERSIONS, ARQM_XML_PATH
from preload import open_possible_gzip
import os


print("reading comments")
with open_possible_gzip(os.path.join(ARQM_XML_PATH, DATA_VERSIONS["comment"])) as f:
    comment_parser = CommentParser.load(f)

print("reading post links")
with open_possible_gzip(os.path.join(ARQM_XML_PATH, DATA_VERSIONS["post_link"])) as f:
    post_link_parser = PostLinkParser.load(f)

print("reading votes")
with open_possible_gzip(os.path.join(ARQM_XML_PATH, DATA_VERSIONS["vote"])) as f:
    vote_parser = VoteParser.load(f)

print("reading users")
with open_possible_gzip(os.path.join(ARQM_XML_PATH, DATA_VERSIONS["user"])) as f:
    with open_possible_gzip(os.path.join(ARQM_XML_PATH, DATA_VERSIONS["badge"])) as g:
        user_parser = UserParser.load(f, g)

print("reading posts")
with open_possible_gzip(os.path.join(ARQM_XML_PATH, DATA_VERSIONS["post"])) as f:
    post_parser = PostParser.load(
        f,
        comment_parser.map_of_comments_for_post,
        post_link_parser.map_related_posts,
        post_link_parser.map_duplicate_posts,
        vote_parser.map_of_votes, user_parser.map_of_user,
        None)  # ignore post_history_file_path
