import sqlite3, abc, datetime, random, os, json

DB_PATH = 'test.db'

def get_db():
    db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db


class ChatterDB(abc.ABC):

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def delete(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def add():
        pass


class UserNotFoundError(Exception):
    pass


class UserPermissionError(Exception):
    pass


class UserActionError(Exception):
    pass


class UserAuthenticationError(Exception):
    pass


class User(ChatterDB):

    def __init__(self, userid, db:sqlite3.Connection):

        self.__db = db
        self.__userid = userid

        c = self.__db.cursor()

        user_data = c.execute("SELECT username, last_login_ts, admin, active FROM User WHERE userid=?",
                            [self.__userid]).fetchone()

        if user_data:
            self.__username = user_data['username']
            self.__last_login_ts = user_data['last_login_ts']
            self.__admin = True if user_data['admin'] == 1 else False
            self.__active = True if user_data['active'] == 1 else False

        else:
            raise UserNotFoundError(f"ERROR: No user found with userid {userid}.")

    @property
    def userid(self):
        return self.__userid

    @property
    def username(self):
        return self.__username

    @property
    def is_admin(self):
        return self.__admin

    @property
    def is_active(self):
        return self.__active

    @property
    def last_login_ts(self):
        # Rather than a meaningless integer, provide a useful datetime object
        return datetime.datetime.fromtimestamp(self.__last_login_ts)

    @property
    def json(self):
        return self.__encode_json()

    def delete(self, active_user):
        # Do we have permission to delete? Is the active user either the self or an admin?
        if active_user.userid == self.__userid or active_user.is_admin:
            # TODO: Check the user isn't the only owner of a chatroom before deleting them

            # Assuming we can delete, we need to update all messages that the user has sent to be senderid = 0
            users_messsages = Message.get_messages_for_user(self.__userid, None, self.__db)

            try:
                c = self.__db.cursor()
                c.execute("DELETE FROM User WHERE userid=?", [self.__userid])

                for m in users_messsages:
                    # update senderid to 0
                    m.update(senderid=0)

                self.__db.commit()

            except sqlite3.Error as e:
                self.__db.rollback()
                for m in users_messsages:
                    # update senderid to 0
                    m.update(senderid=self.__userid)
                raise UserActionError(f"ERROR: Cannot delete userid {self.__userid}. Details:\n{e}")

        else:
            # raise error
            raise UserPermissionError(f"Active user (userid: {active_user.userid}) does not have permission "
                                      f"to delete userid {self.__userid}.")

    def update(self, username=None, password=None, last_login_ts=None, admin=None, active=None):
        try:
            c = self.__db.cursor()

            if username is not None:
                # is the username unqiue?

                existing_username = c.execute("SELECT userid FROM User WHERE username=?", [username]).fetchone()

                if existing_username:
                    raise UserActionError(f"User already exists with username '{username}'.")

                c.execute("UPDATE User SET username=? WHERE userid=? ", [ username, self.__userid])
                self.__username = username

            if password is not None:
                # TODO: Add password length/criteria validation and hashing
                c.execute("UPDATE User SET password=? WHERE userid=? ", [password, self.__userid])

            if last_login_ts is not None:
                c.execute("UPDATE User SET last_login_ts=? WHERE userid=? ", [last_login_ts, self.__userid])
                self.__last_login_ts = last_login_ts

            if admin is not None:
                c.execute("UPDATE User SET admin=? WHERE userid=?", [1 if admin else 0, self.__userid])
                self.__admin = admin

            if active is not None:
                c.execute("UPDATE User SET active=? WHERE userid=? ", [1 if active else 0, self.__userid])
                self.__active = active

            self.__db.commit()

        except sqlite3.Error as e:
            self.__db.rollback()
            print(f"ERROR: Exception raised when updating user {self.__userid}. Details\n{e}")
            raise e

    @staticmethod
    def add(username, password, db:sqlite3.Connection):

        try:
            c = db.cursor()
            # Check username is unique
            existing_username = c.execute("SELECT userid FROM User WHERE username=?", [username]).fetchone()

            if existing_username:
                raise UserActionError(f"User already exists with username '{username}'.")

            # Insert new user
            c.execute("INSERT INTO User (username, password, last_login_ts) VALUES (?, ?, ?)",
                      (username, password, 0))
            new_user_id = c.lastrowid
            db.commit()

            return User(new_user_id, db)

        except sqlite3.Error as e:
            db.rollback()
            print(f"ERROR: Exception raised when adding user {username}.\n"
                  f"Database rolled back to last commit. Details:\n{e}")

    def send_message(self, content, chatroomid):
        return Message.add(content, chatroomid, self.__userid, self.__db)

    def get_chatrooms(self):
        return Chatroom.get_chatrooms_for_user(self.__userid, self.__db)

    @staticmethod
    def authenticate(username, password, db:sqlite3.Connection):

        try:
            c = db.cursor()
            user_row = c.execute("SELECT userid FROM User WHERE username=? AND password=? AND active=1",
                                 [username, password]).fetchone()
            if user_row:
                return User(user_row['userid'], db)

            else:
                raise UserAuthenticationError

        except sqlite3.Error as e:
            print(f"ERROR: Exception raised when attempting to authenticate a user. Details:\n{e}")
            raise e

    def __encode_json(self):

        chatrooms = self.get_chatrooms()
        cr_owner_ids = []
        cr_member_ids = []

        for cr in chatrooms['owner']:
            cr_owner_ids.append(cr.chatroomid)

        for cr in chatrooms['member']:
            cr_member_ids.append(cr.chatroomid)

        return json.dumps({
            'userid':self.__userid,
            'username':self.__username,
            'admin':self.__admin,
            'active':self.__active,
            'last_login_ts': self.__last_login_ts,
            'chatrooms': {'owner': cr_owner_ids, 'member': cr_member_ids}
        }, sort_keys=False, indent=4)


class ChatroomNotFoundError(Exception):
    pass


class ChatroomActionError(Exception):
    pass


class Chatroom(ChatterDB):

    def __init__(self, chatroomid, db: sqlite3.Connection):

        self.__db = db
        self.__chatroomid = chatroomid

        c = self.__db.cursor()

        chatroom_data = c.execute("SELECT name, description, joincode FROM Chatroom WHERE chatroomid=?",
                              [self.__chatroomid]).fetchone()

        if chatroom_data:
            self.__name = chatroom_data['name']
            self.__description = chatroom_data['description']
            self.__joincode = chatroom_data['joincode']

        else:
            raise ChatroomNotFoundError(f"ERROR: No chatroom found with chatroomid {chatroomid}.")

    @property
    def chatroomid(self):
        return self.__chatroomid

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value
        self.update(description=value)

    @property
    def joincode(self):
        return self.__joincode

    @property
    def json(self):
        return self.__encode_json()

    @property
    def json_with_messages(self):
        return self.__encode_json_with_messages()

    @property
    def messages(self):
        return self.get_messages()

    @staticmethod
    def __get_new_joincode():

        new_joincode = ""

        chars = [x for x in range(65, 91)] + [x for x in range(97, 123)] + [x for x in range(48, 58)]

        for x in range(6):
            new_joincode += chr(random.choice(chars))

        return new_joincode

    def update_join_code(self):
        self.__joincode = self.__get_new_joincode()
        self.update(joincode=self.__joincode)

    def delete(self):
        try:

            # Delete all messages associated with the chatroom
            messages_to_delete = Message.get_msesages_for_chatroom(self.__chatroomid, None, self.__db)

            c = self.__db.cursor()

            c.execute("DELETE FROM Chatroom WHERE chatroomid=?", [self.__chatroomid])

            # Hold off on deletings messages until the chatroom has been successfully deleted.
            for m in messages_to_delete:
                m.delete()

            self.__db.commit()

        except sqlite3.Error as e:
            self.__db.rollback()
            print(f"ERROR: Exception raised when deleting chatroomid {self.__chatroomid}. Details:\n{e}")
            raise e

    @staticmethod
    def __check_name_is_unique(name, db:sqlite3.Connection):

        # Check chatroom name is unique
        c = db.cursor()
        if c.execute("SELECT chatroomid FROM Chatroom WHERE name=?", [name]).fetchone():
            raise ChatroomActionError(f"Chatroom name {name} already in use.")

    @staticmethod
    def __check_join_code_is_unique(joincode, db:sqlite3.Connection):
        c = db.cursor()
        if c.execute("SELECT chatroomid FROM Chatroom WHERE joincode=?", [joincode]).fetchone():
            raise ChatroomActionError(f"Chatroom joincode {joincode} already in use.")

    def update(self, name=None, description=None, joincode=None):

        try:

            c = self.__db.cursor()

            if name is not None:

                self.__check_name_is_unique(name, self.__db)
                c.execute("UPDATE Chatroom SET name=? WHERE chatroomid=?", [name, self.__chatroomid])
                self.__name = name

            if description is not None:
                c.execute("UPDATE Chatroom SET description=? WHERE chatroomid=?", [description, self.__chatroomid])
                self.__description = description

            if joincode is not None:

                self.__check_join_code_is_unique(joincode, self.__db)
                c.execute("UPDATE Chatroom SET joincode=? WHERE chatroomid=?", [joincode, self.__chatroomid])
                self.__joincode = joincode

            self.__db.commit()

        except sqlite3.Error as e:
            self.__db.rollback()
            print(f"ERROR: Exception raised when updating chatroomid {self.__chatroomid}. Details:\n{e}")

        except ChatroomActionError as e:
            self.__db.rollback()
            print(f"ERROR: Exception raised when updating chatroomid {self.__chatroomid}. Details:\n{e}")
            raise e

    @staticmethod
    def add(name, descrption, db:sqlite3.Connection):

        try:

            c = db.cursor()

            Chatroom.__check_name_is_unique(name, db)

            while True:
                try:
                    new_join_code = Chatroom.__get_new_joincode()
                    Chatroom.__check_join_code_is_unique(new_join_code, db)
                    break
                except ChatroomActionError:
                    print("WARNING: new_join_code in use. Generating another.")

            c.execute("INSERT INTO Chatroom (name, description, joincode) VALUES (?, ?, ?)",
                      [name, descrption, Chatroom.__get_new_joincode()])

            db.commit()

            return Chatroom(c.lastrowid, db)

        except sqlite3.Error as e:

            db.rollback()
            print(f"ERROR: Unable to add chatroom with name {name}.Details:\n{e}")

    def get_all_members(self):

        c = self.__db.cursor()
        member_rows = c.execute("SELECT userid FROM ChatroomMember WHERE chatroomid=? AND owner=0",
                                [self.__chatroomid]).fetchall()

        # Return a list of User objects for all Users that are members of this chatroom
        return [User(m['userid'], self.__db) for m in member_rows]

    def get_all_owners(self):

        c = self.__db.cursor()
        member_rows = c.execute("SELECT userid FROM ChatroomMember WHERE chatroomid=? AND owner=1",
                                [self.__chatroomid]).fetchall()

        # Return a list of User objects for all Users that are members of this chatroom
        return [User(m['userid'], self.__db) for m in member_rows]

    def user_is_owner(self, u:User):

        c = self.__db.cursor()
        user_row = c.execute("SELECT userid FROM ChatroomMember WHERE chatroomid=? AND userid=? AND owner=1",
                             [self.__chatroomid, u.userid]).fetchone()

        return True if user_row else False

    def user_is_member(self, u: User):

        c = self.__db.cursor()
        user_row = c.execute("SELECT userid FROM ChatroomMember WHERE chatroomid=? AND userid=? AND owner=0",
                             [self.__chatroomid, u.userid]).fetchone()

        return True if user_row else False

    def get_messages(self, since=None):
        return Message.get_msesages_for_chatroom(self.__chatroomid, since, self.__db)

    def get_message_count(self, since=None):
        return Message.get_message_count_for_chatroom(self.__chatroomid, since, self.__db)

    def add_message(self, content, senderid):
        return Message.add(content, self.__chatroomid, senderid, self.__db)

    @staticmethod
    def get_chatrooms_for_user(userid, db: sqlite3.Connection) -> dict:
        """
        Finds all chatrooms for a particular user, returning them in a dictionary containing a list of chatrooms where
        the user is an owner and another list where they are members.
        :param u: The user for whom chatrooms are to be found
        :param db: Database connection
        :return: A dictionary with 'owner' and 'member' keys, each paired with a list of Chatroom objects
        """

        rooms = {'owner': [], 'member': []}

        c = db.cursor()

        rows = c.execute("SELECT chatroomid, owner FROM ChatroomMember WHERE userid=?", [userid]).fetchall()

        for r in rows:
            if bool(r['owner']):
                rooms['owner'].append(Chatroom(r['chatroomid'], db))
            else:
                rooms['member'].append(Chatroom(r['chatroomid'], db))

        return rooms

    def __encode_json(self):

        message_ids = [m.messageid for m in self.get_messages()]
        owner_ids = [o.userid for o in self.get_all_owners()]
        member_ids = [m.userid for m in self.get_all_members()]

        return json.dumps({
            'chatroomid': self.__chatroomid,
            'name': self.__name,
            'description': self.__description,
            'joincode': self.__joincode,
            'messages': message_ids,
            'owners': owner_ids,
            'members': member_ids
        }, sort_keys=False, indent=4)

    def __encode_json_with_messages(self):

        messages = [m.json for m in self.get_messages()]

        owner_ids = [o.userid for o in self.get_all_owners()]
        member_ids = [m.userid for m in self.get_all_members()]

        return json.dumps({
            'chatroomid': self.__chatroomid,
            'name': self.__name,
            'description': self.__description,
            'joincode': self.__joincode,
            'messages': messages,
            'owners': owner_ids,
            'members': member_ids
        }, sort_keys=False, indent=4)

class MessageNotFoundError(Exception):
    pass


class Message(ChatterDB):

    def __init__(self, messageid, db: sqlite3.Connection):

        self.__db = db
        self.__messageid = messageid

        c = self.__db.cursor()

        message_data = c.execute("SELECT content, chatroomid, senderid, timestamp FROM Message WHERE messageid=?",
                              [self.__messageid]).fetchone()

        if message_data:
            self.__content = message_data['content']
            self.__chatroomid = int(message_data['chatroomid'])
            self.__senderid = int(message_data['senderid'])
            self.__timestamp = message_data['timestamp']

        else:
            raise MessageNotFoundError(f"ERROR: No message found with mesageid {messageid}.")

    @property
    def messageid(self):
        return self.__messageid

    @property
    def content(self):
        return self.__content

    @property
    def chatroomid(self):
        return self.__chatroomid

    @property
    def chatroom(self):
        return Chatroom(self.__chatroomid, self.__db)

    @property
    def senderid(self):
        return self.__senderid

    @property
    def sender(self):
        return User(self.__senderid, self.__db)

    @property
    def timestamp(self):
        return datetime.datetime.fromtimestamp(self.__timestamp)

    @property
    def attachments(self):
        return Attachment.get_all_attachments_for_message(self.__messageid, self.__db)

    @property
    def json(self):
        return self.__encode_json()

    def delete(self):

        try:

            c = self.__db.cursor()

            # Get all attachments for message and delete them also (files as well as entries in database)
            attachments = Attachment.get_all_attachments_for_message(self.__messageid, self.__db)
            for a in attachments:
                a.delete()

            c.execute("DELETE FROM Message WHERE messageid=?", [self.__messageid])

            self.__db.commit()

        except sqlite3.Error as e:
            self.__db.rollback()
            print(f"ERROR: Database exception raised when deleting messageid {self.__messageid}. Details:\n{e}")
            raise e

    def update(self, content=None, chatroomid=None, senderid=None, timestamp:datetime.datetime=None):

        try:
            c = self.__db.cursor()

            if content is not None:
                c.execute("UPDATE Message SET content=? WHERE messageid=?", [content, self.__messageid])
                self.__content = content

            if chatroomid is not None:
                c.execute("UPDATE Message SET chatroomid=? WHERE messageid=?", [chatroomid, self.__messageid])
                self.__chatroomid = chatroomid

            if senderid is not None:
                c.execute("UPDATE Message SET senderid=? WHERE messageid=?", [senderid, self.__messageid])
                self.__senderid = senderid

            if timestamp is not None:
                c.execute("UPDATE Message SET timestamp=? WHERE messageid=?", [timestamp.timestamp(), self.__messageid])
                self.__timestamp = timestamp

            self.__db.commit()

        except sqlite3.Error as e:
            self.__db.rollback()
            print(f"ERROR: Exception raised when updating messageid {self.__messageid}.\n"
                  f"Database rolled back to last commit. Details:\n{e}")

    def add_attachment(self, filepath):
        return Attachment.add(self.__messageid, filepath, self.__db)

    @staticmethod
    def add(content, chatroomid, senderid, db:sqlite3.Connection):
        try:
            c = db.cursor()
            ts = int(round(datetime.datetime.now().timestamp(),0))
            #          (content, chatroomid, senderid, int(round(datetime.datetime.now().timestamp(), 0))))
            c.execute("INSERT INTO Message (content, chatroomid, senderid, timestamp) VALUES (?, ?, ?, ?)",
                      (content, chatroomid, senderid, ts))
            new_messageid = c.lastrowid
            db.commit()

            return Message(new_messageid, db)

        except sqlite3.Error as e:
            db.rollback()
            print(f"ERROR: Exception raised when adding message.\n"
                  f"Database rolled back to last commit. Details:\n{e}")
            raise e

    @staticmethod
    def get_messages_for_user(userid, since:datetime.datetime, db:sqlite3.Connection):

        if not since:
            since = datetime.datetime(2010,1,1)

        c = db.cursor()

        message_rows = c.execute("SELECT messageid FROM Message WHERE senderid = ? AND timestamp > ?",
                                 [userid, since.timestamp()]).fetchall()

        messages_to_return = []

        for row in message_rows:

            messages_to_return.append(Message(int(row['messageid']), db))

        return messages_to_return

    @staticmethod
    def get_msesages_for_chatroom(chatroomid, since:datetime.datetime, db:sqlite3.Connection):

        if not since:
            since = datetime.datetime(2010,1,1)

        try:
            c = db.cursor()

            ts = int(round(since.timestamp(), 0))

            message_rows = c.execute("SELECT messageid FROM Message WHERE chatroomid=? AND timestamp>?",
                                     [chatroomid, ts]).fetchall()

            return [Message(int(row['messageid']), db) for row in message_rows]

        except sqlite3.Error as e:
            print(f"ERROR: Unable to retrieve messages for chatroomid {chatroomid}. Details\n{e}")
            raise e

    @staticmethod
    def get_message_count_for_chatroom(chatroomid, since:datetime.datetime, db:sqlite3.Connection):

        if not since:
            since = datetime.datetime(2010,1,1)

        try:
            c = db.cursor()

            ts = int(round(since.timestamp(), 0))

            row = c.execute("SELECT count(messageid) as message_count FROM Message WHERE chatroomid=? AND timestamp>?",
                                     [chatroomid, ts]).fetchone()

            return row['message_count']

        except sqlite3.Error as e:
            print(f"ERROR: Unable to retrieve message count for chatroomid {chatroomid}. Details\n{e}")
            raise e

    def __encode_json(self):

        attachments = [a.json for a in self.attachments]

        return json.dumps(
            {
            'messageid': self.__messageid,
            'content': self.__content,
            'chatroomid': self.__chatroomid,
            'senderid': self.__senderid,
            'timestamp': self.__timestamp,
            'attachments': attachments

        }, sort_keys=False, indent=4)


class AttachmentNotFoundError(Exception):
    pass


class Attachment(ChatterDB):

    def __init__(self, attachmentid, db: sqlite3.Connection):

        self.__db = db
        self.__attachmentid = attachmentid

        c = self.__db.cursor()

        attachment_data = c.execute("SELECT messageid, filepath FROM Attachment WHERE attachmentid=?",
                              [self.__attachmentid]).fetchone()

        if attachment_data:
            self.__messageid = attachment_data['messageid']
            self.__filepath = attachment_data['filepath']

        else:
            raise AttachmentNotFoundError(f"ERROR: No attachment found with attachment {attachmentid}.")

    @property
    def attachmentid(self):
        return self.__attachmentid

    @property
    def filepath(self):
        # TODO: Could update this to include the static path once it is known
        return self.__filepath

    @property
    def messageid(self):
        return self.__messageid

    @property
    def message(self):
        return Message(self.__messageid, self.__db)

    @property
    def json(self):
        return self.__encode_json()

    def delete(self):
        # First remove the associated files
        try:
            os.remove(self.filepath)

        except FileNotFoundError:
            print(f"WARNING: Could not remove {self.__filepath} as the file could not be found. Proceeding with"
                  f"deleting attachmentid {self.__attachmentid}.")

        # Next remove data from database
        try:
            c = self.__db.cursor()
            c.execute("DELETE FROM Attachment WHERE attachmentid=?", [self.__attachmentid])
            self.__db.commit()

        except sqlite3.Error as e:
            self.__db.rollback()
            print(f"ERROR: Exception raised when deleting attachmentid {self.__attachmentid}. Details:\n{e}")
            raise e

    def update(self, filepath):
        # The only attribute that can be updated is the filepath for the attachment

        try:
            # Test if file exists
            if not os.path.exists(filepath):
                raise FileNotFoundError

            c = self.__db.cursor()
            c.execute("UPDATE Attachment SET filepath=? WHERE attachmentid=?", [self.__filepath, self.__attachmentid])
            self.__db.commit()

        except sqlite3.Error as e:
            self.__db.rollback()
            print(f"ERROR: Exception raised when updating attachmentid {self.__attachmentid}. Details:\n{e}")
            raise e

        except FileNotFoundError:
            print(f"ERROR: file {filepath} could not be found. Aborting updated of attachmentid {self.__attachmentid}.")

    @staticmethod
    def add(messageid, filepath, db:sqlite3.Connection):
        # TODO: Add ability to receive any file, copy it to the correct path and set the correct path location for this
        #  Attachment object
        try:
            c = db.cursor()
            c.execute("INSERT INTO Attachment (messageid, filepath) VALUES (?, ?)", [messageid, filepath])
            new_attachmentid = c.lastrowid
            db.commit()
            return Attachment(new_attachmentid, db)

        except sqlite3.Error as e:
            db.rollback()
            print(f"ERROR: Exception raised when inserting a new attachment. Details:\n{e}")
            raise e

    @staticmethod
    def get_all_attachments_for_message(messsageid, db:sqlite3.Connection):

        try:
            c = db.cursor()

            attachment_rows = c.execute("SELECT attachmentid FROM Attachment WHERE messageid=?", [messsageid]).fetchall()

            return [Attachment(int(row['attachmentid']), db) for row in attachment_rows]

        except sqlite3.Error as e:
            print(f"ERROR: Unable to retrieve attachments for messsageid {messsageid}. Details\n{e}")
            raise e

    def __encode_json(self):

        return json.dumps({
            'attachmentid': self.__attachmentid,
            'filepath': self.__filepath,
            'messageid': self.__messageid,

        }, sort_keys=False, indent=4)

if __name__ == "__main__":

    db = get_db()
