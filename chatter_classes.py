import sqlite3, abc, datetime

DB_PATH = 'chatter_db.db'

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

    def delete(self, active_user):
        # Do we have permission to delete? Is the active user either the self or an admin?
        if active_user.userid == self.__userid or active_user.is_admin:
            # Assuming we can delete, we need to update all messages that the user has sent to be senderid = 0
            users_messsages = Message.get_messages_from_user(self.__userid, self.__db)
            for m in users_messsages:
                # update senderid to 0
                m.update(senderid=0)

            try:
                c = self.__db.cursor()
                c.execute("DELETE FROM User WHERE userid=?", [self.__userid])
                self.__db.commit()
            except sqlite3.Error as e:
                raise UserActionError(f"ERROR: Cannot delete userid {self.__userid}. Details:\n{e}")

        else:
            # raise error
            raise UserPermissionError(f"Active user (userid: {active_user.userid}) does not have permission "
                                      f"to delete userid {self.__userid}.")

    def update(self):
        # TODO: Add User.update()
        pass

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


class ChatroomNotFoundError(Exception):
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
        # TODO: Will need to call update method to update description in database
        # self.__update(description=value)

    @property
    def joincode(self):
        return self.__joincode

    def delete(self):
        # TODO: Add Chatroom.delete()
        pass

    def update(self):
        # TODO: Add Chatroom.update()
        pass

    @staticmethod
    def add():
        # TODO: Add Chatroom.add()
        pass


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

    def delete(self):
        #TODO: Add Message.delete()
        pass

    # Tweaked the interface below to include db
    def update(self, content=None, chatroomid=None, senderid=None, timestamp:datetime.datetime=None):

        try:
            c = self.__db.cursor()

            if content:
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


    @staticmethod
    def add(content, chatroomid, senderid, db:sqlite3.Connection):
        try:
            c = db.cursor()
            c.execute("INSERT INTO Message (content, chatroomid, senderid, timestamp) VALUES (?, ?, ?, ?)",
                      (content, chatroomid, senderid, datetime.datetime.now().timestamp()))
            new_messageid = c.lastrowid
            db.commit()

            return Message(new_messageid, db)

        except sqlite3.Error as e:
            db.rollback()
            print(f"ERROR: Exception raised when adding message.\n"
                  f"Database rolled back to last commit. Details:\n{e}")
            raise e

    @staticmethod
    def get_messages_from_user(userid, db:sqlite3.Connection):

        c = db.cursor()

        message_rows = c.execute("SELECT messageid FROM Message WHERE senderid = ?", [userid]).fetchall()

        messages_to_return = []

        for row in message_rows:

            messages_to_return.append(Message(int(row['messageid']), db))

        return messages_to_return


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
    def filepath(self):
        return self.__filepath

    @property
    def messageid(self):
        return self.__messageid

    @property
    def message(self):
        return Message(self.__messageid, self.__db)

    def delete(self):
        # TODO: Add Attachment.delete()
        pass

    def update(self):
        # TODO: Add Attachment.update()
        pass

    @staticmethod
    def add():
        # TODO: Add Attachment.add()
        pass


if __name__=="__main__":

    db = get_db()

