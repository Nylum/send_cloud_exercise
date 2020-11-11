from datetime import datetime

import pytz
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from manager.db_model import User, Feed, Follows, FeedItem, Unread, Read


def generate_setup() -> list:
    """Used to populate the db with hardcoded data"""

    # --------------------------------------------- User table --------------------------------------------------------
    user1 = User(username="user", password=pbkdf2_sha256.hash("pass"))
    user2 = User(username="user2", password=pbkdf2_sha256.hash("pass"))
    user3 = User(username="user3", password=pbkdf2_sha256.hash("pass"))

    # --------------------------------------------- Feed table --------------------------------------------------------
    feed_dt = datetime(year=2020, month=11, day=10, hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
    feed1 = Feed(id=1, url="https://feeds.feedburner.com/tweakers/mixed", parser="html5lib",
                 time_format="%a, %d %b %Y %H:%M:%S %Z", last_updated=feed_dt)
    feed2 = Feed(id=2, url="http://www.nu.nl/rss/Algemeen", parser="lxml",
                 time_format="%a, %d %b %Y %H:%M:%S %z",
                 last_updated=feed_dt)

    # --------------------------------------------- Follows table -----------------------------------------------------
    follows1 = Follows(username=user1.username, feed_id=feed1.id)
    follows2 = Follows(username=user2.username, feed_id=feed2.id)

    # --------------------------------------------- FeedItem table ----------------------------------------------------
    item_dt = datetime(year=2020, month=11, day=10, hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
    item1 = FeedItem(
        id=1, url="https://www.amazon.com/", title="Item 1", description="Desc 1", feed_id=1,
        published=item_dt)
    item2 = FeedItem(
        id=2, url="https://www.ebay.com/", title="Item 2", description="Desc 2", feed_id=1, published=item_dt)
    item3 = FeedItem(
        id=3, url="https://www.subito.it/", title="Item 3", description="Desc 3", feed_id=2,
        published=item_dt)
    item4 = FeedItem(
        id=4, url="https://www.kijiji.it/", title="Item 4", description="Desc 4", feed_id=2, published=item_dt)

    # --------------------------------------------- Read/Unread tables ------------------------------------------------
    unread1 = Unread(username=user1.username, item_id=1, feed_id=1)
    read1 = Read(username=user1.username, item_id=2, feed_id=1)
    unread2 = Unread(username=user2.username, item_id=3, feed_id=2)
    read2 = Read(username=user2.username, item_id=4, feed_id=2)

    # --------------------------------------------- End of tables population ------------------------------------------
    return [user1, user2, user3, feed1, feed2, follows1, follows2, item1, item2,
            item3, item4, unread1, unread2, read1, read2]
