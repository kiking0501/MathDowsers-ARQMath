"""
Creates initial parser for each MSE entity in pkl format. These pkl files stores selected information from the raw XML file.

Run py "python 01_create_initial_parsers.py"
"""

from Entity_Parser_Record.comment_parser_record import CommentParser
from Entity_Parser_Record.post_history_parser_record import PostHistoryParser
from Entity_Parser_Record.post_link_parser_record import PostLinkParser
from Entity_Parser_Record.post_parser_record import PostParser
from Entity_Parser_Record.user_parser_record import UserParser
from Entity_Parser_Record.vote_parser_record import VoteParser

from config import DATA_VERSIONS, ARQM_XML_PATH
import os


print("reading comments")
comment_parser = CommentParser.load(
    os.path.join(ARQM_XML_PATH, DATA_VERSIONS["comment"]))

print("reading post links")
post_link_parser = PostLinkParser.load(
    os.path.join(ARQM_XML_PATH, DATA_VERSIONS["post_link"]))

print("reading votes")
vote_parser = VoteParser.load(
    os.path.join(ARQM_XML_PATH, DATA_VERSIONS["vote"]))

print("reading users")
user_parser = UserParser.load(
    os.path.join(ARQM_XML_PATH, DATA_VERSIONS["user"]),
    os.path.join(ARQM_XML_PATH, DATA_VERSIONS["badge"]))

print("reading posts")
post_parser = PostParser.load(
    os.path.join(ARQM_XML_PATH, DATA_VERSIONS["post"]),
    comment_parser.map_of_comments_for_post,
    post_link_parser.map_related_posts,
    post_link_parser.map_duplicate_posts,
    vote_parser.map_of_votes, user_parser.map_of_user,
    None)  # ignore post_history_file_path
