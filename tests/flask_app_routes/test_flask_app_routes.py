from unittest.mock import patch

from manager.db_model import FeedItem, Unread
from tests import TestWrapper, basic_auth_headers


class TestSignup(TestWrapper):
    def test_successful_signup(self):
        payload = {
            "username": "test",
            "password": "test"
        }

        response = self.client.post('/api/users', json=payload)
        self.assertIsNotNone(response)
        self.assertDictEqual({'username': 'test'}, response.json)
        self.assertEqual(201, response.status_code)

    def test_signup_without_password(self):
        payload = {
            "username": "test"
        }

        response = self.client.post('/api/users', json=payload)
        self.assertIsNotNone(response)
        self.assertDictEqual(
            {'message': 'Username and Password are required',
             'payload': {'username': 'test'}}, response.json)
        self.assertEqual(400, response.status_code)

    def test_signup_without_username(self):
        payload = {
            "password": "test"
        }
        response = self.client.post('/api/users', json=payload)
        self.assertIsNotNone(response)
        self.assertDictEqual({
            'message': 'Username and Password are required',
            'payload': {'password': 'test'}}, response.json)
        self.assertEqual(400, response.status_code)

    def test_signup_empty_request_body(self):
        response = self.client.post('/api/users')
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Missing Request Body', 'payload': {}}, response.json)
        self.assertEqual(400, response.status_code)


