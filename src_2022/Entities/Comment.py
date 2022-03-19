class Comment:
    def __init__(self, comment_id, related_post_id, text, score, user_id, creation_date):
        self.id = comment_id
        self.related_post_id = related_post_id
        self.text = text
        self.score = score
        self.user_id = user_id
        self.creation_date = creation_date

    def __repr__(self):
        return "%s[" % self.__class__.__name__ + ', '.join(['{key}={value}'.format(
            key=key,
            value=value if type(value) != str
             else "\"%s%s\"" % (value[:100],
                                "..." if len(value) > 100 else ""))
            for key, value in self.__dict__.items()]) + "]"
