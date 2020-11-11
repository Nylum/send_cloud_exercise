from manager import sql_db

from passlib.hash import pbkdf2_sha256


class User(sql_db.Model):
    """Representation of a User in the database"""
    __tablename__ = "users"

    username = sql_db.Column(sql_db.String(256), primary_key=True)
    password = sql_db.Column(sql_db.String(128))

    def hash_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def __str__(self):
        return f"User('usernam'e='{self.username}')"


class Feed(sql_db.Model):
    """Representation of a Feed in the database that is being scraped, ready for any new posts"""
    __tablename__ = "feeds"

    id = sql_db.Column(sql_db.Integer, primary_key=True)
    url = sql_db.Column(sql_db.String(2000))
    parser = sql_db.Column(sql_db.String(20))
    time_format = sql_db.Column(sql_db.String(50))
    last_updated = sql_db.Column(sql_db.TIMESTAMP(timezone=True))

    def serialize(self):
        return {
            'id': self.id,
            'url': self.url
        }

    def __str__(self):
        return f"'id': '{self.id}', 'url': '{self.url}', 'parser': '{self.parser}', " \
               f"'time_format': '{self.time_format}', 'last_updated': '{self.last_updated}'"


class FeedItem(sql_db.Model):
    """Representation of a FeedItem in the database, meaning a single post related to any specific feed"""
    __tablename__ = "feed_items"

    id = sql_db.Column(sql_db.Integer, primary_key=True)
    url = sql_db.Column(sql_db.String(2000))
    title = sql_db.Column(sql_db.String(100))
    description = sql_db.Column(sql_db.String(5000))
    feed_id = sql_db.Column(sql_db.Integer, sql_db.ForeignKey('feeds.id'))
    feed = sql_db.relationship('Feed', backref=sql_db.backref('feed_items', lazy=True))
    published = sql_db.Column(sql_db.TIMESTAMP(timezone=True))

    def serialize(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'published': self.published,
        }

    def __str__(self):
        return f"FeedItem(id='{self.id}', title='{self.title}', feed_id='{self.feed_id}', url='{self.url}', " \
               f"published='{self.published}')"


class Follows(sql_db.Model):
    """This table describes a follow relationship between a User and a Feed, more specific it is showing that
    for each feed a user follows, the table will be populated with a new record
    """
    __tablename__ = "follows"

    id = sql_db.Column(sql_db.Integer(), primary_key=True)

    username = sql_db.Column(sql_db.String, sql_db.ForeignKey('users.username'))
    user = sql_db.relationship('User', backref=sql_db.backref('follows', lazy=True))

    feed_id = sql_db.Column(sql_db.Integer, sql_db.ForeignKey('feeds.id'))
    feed = sql_db.relationship('Feed', backref=sql_db.backref('follows', lazy=True))


class Read(sql_db.Model):
    """This table describes the relationship between a User and a FeedItem, meaning that every item from a feed that
     a user follows that was already seen is considered a Read item
    """
    __tablename__ = "reads"

    id = sql_db.Column(sql_db.Integer(), primary_key=True)

    username = sql_db.Column(sql_db.String, sql_db.ForeignKey('users.username'))
    user = sql_db.relationship('User', backref=sql_db.backref('reads', lazy=True))

    item_id = sql_db.Column(sql_db.Integer, sql_db.ForeignKey('feed_items.id'))
    item = sql_db.relationship('FeedItem', backref=sql_db.backref('reads', lazy=True))

    feed_id = sql_db.Column(sql_db.Integer, sql_db.ForeignKey('feeds.id'))
    feed = sql_db.relationship('Feed', backref=sql_db.backref('reads', lazy=True))


class Unread(sql_db.Model):
    """This table describes a relationship between a User and a FeedItem, meaning that every item from a feed that
    a user follows that wasn't yet seen is considered an Unread item
    """
    __tablename__ = "unreads"

    id = sql_db.Column(sql_db.Integer(), primary_key=True)

    username = sql_db.Column(sql_db.String, sql_db.ForeignKey('users.username'))
    user = sql_db.relationship('User', backref=sql_db.backref('unreads', lazy=True))

    item_id = sql_db.Column(sql_db.Integer, sql_db.ForeignKey('feed_items.id'))
    item = sql_db.relationship('FeedItem', backref=sql_db.backref('unreads', lazy=True))

    feed_id = sql_db.Column(sql_db.Integer, sql_db.ForeignKey('feeds.id'))
    feed = sql_db.relationship('Feed', backref=sql_db.backref('unreads', lazy=True))