class TestGetFeeds(TestWrapper):
    def test_get_all_feeds_not_authenticated(self):
        response = self.client.get('/api/feeds')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_get_all_feeds_authenticated(self):
        response = self.client.get(
            '/api/feeds',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        self.assertListEqual([{'id': 1, 'url': 'https://feeds.feedburner.com/tweakers/mixed'},
                              {'id': 2, 'url': 'http://www.nu.nl/rss/Algemeen'}], response.json)
        self.assertEqual(200, response.status_code)


class TestFollowFeed(TestWrapper):
    def test_follow_feed_case_feed_not_exist(self):
        response = self.client.post(
            '/api/feeds/follow',
            headers=basic_auth_headers("user", "pass"),
            json={"feed_id": 5}
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Feed id not found', 'payload': {'feed_id': 5}}, response.json)
        self.assertEqual(404, response.status_code)

    def test_follow_feed_case_not_followed(self):
        response = self.client.post(
            '/api/feeds/follow',
            headers=basic_auth_headers("user", "pass"),
            json={"feed_id": 2}
        )
        self.assertIsNotNone(response)
        with self.app.app_context():
            unread_list = Unread.query.filter_by(username="user").all()

        self.assertEqual(3, len(unread_list))
        list_ids = [1, 3, 4]
        for element in unread_list:
            self.assertIn(element.id, list_ids)
            self.assertEqual("user", element.username)
            self.assertIn(element.item_id, list_ids)
            self.assertIn(element.feed_id, [1, 2, 2])
        self.assertEqual(204, response.status_code)

    def test_follow_feed_case_already_followed(self):
        response = self.client.post(
            '/api/feeds/follow',
            headers=basic_auth_headers("user", "pass"),
            json={"feed_id": 1}
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': "User 'user' already follows feed '1'", 'payload': {}}, response.json)
        self.assertEqual(409, response.status_code)

    def test_follow_feed_case_bad_request(self):
        response = self.client.post(
            '/api/feeds/follow',
            headers=basic_auth_headers("user", "pass"),
            json={"lorem_ipsum": 1}
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': "Missing 'feed_id' in request body",
                              'payload': {'lorem_ipsum': 1}}, response.json)
        self.assertEqual(400, response.status_code)

    def test_follow_feed_case_not_authenticated(self):
        response = self.client.post('/api/feeds/follow', json={"feed_id": 1})
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_follow_feed_empty_request_body(self):
        response = self.client.post('/api/feeds/follow', headers=basic_auth_headers("user", "pass"))
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Missing request body', 'payload': {}}, response.json)
        self.assertEqual(400, response.status_code)


class TestUnfollowFeed(TestWrapper):
    def test_unfollow_feed_case_feed_not_exist(self):
        response = self.client.delete(
            '/api/feeds/unfollow',
            headers=basic_auth_headers("user", "pass"),
            json={"feed_id": 5}
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Feed id not found', 'payload': {'feed_id': 5}}, response.json)
        self.assertEqual(404, response.status_code)

    def test_unfollow_feed_case_followed(self):
        response = self.client.delete(
            '/api/feeds/unfollow',
            headers=basic_auth_headers("user2", "pass"),
            json={"feed_id": 2}
        )
        self.assertIsNotNone(response)
        with self.app.app_context():
            unread_list = Unread.query.filter_by(username="user2").all()

        self.assertEqual(0, len(unread_list))
        self.assertEqual(204, response.status_code)

    def test_unfollow_feed_case_not_following(self):
        response = self.client.delete(
            '/api/feeds/unfollow',
            headers=basic_auth_headers("user2", "pass"),
            json={"feed_id": 1}
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': "User 'user2' does not follow feed '1'", 'payload': {}}, response.json)
        self.assertEqual(409, response.status_code)

    def test_unfollow_feed_case_bad_request(self):
        response = self.client.delete(
            '/api/feeds/unfollow',
            headers=basic_auth_headers("user2", "pass"),
            json={"lorem_ipsum": 1}
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': "Missing 'feed_id' in request body",
                              'payload': {'lorem_ipsum': 1}}, response.json)
        self.assertEqual(400, response.status_code)

    def test_unfollow_feed_case_not_authenticated(self):
        response = self.client.delete('/api/feeds/unfollow', json={"feed_id": 1})
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_unfollow_feed_empty_request_body(self):
        response = self.client.delete('/api/feeds/unfollow', headers=basic_auth_headers("user2", "pass"))
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Missing request body', 'payload': {}}, response.json)
        self.assertEqual(400, response.status_code)


class TestReadFeedItems(TestWrapper):
    def test_read_single_item_case_not_authenticated(self):
        response = self.client.post('/api/items/1/read')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_read_single_item_case_item_not_exist(self):
        response = self.client.post(
            '/api/items/5/read',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Item id not found', 'payload': {}}, response.json)
        self.assertEqual(404, response.status_code)

    def test_read_single_item_case_feed_is_not_followed(self):
        response = self.client.post(
            '/api/items/1/read',
            headers=basic_auth_headers("user3", "pass")
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': "User 'user3' does not follow feed '1'", 'payload': {}}, response.json)
        self.assertEqual(409, response.status_code)

    def test_read_single_item_successfully(self):
        response = self.client.post(
            '/api/items/1/read',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        with self.app.app_context():
            unread_list = Unread.query.filter_by(username="user", feed_id=1).all()
            self.assertEqual(0, len(unread_list))

        self.assertEqual(204, response.status_code)

    def test_read_multiple_items_case_not_authenticated(self):
        response = self.client.post('/api/items/read-multiple')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_read_multiple_items_missing_parameter(self):
        response = self.client.post(
            '/api/items/read-multiple',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Missing request body.', 'payload': {}}, response.json)
        self.assertEqual(400, response.status_code)

    def test_read_multiple_items_successfully(self):
        response = self.client.post(
            '/api/items/read-multiple',
            headers=basic_auth_headers("user2", "pass"),
            json={'item_ids': ['3', '4']}
        )
        self.assertIsNotNone(response)
        with self.app.app_context():
            unread_list = Unread.query.filter_by(username="user2", feed_id=2).all()
            self.assertEqual(0, len(unread_list))

        self.assertEqual(204, response.status_code)


class TestGetReadItems(TestWrapper):
    def test_get_read_items_from_feed_no_auth(self):
        response = self.client.get('/api/my-feeds/1/old')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_get_read_items_from_feed_case_feed_is_missing(self):
        response = self.client.get(
            '/api/my-feeds/5/old',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Feed id not found', 'payload': {}}, response.json)
        self.assertEqual(404, response.status_code)

    def test_get_read_items_from_feed_case_not_followed(self):
        response = self.client.get(
            '/api/my-feeds/1/old',
            headers=basic_auth_headers("user3", "pass")
        )
        self.assertIsNotNone(response)
        self.assertEqual("User 'user3' does not follow feed '1'", response.get_json().get("message"))
        self.assertEqual(409, response.status_code)

    def test_get_read_items_from_feed_successfully(self):
        response = self.client.get(
            '/api/my-feeds/1/old',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        with self.app.app_context():
            unread_list = Unread.query.filter_by(username='user', feed_id=1).all()
            self.assertEqual(1, len(unread_list))
            self.assertEqual(1, unread_list[0].id)
            self.assertEqual("user", unread_list[0].username)
            self.assertEqual(1, unread_list[0].item_id)
            self.assertEqual(1, unread_list[0].feed_id)

        self.assertEqual(200, response.status_code)

    def test_get_all_read_items_no_auth(self):
        response = self.client.get('/api/my-feeds/old')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_get_all_read_items_case_user_follows_no_feed(self):
        response = self.client.get(
            '/api/my-feeds/old',
            headers=basic_auth_headers("user3", "pass")
        )
        self.assertIsNotNone(response)
        self.assertEqual("User 'user3' does not follow any feeds", response.get_json())
        self.assertEqual(200, response.status_code)

    def test_get_all_read_items_case_user_follows_some_feeds(self):
        response = self.client.get(
            '/api/my-feeds/old',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        with self.app.app_context():
            unread_list = Unread.query.filter_by(username='user').all()
            self.assertEqual(1, len(unread_list))
            self.assertEqual(1, unread_list[0].id)
            self.assertEqual("user", unread_list[0].username)
            self.assertEqual(1, unread_list[0].item_id)
            self.assertEqual(1, unread_list[0].feed_id)

        self.assertEqual(200, response.status_code)


class TestGetUnreadItems(TestWrapper):
    def test_get_unread_items_from_feed_no_auth(self):
        response = self.client.get('/api/my-feeds/1/new')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_get_unread_items_from_feed_case_feed_is_missing(self):
        response = self.client.get(
            '/api/my-feeds/5/new',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'Feed id not found', 'payload': {}}, response.json)
        self.assertEqual(404, response.status_code)

    def test_get_unread_items_from_feed_case_not_followed(self):
        response = self.client.get(
            '/api/my-feeds/1/new',
            headers=basic_auth_headers("user3", "pass")
        )
        self.assertIsNotNone(response)
        self.assertDictEqual({'message': 'User user3 does not follow feed 1', 'payload': {}}, response.json)
        self.assertEqual(409, response.status_code)

    def test_get_unread_items_from_feed_successfully(self):
        response = self.client.get(
            '/api/my-feeds/1/new',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        with self.app.app_context():
            unread_list = Unread.query.filter_by(username='user', feed_id=1).all()
            self.assertEqual(1, len(unread_list))
            self.assertEqual(1, len(unread_list))
            self.assertEqual(1, unread_list[0].id)
            self.assertEqual("user", unread_list[0].username)
            self.assertEqual(1, unread_list[0].item_id)
            self.assertEqual(1, unread_list[0].feed_id)

        self.assertEqual(200, response.status_code)

    def test_get_all_unread_items_no_auth(self):
        response = self.client.get('/api/my-feeds/new')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_get_all_unread_items_case_user_follows_no_feed(self):
        response = self.client.get(
            '/api/my-feeds/new',
            headers=basic_auth_headers("user3", "pass")
        )
        self.assertIsNotNone(response)
        self.assertEqual("User 'user3' does not follow any feeds", response.get_json())
        self.assertEqual(200, response.status_code)

    def test_get_all_unread_items_case_user_follows_some_feeds(self):
        response = self.client.get(
            '/api/my-feeds/new',
            headers=basic_auth_headers("user", "pass")
        )
        with self.app.app_context():
            unread_list = Unread.query.filter_by(username='user').all()
            self.assertEqual(1, len(unread_list))
            self.assertEqual(1, len(unread_list))
            self.assertEqual(1, len(unread_list))
            self.assertEqual(1, unread_list[0].id)
            self.assertEqual("user", unread_list[0].username)
            self.assertEqual(1, unread_list[0].item_id)
            self.assertEqual(1, unread_list[0].feed_id)

        self.assertEqual(200, response.status_code)


class TestGetUserSubscribedFeeds(TestWrapper):
    def test_get_user_feeds_without_auth(self):
        response = self.client.get('/api/my-feeds')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_get_user_feeds_case_auth_without_feeds(self):
        response = self.client.get(
            '/api/my-feeds',
            headers=basic_auth_headers("user3", "pass")
        )
        self.assertIsNotNone(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.get_json()))

    def test_get_user_feeds_with_auth_with_feeds(self):
        response = self.client.get(
            '/api/my-feeds',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response)
        self.assertEqual(200, response.status_code)
        self.assertListEqual([{'id': 1, 'url': 'https://feeds.feedburner.com/tweakers/mixed'}], response.get_json())


class TestRefreshUserFeeds(TestWrapper):
    def test_refresh_single_feed_case_not_authenticated(self):
        response = self.client.post('/api/my-feeds/5/update')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_refresh_all_user_feeds_case_not_authenticated(self):
        response = self.client.post('/api/my-feeds/update')
        self.assertIsNone(response.json)
        self.assertEqual(401, response.status_code)

    def test_refresh_single_feed_case_feed_not_exist(self):
        response = self.client.post(
            '/api/my-feeds/5/update',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response.json)
        self.assertDictEqual({'message': 'Feed id not found', 'payload': {}}, response.json)
        self.assertEqual(404, response.status_code)

    @patch("manager.flask_app_routes.Scraper")
    @patch("manager.flask_app_routes.scrape_single")
    def test_refresh_single_feed_successfully(self, scrape_single_task, scraper):
        scraper.parse.return_value = [FeedItem(id=5), FeedItem(id=6)]
        scrape_single_task.return_value = {}

        response = self.client.post(
            '/api/my-feeds/1/update',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response.json)
        self.assertDictEqual({'message': 'Update successful'}, response.json)
        self.assertEqual(200, response.status_code)
        self.assertTrue(scraper.persist.called_with([FeedItem(id=5), FeedItem(id=6)]))
        self.assertTrue(scrape_single_task.delay.called)

    @patch("manager.flask_app_routes.Scraper")
    @patch("manager.flask_app_routes.scrape_single")
    def test_refresh_all_user_feeds_successfully(self, scrape_single_task, scraper):
        scraper.parse.return_value = [FeedItem(id=5), FeedItem(id=6)]
        scrape_single_task.return_value = {}

        response = self.client.post(
            '/api/my-feeds/update',
            headers=basic_auth_headers("user", "pass")
        )
        self.assertIsNotNone(response.json)
        self.assertListEqual([{'feed_id': '1', 'status': 'SUCCESSFUL'}], response.json)
        self.assertEqual(200, response.status_code)
        self.assertTrue(scraper.persist.called_with([FeedItem(id=5), FeedItem(id=6)]))
        self.assertTrue(scrape_single_task.delay.called)
