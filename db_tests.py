import init_db, sqlite3, time, unittest, chatter_classes, datetime

db = sqlite3.connect('test.db', detect_types=sqlite3.PARSE_DECLTYPES)
db.row_factory = sqlite3.Row


def add_test_users(db:sqlite3.Connection):

    c = db.cursor()

    # INSERT TEST USERS
    sql = '''INSERT INTO User VALUES
                    (NULL,'TestUser1','test1',0,0,1),
                    (NULL,'TestUser2','test2',0,0,1),
                    (NULL,'TestUser3','test3',0,0,1),
                    (NULL,'TestUser4','test4',0,0,1),
                    (NULL,'TestUser5','test5',0,0,1),
                    (NULL,'TestAdmin','testadmin',0,1,1)        
        '''
    c.execute(sql)

    db.commit()

    print("Success: Added test users")


def add_test_chatrooms(db:sqlite3.Connection):

    c = db.cursor()

    # INSERT TEST CHATROOMS
    sql = '''INSERT INTO Chatroom VALUES 
                    (NULL,'TestRoom1','A test chatroom','apxffa'),
                    (NULL,'TestRoom2','A test chatroom','3jxFsd'),
                    (NULL,'TestRoom3','A test chatroom','Ajf38s')
        '''

    c.execute(sql)
    db.commit()

    print("Success: Added test chatrooms")


def add_chatroom_members(db:sqlite3.Connection):

    c = db.cursor()

    sql = '''INSERT INTO ChatroomMember VALUES 
                (1, 1, 1),
                (1, 2, 0),
                (1, 3, 0),
                (2, 2, 1),
                (2, 3, 0),
                (2, 4, 0),
                (3, 1, 1),
                (3, 2, 1),
                (3, 3, 0),
                (3, 4, 0),
                (3, 5, 0)
                '''

    c.execute(sql)
    db.commit()
    print("Success: Added Chatroom Members")


def add_messages(db:sqlite3.Connection):

    c = db.cursor()

    # We need to add import time to the start of db_tests.py
    base_time = int(time.time()) - 3600  # Set the message timestamp to be 1 hour ago

    sql =  '''INSERT INTO Message VALUES 
                    (NULL, 'This is the first message in TestRoom1, sent by TestUser1. It has two attachments (a picture of Donald Trump and another of Gary Barlow).', 1, 1, ?),
                    (NULL, 'This is the second message in TestRoom1, sent by TestUser2.', 1, 2, ?),
                    (NULL, 'This is the third message in TestRoom1, sent by TestUser3.', 1, 3, ?),
                    (NULL, 'This is the fourth message in TestRoom1, sent by TestUser1.', 1, 1, ?),
                    (NULL, 'This is the fifth message in TestRoom1, sent by TestUser3.', 1, 3, ?),
                    (NULL, 'This is the sixth message in TestRoom1, sent by TestUser2.', 1, 2, ?)
                '''

    c.execute(sql,[base_time, base_time + 10, base_time + 20, base_time + 30, base_time + 40, base_time + 50])

    sql =  '''INSERT INTO Message VALUES 
                        (NULL, 'This is the first message in TestRoom2, sent by TestUser2.', 2, 2, ?),
                        (NULL, 'This is the second message in TestRoom2, sent by TestUser3.', 2, 3, ?),
                        (NULL, 'This is the third message in TestRoom2, sent by TestUser4.', 2, 4, ?),
                        (NULL, 'This is the fourth message in TestRoom2, sent by TestUser3.', 2, 3, ?),
                        (NULL, 'This is the fifth message in TestRoom2, sent by TestUser4.', 2, 4, ?),
                        (NULL, 'This is the sixth message in TestRoom2, sent by TestUser2. It has an attachment (a picture of Will Smith).', 2, 2, ?)
                    '''

    c.execute(sql,[base_time, base_time + 10, base_time + 20, base_time + 30, base_time + 40, base_time + 50])

    sql =  '''INSERT INTO Message VALUES 
                        (NULL, 'This is the first message in TestRoom3, sent by TestUser1.', 3, 1, ?),
                        (NULL, 'This is the second message in TestRoom3, sent by TestUser2. It has an attachment (a picture of Jennifer Anniston).', 3, 2, ?),
                        (NULL, 'This is the third message in TestRoom3, sent by TestUser3. It also has an attachment, this time a picture of Gary Barlow.', 3, 3, ?),
                        (NULL, 'This is the fourth message in TestRoom3, sent by TestUser4.', 3, 4, ?),
                        (NULL, 'This is the fifth message in TestRoom3, sent by TestUser5.', 3, 5, ?),
                        (NULL, 'This is the sixth message in TestRoom3, sent by TestUser4.', 3, 4, ?),
                        (NULL, 'This is the seventh message in TestRoom3, sent by TestUser2.', 3, 2, ?),
                        (NULL, 'This is the eighth message in TestRoom3, sent by TestUser3.', 3, 3, ?),
                        (NULL, 'This is the ninth message in TestRoom3, sent by TestUser1.', 3, 1, ?)
                    '''

    c.execute(sql,[base_time, base_time + 10, base_time + 20, base_time + 30, base_time + 40, base_time + 50,
                   base_time + 60, base_time + 70, base_time + 80])

    db.commit()
    print("Success: Added test messages")


