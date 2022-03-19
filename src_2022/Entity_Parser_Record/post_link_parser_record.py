from xmlr import xmliter
from config import RECORD_NUM, PARSER_PKL, CACHE


class PostLinkParser:
    """
        This class is used for reading the post link file. It reads it record by record.
    """
    def __init__(self, xml_post_link_file_path):
        self.map_duplicate_posts = {}
        self.map_related_posts = {}
        for ind, attr_dic in enumerate(xmliter(xml_post_link_file_path, 'row')):
            if RECORD_NUM['post_link'] is not None and ind >= RECORD_NUM['post_link']:
                break

            post_id = int(attr_dic["@PostId"])
            related_post_id = int(attr_dic["@RelatedPostId"])
            link_type_id = int(attr_dic["@LinkTypeId"])

            if link_type_id == 3:  # Duplicate
                if post_id in self.map_duplicate_posts:
                    self.map_duplicate_posts[post_id].append(related_post_id)
                else:
                    self.map_duplicate_posts[post_id] = [related_post_id]
            elif link_type_id == 1:  # Related
                if post_id in self.map_related_posts:
                    self.map_related_posts[post_id].append(related_post_id)
                else:
                    self.map_related_posts[post_id] = [related_post_id]

    @classmethod
    @CACHE(PARSER_PKL['post_link'])
    def load(cls, xml_post_link_file_path):
        print("Initiating...")
        parser = cls(xml_post_link_file_path)
        return parser
