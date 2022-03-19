class PostHistory:
    def __init__(self, history_id, post_id, post_history_type_id, revision_guid, creation_date,
                 user_id, user_display_name, comment, text, close_reason_id):
        self.history_id = history_id
        self.post_id = post_id
        self.post_history_type_id = post_history_type_id
        self.revision_guid = revision_guid
        self.creation_date = creation_date
        self.user_id = user_id
        self.user_display_name = user_display_name
        self.comment = comment
        self.text = text
        self.close_reason_id = close_reason_id

    def __repr__(self):
        return "%s[" % self.__class__.__name__ + ', '.join(['{key}={value}'.format(
            key=key,
            value=value if type(value) != str
             else "\"%s%s\"" % (value[:30],
                                "..." if len(value) > 30 else ""))
            for key, value in self.__dict__.items()]) + "]"
