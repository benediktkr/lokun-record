#! /usr/bin/env python2
# coding: utf8

"""Functional testing for the REST API.

Depends on WebTest, which is not in the standard library and also not included
in git.
Pretty badly written but meh, I was half-asleep.
"""

import sys
sys.path.append("..")

import unittest
import os

from webtest import TestApp

from record import restapi
from record import model
from record import config


DB_NAME = '/tmp/testing.db'


def mock_noop(*args, **kwargs):
	pass


class TestREST(unittest.TestCase):
	def verify_userjson(self, json, name, email=None, dl_left=0, credit=0):
		self.assertNotIn('error', json)
		self.assertEquals(json['username'], name)
		if email:
			self.assertEquals(json['email'], email)
		self.assertNotIn('password', json)
		self.assertEquals(json['dl_left'], dl_left)
		self.assertEquals(json['credit_isk'], credit)

	
	def setUp(self):
		model.new_db(DB_NAME)
		config.db = DB_NAME

		# Not under test
		self.real_mkkeys = model.User.mkkeys
		model.User.mkkeys = mock_noop
		self.real_mkinstaller = model.User.mkinstaller
		model.User.mkinstaller = mock_noop

		app = restapi.app()
		app.catchall = False
		self.app = TestApp(app)
		self.invkeys = [model.InviteKey.new().key for _ in xrange(20)]

	def tearDown(self):
		os.remove(DB_NAME)
		model.User.mkkeys = self.real_mkkeys
		model.User.mkinstaller = self.real_mkinstaller

	def test_create_user(self):
		resp = self.app.put('/users/testuser1', dict(
				password='validpassword',
				invite_key=self.invkeys.pop()))
		self.verify_userjson(resp.json, 'testuser1')

		resp = self.app.post('/users', dict(
				username='testuser2',
				password='validpassword',
				invite_key=self.invkeys.pop()))
		self.verify_userjson(resp.json, 'testuser2')

		resp = self.app.put('/users/testuser3', dict(
				password='validpassword',
				email='testuser3@example.com',
				invite_key=self.invkeys.pop()))
		self.verify_userjson(resp.json, 'testuser3', email='testuser3@example.com')

	def test_create_invalid_user(self):
		resp = self.app.put('/users/testuser4', dict(
				password='validpassword',
				invite_key='invalidinvitekey'), status=403)
		self.assertEqual(resp.json['error'], "Invite key not valid")

		resp = self.app.put('/users/testuser5', dict(
				password='validpassword'), status=400)
		self.assertEqual(resp.json['error'], "Must include an invite_key")

		resp = self.app.put('/users/testuser6', dict(
				invite_key=self.invkeys.pop()), status=400)
		self.assertEqual(resp.json['error'], "Must include a password")

		resp = self.app.put('/users/validuser', dict(
				password='validpassword',
				invite_key=self.invkeys.pop()))
		resp = self.app.put('/users/validuser', dict(
				password='anothervalidpassword',
				invite_key=self.invkeys.pop()), status=401)
		self.assertEqual(resp.json['error'], "Wrong username/password combination")

	def test_access_user(self):
		resp = self.app.put('/users/accesstestuser', dict(
				password='validpassword',
				email='hurr@example.com',
				invite_key=self.invkeys.pop()))
		self.verify_userjson(resp.json, 'accesstestuser')

		resp = self.app.put('/users/accesstestuser', dict(password='validpassword'))
		self.verify_userjson(resp.json, 'accesstestuser', email='hurr@example.com')
		resp = self.app.post('/users/accesstestuser', dict(password='validpassword'))
		self.verify_userjson(resp.json, 'accesstestuser', email='hurr@example.com')

		resp = self.app.put('/users/accesstestuser', dict(password='wrongpassword'), status=401)
		self.assertEqual(resp.json['error'], "Wrong username/password combination")
		self.assertNotIn('username', resp.json)
		resp = self.app.put('/users/accesstestuser', {}, status=400)
		self.assertEqual(resp.json['error'], "Must include a password")
		resp = self.app.post('/users/accesstestuser', dict(password='wrongpassword'), status=401)
		self.assertEqual(resp.json['error'], "Wrong username/password combination")
		self.assertNotIn('username', resp.json)
		resp = self.app.post('/users/accesstestuser', {}, status=400)
		self.assertEqual(resp.json['error'], "Must include a password")

		

if __name__ == '__main__':
	unittest.main()
