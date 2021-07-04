class User:
    def __init__(self, id, reputation, age, location, creation_date, views, lst_badges,
                 about_me, up_votes, down_votes, website_url, last_access_date, display_name):
        self.id = id
        self.reputation = reputation
        self.age = age
        self.location = location
        self.creation_date = creation_date
        self.views = views
        self.lst_badges = lst_badges
        self.about_me = about_me
        self.up_votes = up_votes
        self.down_votes = down_votes
        self.website_url = website_url
        self.last_access_date = last_access_date
        self.display_name = display_name

    def __repr__(self):
        return "%s[" % self.__class__.__name__ + ', '.join(['{key}={value}'.format(
            key=key,
            value=value if type(value) != str
             else "\"%s%s\"" % (value[:30],
                                "..." if len(value) > 30 else ""))
            for key, value in self.__dict__.items()]) + "]"