def add_attachments(db:sqlite3.Connection):

    c = db.cursor()

    sql = '''INSERT INTO Attachment VALUES 
                (NULL, 1, 'donald.png'),
                (NULL, 1, 'gary.png'),
                (NULL, 12, 'will.png'),
                (NULL, 14, 'jen.png'),
                (NULL, 15, 'gary.png')
                
            '''

    c.execute(sql)

    db.commit()


class SetupTestData(unittest.TestCase):

    def test_setup_initialise_database(self):
        init_db.init_db(db)
        add_test_users(db)
        add_test_chatrooms(db)
        add_chatroom_members(db)
        add_messages(db)
        add_attachments(db)


class TestUser(unittest.TestCase):

    def test_constructor_existing_user(self):
        # Instantiate a User object from user id 1 in the test database
        u = chatter_classes.User(1, db)
        # Assert that the properties for the instantiated User matches our test data
        self.assertEqual(u.username,"TestUser1")
        self.assertFalse(u.is_admin)
        self.assertTrue(u.is_active)

    def test_constructor_user_not_found(self):
        # Assert that an attempt to instantiate a User with id -1 will raise a UserNotFound exception
        # Note that the arguments for the constructor need to be passed as additional arguments to
        # assertRaises()
        self.assertRaises(chatter_classes.UserNotFoundError, chatter_classes.User, -1, db)

    def test_add_new_user(self):
        new_user = chatter_classes.User.add("NewTestUser", "pass123", db)
        self.assertIsInstance(new_user, chatter_classes.User)
        self.assertEqual(new_user.username, "NewTestUser")

    def test_new_username_unique(self):
        new_user = chatter_classes.User.add("UniqueTestUser", "unique123",db)
        self.assertRaises(chatter_classes.UserActionError, chatter_classes.User.add, "UniqueTestUser", "unique123", db)

    def test_delete_user_by_admin(self):
        u = chatter_classes.User(5, db)

        # As well as deleting the user, we need to ensure that their messages have been reassigned
        users_messages = chatter_classes.Message.get_messages_for_user(5, None, db)
        users_message_ids = [message.messageid for message in users_messages]

        u.delete(chatter_classes.User(6, db))  # User 6 is TestAdmin

        for message_id in users_message_ids:
            m = chatter_classes.Message(message_id, db)
            self.assertEqual(m.senderid, 0)  # assert message's sender Id updated to DeletedUser 0

        # Check it's no longer possible to instantiate the deleted user
        self.assertRaises(chatter_classes.UserNotFoundError, chatter_classes.User, 5, db)

    def test_delete_user_non_admin_fails(self):
        u = chatter_classes.User(4, db)
        self.assertRaises(chatter_classes.UserPermissionError, u.delete, chatter_classes.User(1, db))  # User 1 is a standard user

    def test_update_user(self):
        u = chatter_classes.User(1, db)
        u.update(username="UpdatedUser", password="updatedpass", last_login_ts=0, active=False, admin=True)

        v = chatter_classes.User(1, db)
        self.assertEqual(v.username, "UpdatedUser")
        self.assertEqual(v.last_login_ts, datetime.datetime.fromtimestamp(0))
        self.assertTrue(v.is_admin)
        self.assertFalse(v.is_active)

        # Restore Test User 1's details
        u.update(username="TestUser1", password="pass1234", last_login_ts=0, active=True, admin=False)

    def test_user_send_message(self):

        cr = chatter_classes.Chatroom(1, db)
        message_count = cr.get_message_count()

        u = chatter_classes.User(1,db)
        u.send_message("Sent by test_user_send_message()", cr.chatroomid)

        self.assertEqual(message_count + 1, chatter_classes.Chatroom(1, db).get_message_count())

    def test_user_memberships(self):

        u = chatter_classes.User(2, db)
        rooms = u.get_chatrooms()
        self.assertEqual(2, len(rooms['owner']))
        self.assertEqual(1, len(rooms['member']))

    def test_user_json(self):
        u = chatter_classes.User(1, db)
        js = u.json
        print(js)
        self.assertNotEqual(0, len(js))


