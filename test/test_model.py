#! /usr/bin/python2
# coding: utf8
import unittest
import os

import model
import config


DB_NAME = '/tmp/testing.db'


def mock_noop(*args, **kwargs):
	pass


class TestUser(unittest.TestCase):
	def verify(self, testuser, username, passwd, email='', dl_left=0, credit=0):
		self.assertEquals(testuser.username, username)
		self.assertTrue(model.compare_passwd(passwd, testuser.hashed_passwd))
		self.assertEquals(testuser.email, email)
		self.assertEquals(testuser.dl_left, dl_left)
		self.assertEquals(testuser.credit, credit)

	def setUp(self):
		model.new_db(DB_NAME)
		config.db = DB_NAME

		# Those are not under test. Hurray for monkeypatched dependency injection!
		self.real_mkkeys = model.User.mkkeys
		model.User.mkkeys = mock_noop
		self.real_mkinstaller = model.User.mkinstaller
		model.User.mkinstaller = mock_noop

		self.invkeys = [model.InviteKey.new().key for _ in xrange(10)]

	def tearDown(self):
		os.remove(DB_NAME)
		model.User.mkkeys = self.real_mkkeys
		model.User.mkinstaller = self.real_mkinstaller

	def test_bad_user(self):
		self.assertRaises(ValueError, model.User.new, 'baduser1', 'validpassword', 'invalidinvkey')
		self.assertRaises(ValueError, model.User.new, 'baduser1', 'validpassword', '')
		self.assertRaises(ValueError, model.User.new, 'baduser1', 'badpass', self.invkeys.pop())
		self.assertRaises(ValueError, model.User.new, 'baduser1', range(10)+['bad type'], self.invkeys.pop())
		model.User.new('samename', 'validpassword', self.invkeys.pop())
		self.assertRaises(ValueError, model.User.new, 'samename', 'validpassword', self.invkeys.pop())

	
	def test_user_no_save(self):
		testuser = model.User.new('testusernosave', '_hunter2', self.invkeys.pop())
		self.verify(testuser, 'testusernosave', '_hunter2')

	def test_user_no_email(self):
		testuser = model.User.new('testusernoemail', '_hunter3', self.invkeys.pop())
		self.verify(testuser, 'testusernoemail', '_hunter3')
		testuser.save()
		returneduser = model.User.get('testusernoemail')
		self.verify(returneduser, 'testusernoemail', '_hunter3')

	def test_user_with_more_stuff(self):
		testuser = model.User.new('testuserwithstuff', '_hunter2', self.invkeys.pop(), 'rawr@example.com')
		testuser.dl_left = 822
		testuser.credit_isk = 2000
		self.verify(testuser, 'testuserwithstuff', '_hunter2', 'rawr@example.com', 822, 2000)
		testuser.save()
		returneduser = model.User.get('testuserwithstuff')
		self.verify(returneduser, 'testuserwithstuff', '_hunter2', 'rawr@example.com', 822, 2000)


class TestInviteKey(unittest.TestCase):
	def setUp(self):
		model.new_db(DB_NAME)
		config.db = DB_NAME

	def tearDown(self):
		os.remove(DB_NAME)
	
	def test_new_key(self):
		k = model.InviteKey.new()
		self.assertTrue(len(k.key) > 0)
		self.assertIsInstance(k.key, str)

	def test_invalid(self):
		k = model.InviteKey('notarealkey')
		self.assertFalse(k.valid)
		self.assertRaises(ValueError, k.use)
		k = model.InviteKey('')
		self.assertFalse(k.valid)
		self.assertRaises(ValueError, k.use)

	def test_using(self):
		k = model.InviteKey.new()
		val = k.key
		del k
		k = model.InviteKey(val)
		self.assertTrue(k.valid)
		k.use()
		self.assertFalse(k.valid)
		self.assertRaises(ValueError, k.use)
		del k
		k = model.InviteKey(val)
		self.assertFalse(k.valid)
		self.assertRaises(ValueError, k.use)


if __name__ == '__main__':
	unittest.main()
