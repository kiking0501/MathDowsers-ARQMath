class Vote:
    def __init__(self, id, post_id, vote_type_id, user_id, creation_date, bounty_amount):
        self.id = id
        self.post_id = post_id
        self.vote_type_id = vote_type_id
        self.user_id = user_id
        self.creation_date = creation_date
        self.bounty_amount = bounty_amount

    def __repr__(self):
        return "%s[" % self.__class__.__name__ + ', '.join(['{key}={value}'.format(
            key=key,
            value=value if type(value) != str
             else "\"%s%s\"" % (value[:30],
                                "..." if len(value) > 30 else ""))
            for key, value in self.__dict__.items()]) + "]"

"""
VoteTypeId:
    - ` 1`: AcceptedByOriginator
    - ` 2`: UpMod
    - ` 3`: DownMod
    - ` 4`: Offensive
    - ` 5`: Favorite - if VoteTypeId = 5 UserId will be populated
    - ` 6`: Close
    - ` 7`: Reopen
    - ` 8`: BountyStart
    - ` 9`: BountyClose
    - `10`: Deletion
    - `11`: Undeletion
    - `12`: Spam
    - `13`: InformModerator
"""