class TestChatroom(unittest.TestCase):

    def test_constructor_existing_chatroom(self):
        cr = chatter_classes.Chatroom(1, db)
        self.assertEqual(cr.name, "TestRoom1")

    def test_constructor_chatroom_not_found(self):
        self.assertRaises(chatter_classes.ChatroomNotFoundError, chatter_classes.Chatroom, -1, db)

    def test_add_chatroom(self):
        cr = chatter_classes.Chatroom.add("UnitTestChatroom", "Created by TestChatroom.test_add_chatroom", db)
        self.assertIsInstance(cr, chatter_classes.Chatroom)
        self.assertEqual(cr.name, "UnitTestChatroom")
        self.assertEqual(cr.description, "Created by TestChatroom.test_add_chatroom")
        acceptable_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        for c in cr.joincode:
            self.assertIn(c, acceptable_chars)
        self.assertEqual(len(cr.joincode), 6)

    def test_delete_chatroom(self):
        cr = chatter_classes.Chatroom.add("UnitTestChatroomForDeletion", "Created by TestChatroom.test_delete_chatroom", db)
        cr_id = cr.chatroomid
        cr.delete()
        self.assertRaises(chatter_classes.ChatroomNotFoundError, chatter_classes.Chatroom, cr_id, db)

    def test_update_chatroom(self):

        # Create a chatroom for testing
        cr = chatter_classes.Chatroom.add("UnitTestChatroomForUpdate", "Created by TestChatroom.test_update_chatroom", db)
        cr_id = cr.chatroomid
        cr.update_join_code()
        cr.update(name="UnitTestChatroomForUpdateB", description="Created by TestChatroom.test_update_chatroomB")

        # Instantiate a second instance of the same chatroom and check that its properties match those of the updated
        # one
        crB = chatter_classes.Chatroom(cr_id, db)
        self.assertEqual(cr.name, crB.name)
        self.assertEqual(cr.description, crB.description)
        self.assertEqual(cr.joincode, crB.joincode)

        # Delete chatrooms now that we have finished with them
        cr.delete()
        crB.delete()

    def test_get_all_members(self):

        cr = chatter_classes.Chatroom(1, db)
        members = cr.get_all_members()
        self.assertEqual(2, len(members))
        self.assertEqual(2, members[0].userid)
        self.assertEqual(3, members[1].userid)

    def test_get_all_owners(self):

        cr = chatter_classes.Chatroom(1, db)
        owners = cr.get_all_owners()
        self.assertEqual(1, len(owners))
        self.assertEqual(1, owners[0].userid)

    def test_check_user_is_member(self):

        cr = chatter_classes.Chatroom(2, db)
        u1 = chatter_classes.User(3, db)
        u2 = chatter_classes.User(4, db)
        self.assertTrue(cr.user_is_member(u1))
        self.assertTrue(cr.user_is_member(u2))

    def test_check_user_is_owner(self):

        cr = chatter_classes.Chatroom(2, db)
        u = chatter_classes.User(2, db)

        self.assertTrue(cr.user_is_owner(u))

    def test_add_message_for_chatroom(self):

        cr = chatter_classes.Chatroom(2, db)
        message_count = cr.get_message_count()
        cr.add_message("Added by test_add_message_for_chatroom()", cr.get_all_owners()[0].userid)
        self.assertEqual(message_count + 1, chatter_classes.Chatroom(2, db).get_message_count())

    def test_get_all_messages(self):
        cr = chatter_classes.Chatroom(3, db)
        messages = cr.get_messages()
        self.assertEqual(9, len(messages))

    def test_get_message_count(self):
        cr = chatter_classes.Chatroom(3, db)
        self.assertEqual(9, cr.get_message_count())

    def test_get_all_messages_since(self):
        cr = chatter_classes.Chatroom(1, db)
        start_time = datetime.datetime.now()

        message_content = "Added by test_get_all_message_since()"

        print("Waiting two seconds before adding checking for recent messages")
        time.sleep(2)

        chatter_classes.Message.add(message_content, cr.chatroomid,
                                    cr.get_all_owners()[0].userid, db)

        messages = cr.get_messages(start_time)

        self.assertEqual(1, len(messages))
        self.assertEqual(message_content, messages[0].content)

    def test_get_message_count_since(self):

        cr = chatter_classes.Chatroom(1, db)
        now = datetime.datetime.now()

        message_content = "Added by test_get_message_count_since()"

        print("Waiting two seconds before adding and checking for recent messages")

        time.sleep(2)

        chatter_classes.Message.add(message_content, cr.chatroomid,
                                    cr.get_all_owners()[0].userid, db)

        message_count = cr.get_message_count(now)

        self.assertEqual(1, message_count)

    def test_chatroom_json(self):
        c = chatter_classes.Chatroom(1, db)
        js = c.json
        print(js)
        self.assertNotEqual(0, len(js))

    def test_chatroom_json_with_messages(self):
        c = chatter_classes.Chatroom(1, db)
        js = c.json_with_messages
        print(js)
        self.assertNotEqual(0, len(js))


