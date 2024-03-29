'''User views tests.'''

from app import app, CURR_USER_KEY
import os
from unittest import TestCase
from flask_bcrypt import Bcrypt

from models import db, User, Message, Like

bcrypt = Bcrypt()

# Set an environmental variable to use a different database for tests.
# (Do this before importing app, since that will have already
# connected to the database.)
os.environ['DATABASE_URL'] = 'postgresql:///warbler_test'

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

# Create tables for all tests.
# For each test, data is deleted and recreated.
db.drop_all()
db.create_all()


'''
When you’re logged in, can you see the follower / following pages for any user?
When you’re logged out, are you disallowed from visiting a user’s follower / following pages?
When you’re logged in, can you add a message as yourself?
When you’re logged in, can you delete a message as yourself?
When you’re logged out, are you prohibited from adding messages?
When you’re logged out, are you prohibited from deleting messages?
When you’re logged in, are you prohibited from deleting another user’s message?
'''


class UserViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup('u1', 'u1@email.com', 'password', None)
        u2 = User.signup('u2', 'u2@email.com', 'password', None)

        db.session.add(u1)
        db.session.add(u2)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u1 = u1
        self.u2 = u2

        m1 = Message(
            text='dogdogdogdogdog',
            user_id=u1.id
        )

        m2 = Message(
            text='catcatcat',
            user_id=u2.id
        )

        db.session.add(m1)
        db.session.add(m2)

        db.session.commit()
        self.m1 = m1
        self.m2 = m2

        l1 = Like(
            user_id=self.u1_id,
            message_id=self.m1.id
        )
        db.session.add(l1)
        db.session.commit()

        self.l1 = l1

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_show_following_page(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = client.get(f'/users/{self.u1_id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.u1.username, html)
            self.assertNotIn(self.u2.username, html)

    def test_no_show_following_page(self):
        with self.client as client:

            resp = client.get(
                f'/users/{self.u1_id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_show_followers_page(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = client.get(f'/users/{self.u2_id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.u2.username, html)
            self.assertNotIn(self.u1.username, html)

    def test_no_show_followers_page(self):
        with self.client as client:

            resp = client.get(
                f'/users/{self.u2_id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_add_follow(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = client.post(f'/users/follow/{self.u1_id}', follow_redirects = True)

            html = resp.get_data(as_text = True)
            self.assertIn('u1', html)

    def test_stop_follow(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = client.post(f'/users/follow/{self.u1_id}', follow_redirects = True)

            html = resp.get_data(as_text = True)
            self.assertIn('u1', html)

            resp_delete = client.post(f'/users/stop-following/{self.u1_id}', follow_redirects = True)

            html = resp_delete.get_data(as_text = True)
            self.assertNotIn('u1', html)

    def test_user_add_message(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = client.post('/messages/new',
                               data={'text': 'test message text',
                                      'user_id': f'{self.u1_id}'}
                               )

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.u1_id}')

    def test_user_no_add_message(self):
        with self.client as client:
            resp = client.post('/messages/new',
                               data={'text': 'text',
                                      'user_id': f'{self.u1_id}'}, follow_redirects = True
                               )
            html = resp.get_data(as_text = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_show_message_page(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = client.get(
                f'/messages/{self.m1.id}'
            )
            html = resp.get_data(as_text = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('dog', html)

    def test_no_show_message_page(self):
        with self.client as client:
            resp = client.get(
                f'/messages/{self.m1.id}', follow_redirects=True
            )
            html = resp.get_data(as_text = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_message_404(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = client.get(
                f'/messages/0'
            )
            self.assertEqual(resp.status_code, 404)

    def test_user_delete_message(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = client.post(f'/messages/{self.m1.id}/delete', follow_redirects = True)
            self.assertEqual(resp.status_code, 200)

            self.assertIsNone(db.session.get(Message, self.m1.id))

    def test_user_delete_message_unauth(self):
        with self.client as client:
            resp = client.post(f'/messages/{self.m1.id}/delete', follow_redirects = True)
            self.assertEqual(resp.status_code, 200)

            self.assertIsNotNone(db.session.get(Message, self.m1.id))

    def test_wrong_user_delete_message_unauth(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = client.post(f'/messages/{self.m1.id}/delete', follow_redirects = True)
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text = True)
            self.assertIn('Access', html)

            self.assertIsNotNone(db.session.get(Message, self.m1.id))