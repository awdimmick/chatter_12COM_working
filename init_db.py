import sqlite3, random

DB_PATH = 'chatter_db.db'

db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
db.row_factory = sqlite3.Row


def init_db(dbcnx:sqlite3.Connection):

    create_user_table(dbcnx)
    create_chatroom_table(dbcnx)
    create_chatroommember_table(dbcnx)
    create_message_table(dbcnx)
    create_attachment_table(dbcnx)


def create_user_table(dbcnx:sqlite3.Connection):

    try:
        # GET DATABASE CURSOR OBJECT
        c = dbcnx.cursor()

        # REMOVE EXISTING USER TABLE
        c.execute("DROP TABLE IF EXISTS User")

        # CREATE USER TABLE
        sql = '''CREATE TABLE IF NOT EXISTS User (
                                    userid INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT UNIQUE NOT NULL,
                                    password TEXT NOT NULL,
                                    last_login_ts NUMERIC,
                                    admin INTEGER DEFAULT 0,
                                    active INTEGER DEFAULT 1)
                              '''

        c.execute(sql)

        # Add 'deleteduser' entry to assign messages to when a user is deleted later
        c.execute("INSERT INTO User VALUES (0,'DeletedUser','',0,0,0)")

        dbcnx.commit()

        print("Success: User table initialised.")

    except sqlite3.Error as e:
        dbcnx.rollback()
        print("ERROR: Unable to create User table. Details:", e)
        raise e


def create_chatroom_table(dbcnx:sqlite3.Connection):

    try:
        c = dbcnx.cursor()
        # REMOVE EXISTING CHATROOM TABLE
        c.execute("DROP TABLE IF EXISTS Chatroom")

        # CREATE NEW CHATROOM TABLE
        sql = '''CREATE TABLE IF NOT EXISTS Chatroom (
                        chatroomid INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT NOT NULL,
                        joincode TEXT UNIQUE NOT NULL 
                    )
            '''
        c.execute(sql)

        dbcnx.commit()
        print("Success: Chatroom table initialised.")

    except sqlite3.Error as e:
        dbcnx.rollback()
        print("ERROR: Unable to create Chatroom table. Details:", e)
        raise e


def create_chatroommember_table(dbcnx:sqlite3.Connection):

    try:
        c = dbcnx.cursor()
        c.execute("DROP TABLE IF EXISTS ChatroomMember")

        sql = '''CREATE TABLE IF NOT EXISTS ChatroomMember(
                        chatroomid INTEGER NOT NULL,
                        userid INTEGER NOT NULL,
                        owner INTEGER DEFAULT 0,
                        PRIMARY KEY (chatroomid, userid),
                        FOREIGN KEY (userid) references User(userid)
                    )'''

        c.execute(sql)
        dbcnx.commit()
        print("Success: ChatroomMember table initialised.")

    except sqlite3.Error as e:
        dbcnx.rollback()
        print("ERROR: Unable to create ChatroomMember table. Details:", e)
        raise e


def create_message_table(dbcnx:sqlite3.Connection):

    try:
        c = dbcnx.cursor()

        c.execute("DROP TABLE IF EXISTS Message")

        sql = '''CREATE TABLE IF NOT EXISTS Message (
                        messageid INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        chatroomid INTEGER NOT NULL,
                        senderid INTEGER NOT NULL,
                        timestamp NUMERIC,
                        FOREIGN KEY (chatroomid) REFERENCES Chatroom(chatroomid),
                        FOREIGN KEY (senderid) REFERENCES User(userid)
                )'''

        c.execute(sql)
        dbcnx.commit()
        print("Success: Message table initialised.")


    except sqlite3.Error as e:
        dbcnx.rollback()
        print("ERROR: Unable to create Message table. Details:", e)
        raise e


def create_attachment_table(dbcnx:sqlite3.Connection):

    try:
        c = dbcnx.cursor()

        c.execute("DROP TABLE IF EXISTS Attachment")

        sql = '''CREATE TABLE IF NOT EXISTS Attachment (
                    
                        attachmentid INTEGER PRIMARY KEY AUTOINCREMENT,
                        messageid INTEGER NOT NULL,
                        filepath TEXT NOT NULL,
                        FOREIGN KEY (messageid) REFERENCES Message(messageid)
                    
                    )'''

        c.execute(sql)

        dbcnx.commit()
        print("Success: Attachment table initialised.")


    except sqlite3.Error as e:
        dbcnx.rollback()
        print("ERROR: Unable to create Attachment table. Details:", e)
        raise e


if __name__ == '__main__':
    try:
        conf_number = random.randint(100000,999999)

        print(f"WARNING: Continuing will erase all contents in the database '{DB_PATH}'.\n"
          f"Please ensure that you have a recent backup of the database file!")

        if input(f"Please enter the number {conf_number} to continue: ") != str(conf_number):
            raise ValueError("Incorrect confirmation code entered.")

        init_db(db)

    except Exception as e:
        print(e)

