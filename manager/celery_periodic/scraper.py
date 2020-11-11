import pytz
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

from manager.db_model import FeedItem, Feed, Follows, Unread
from manager import sql_db
from sqlalchemy.exc import SQLAlchemyError


class Scraper:
    """A class that scans provided feed urls for new posts and stores them in the database

    The implementation downloads the full content of the feed page, parses it according to specific feed details
    contained in config.py and extracts the new posted feed items. They are then stored in the database as well as
    specific relationship details are created for each user that follows the specified feed.
    """
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    def __init__(self, feed):
        url = feed.get("url")
        self.feed = Feed.query.filter_by(url=url).first()

    @staticmethod
    def get_title(feed_item) -> str:
        """Gets the title of a single parsed feed item in string format"""
        return feed_item.title.string

    @staticmethod
    def get_description(feed_item) -> str:
        """Gets the description of a single parsed feed item in string format"""
        return feed_item.description.string

    @staticmethod
    def get_url(feed_item):
        """Gets the URL of a single parsed feed item in string format"""
        return feed_item.link.next

    def get_published_time(self, feed_item) -> datetime:
        """Calculates the time of publication of a single parsed feed item in datetime object format"""

        date = datetime.strptime(feed_item.pubdate.string, self.feed.time_format)
        publication_time = datetime(
            year=date.year, month=date.month, day=date.day, hour=date.hour,
            minute=date.minute, second=date.second, tzinfo=pytz.utc if not date.tzinfo else date.tzinfo
        )

        return publication_time

    def build_sql_db_object(self, not_parsed_feed_item) -> FeedItem:
        """Prepares a FeedItem object ready to be stored in the database

        :param not_parsed_feed_item: feed that has not been parsed yet
        :return FeedItem object successfully built
        """

        return FeedItem(
            url=self.get_url(not_parsed_feed_item),
            title=self.get_title(not_parsed_feed_item),
            description=self.get_description(not_parsed_feed_item),
            feed_id=self.feed.id,
            published=self.get_published_time(not_parsed_feed_item)
        )

    def parse(self) -> list:
        """Downloads the content of the specified feed url and prepares the storage of FeedItem objects

        :return None
        """

        try:
            response = requests.get(self.feed.url)
            if response.content:
                soup = BeautifulSoup(response.content, self.feed.parser)
                items = list()

                for feed_item in soup.find_all("item"):
                    if self.feed.last_updated < self.get_published_time(feed_item):
                        sql_db_feed_item = self.build_sql_db_object(feed_item)
                        items.append(sql_db_feed_item)
                return items
            return list()
        except ConnectionError as err:
            self.logger.error(f"Connection for url '{self.feed.url}' not available. Aborting...", err)
            raise err
        except (AttributeError, KeyError) as err:
            self.logger.error(f"Problem parsing data for feed '{self.feed.url}'", err)
            raise err
        except Exception as err:
            raise err

    def persist(self, feed_items: list):
        """Stores a list of FeedItem objects in the database

        :param feed_items: The collection of FeedItem objects to be stored
        :return None
        """
        try:
            if feed_items:
                sql_db.session.add_all(feed_items)

                # Adding an Unread relationship between each new item and each user that follows the current feed
                users_that_follow_current_feed = Follows.query.filter_by(feed_id=self.feed.id).all()
                for item in feed_items:
                    if users_that_follow_current_feed:
                        for user in users_that_follow_current_feed:
                            unread = Unread(username=user.username, item_id=item.id)
                            sql_db.session.add(unread)

                # Updating the last_updated timestamp of the specific Feed
                date = datetime.now()
                last_updated = datetime(year=date.year, month=date.month, day=date.day, hour=date.hour,
                                        minute=date.minute, second=date.second,
                                        tzinfo=pytz.utc if not date.tzinfo else date.tzinfo)
                self.feed.last_updated = last_updated

                # Adding a Feed record inside the db
                sql_db.session.add(self.feed)
                sql_db.session.commit()
        except SQLAlchemyError as err:
            sql_db.session.rollback()
            self.logger.error(f"Impossible to store the generated FeedItem the database", err)
            raise err
        except Exception as err:
            raise err
