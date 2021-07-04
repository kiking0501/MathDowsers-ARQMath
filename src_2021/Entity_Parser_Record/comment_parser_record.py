from xmlr import xmliter
from Entities.Comment import Comment
from config import RECORD_NUM, PARSER_PKL, CACHE


class CommentParser:
    """
        This class is used for reading the comment file. It reads it record by record.
    """
    def __init__(self, xml_comment_file_path):

        self.map_of_comments_for_post = {}
        for ind, attr_dic in enumerate(xmliter(xml_comment_file_path, 'row')):
            if RECORD_NUM['comment'] is not None and ind >= RECORD_NUM['comment']:
                break

            comment_id = int(attr_dic["@Id"])
            post_id = int(attr_dic["@PostId"])
            text = (attr_dic["@Text"])
            creation_date = None
            score = None
            user_id = None

            if "@Score" in attr_dic:
                score = int(attr_dic["@Score"])
            if "@UserId" in attr_dic:
                user_id = int(attr_dic["@UserId"])
            if "@CreationDate" in attr_dic:
                creation_date = (attr_dic["@CreationDate"])

            comment = Comment(comment_id, post_id, text, score, user_id, creation_date)
            if post_id in self.map_of_comments_for_post:
                self.map_of_comments_for_post[post_id].append(comment)
            else:
                self.map_of_comments_for_post[post_id] = [comment]

    @classmethod
    @CACHE(PARSER_PKL['comment'])
    def load(cls, xml_comment_file_path):
        print("Initiating...")
        parser = cls(xml_comment_file_path)
        return parser
