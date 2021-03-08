import init_db, sqlite3, time, unittest, chatter_classes

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

    # Initialise test database and add required data
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


class TestChatroom(unittest.TestCase):

    def test_constructor_existing_chatroom(self):
        cr = chatter_classes.Chatroom(1, db)
        self.assertEqual(cr.name, "TestRoom1")

    def test_constructor_chatroom_not_found(self):
        self.assertRaises(chatter_classes.ChatroomNotFoundError, chatter_classes.Chatroom, -1, db)


class TestMessage(unittest.TestCase):

    def test_contructor_existing_message(self):
        m = chatter_classes.Message(1, db)
        self.assertEqual(m.content, "This is the first message in TestRoom1, sent by TestUser1. It has two attachments (a picture of Donald Trump and another of Gary Barlow).")
        self.assertEqual(m.chatroom.name, chatter_classes.Chatroom(1,db).name)
        self.assertEqual(m.sender.username, chatter_classes.User(1,db).username)
        self.assertEqual(m.timestamp.year, 2021)

    def test_constructor_message_not_found(self):
        self.assertRaises(chatter_classes.MessageNotFoundError, chatter_classes.Message, -1, db)


class TestAttachment(unittest.TestCase):

    def test_constructor_existing_attachment(self):
        a = chatter_classes.Attachment(1,db)
        self.assertEqual(a.filepath, "donald.png")
        self.assertEqual(a.message.messageid, chatter_classes.Message(1, db).messageid)

    def test_constructor_attachment_not_found(self):
        self.assertRaises(chatter_classes.AttachmentNotFoundError, chatter_classes.Attachment, -1, db)

if __name__ == '__main__':


    # Initialise test database and add required data
    init_db.init_db(db)
    add_test_users(db)
    add_test_chatrooms(db)
    add_chatroom_members(db)
    add_messages(db)
    add_attachments(db)


    unittest.main()

