'''User model tests.'''

# Run these tests like:
#
#    python -m unittest test_user_model.py

from app import app
import os
from unittest import TestCase
from flask_bcrypt import Bcrypt

from models import db, User

bcrypt = Bcrypt()

# Set an environmental variable to use a different database for tests.
# (Do this before importing app, since that will have already
# connected to the database.)
os.environ['DATABASE_URL'] = 'postgresql:///warbler_test'

# Create tables for all tests.
# For each test, data is deleted and recreated.
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup('u1', 'u1@email.com', 'password', None)
        u2 = User.signup('u2', 'u2@email.com', 'password', None)

        db.session.add(u1)
        db.session.add(u2)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_signup(self):
        u = User.signup(
            username='uname',
            email='e@e.com',
            password='pwd',
            image_url=None
        )

        self.assertEqual(u.username, 'uname')
        self.assertEqual(u.email, 'e@e.com')
        self.assertNotEqual(u.password, 'pwd')

        self.assertTrue(bcrypt.check_password_hash(u.password,'pwd'))

    def test_invalid_signup(self):
        u = User.signup(
            username='uname',
            email='egg',
            password='pwd',
            image_url=None
        )

        self.assertEqual(User.query.get(u.id), None)

    def test_auth_ok(self):
        u = db.session.get(User, self.u1_id)
        self.assertEqual(User.authenticate('u1', 'password'), u)

    def test_auth_fail_no_user(self):
        self.assertFalse(User.authenticate('user-X', 'password'))

    def test_auth_ok_wrong_pwd(self):
        u2 = User.query.get(self.u2_id)
        self.assertFalse(User.authenticate('u2', 'wrong'))

    def test_user_is_following(self):

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))

    def test_user_is_not_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u1.is_following(u2))

    def test_user_is_followed_by(self):

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)
        db.session.commit()

        self.assertTrue(u2.is_followed_by(u1))

    def test_user_is_not_followed_by(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u1.is_followed_by(u2))