class TestMessage(unittest.TestCase):

    # TODO: Add test for updating message
    # TODO: Add test for retrieving all messages for a particular user
    # TODO: Add test for retrieving all messages for a particular chatroom

    def test_contructor_existing_message(self):
        m = chatter_classes.Message(1, db)
        self.assertEqual(m.content, "This is the first message in TestRoom1, sent by TestUser1. It has two attachments (a picture of Donald Trump and another of Gary Barlow).")
        self.assertEqual(m.chatroom.name, chatter_classes.Chatroom(1,db).name)
        self.assertEqual(m.sender.username, chatter_classes.User(1,db).username)
        self.assertEqual(m.timestamp.year, 2021)

    def test_constructor_message_not_found(self):
        self.assertRaises(chatter_classes.MessageNotFoundError, chatter_classes.Message, -1, db)

    def test_add_new_message(self):

        text = "This is a test message generated in the unit test test_add_new_message()"

        message = chatter_classes.Message.add(text, 1, 1, db)

        self.assertIsInstance(message, chatter_classes.Message)
        self.assertEqual(message.content, text)
        self.assertEqual(message.sender.username, chatter_classes.User(1, db).username)
        self.assertEqual(message.chatroom.name, chatter_classes.Chatroom(1, db).name)

    def test_delete_message(self):
        m = chatter_classes.Message.add("This is a message to delete", 1, 1, db)
        m_id = m.messageid
        m.delete()
        self.assertRaises(chatter_classes.MessageNotFoundError, chatter_classes.Message, m_id, db)

    def test_sender(self):
        m = chatter_classes.Message(1, db)
        self.assertEqual(1, m.sender.userid)

    def test_chatroom(self):
        m = chatter_classes.Message(7, db)
        self.assertEqual(2, m.chatroom.chatroomid)

    def test_message_json(self):
        m = chatter_classes.Message(1, db)
        js = m.json
        print(js)
        self.assertNotEqual(0, len(js))


class TestAttachment(unittest.TestCase):

    def test_constructor_existing_attachment(self):
        a = chatter_classes.Attachment(1,db)
        self.assertEqual(a.filepath, "donald.png")
        self.assertEqual(a.message.messageid, chatter_classes.Message(1, db).messageid)

    def test_constructor_attachment_not_found(self):
        self.assertRaises(chatter_classes.AttachmentNotFoundError, chatter_classes.Attachment, -1, db)

    def test_attachment_json(self):
        a = chatter_classes.Attachment(1, db)
        js = a.json
        print(js)
        self.assertNotEqual(0, len(js))

    # TODO: Add test for deleting attachment (including files)

    # TODO: Add test for adding an attachment


if __name__ == '__main__':

    unittest.main()

