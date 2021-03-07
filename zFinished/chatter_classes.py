import sqlite3, abc, datetime

DB_PATH = 'chatter_db.db'


def get_db():
    # This will eventually be replaced by a get_db() method in app.py that is
    # used to obtain the appropriate database connection for the application context requiring it.
    db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db


# Add abc to the import list at the top
class ChatterDB(abc.ABC):

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def add(self):
        pass

    @abc.abstractmethod
    def delete(self):
        pass


class UserNotFound(Exception):
    pass


class User(ChatterDB):

    def __init__(self, id, db:sqlite3.Connection):

        self.__db = db
        self.__userid = id

        c = self.__db.cursor()

        user_data = c.execute("SELECT username, last_login_ts, admin, active "
                              "FROM User WHERE userid=?",[self.__userid]).fetchone()

        if user_data:
            self.__username = user_data['username']
            self.__last_login_ts = user_data['last_login_ts']
            self.__admin = True if user_data['admin'] == 1 else False
            self.__active = True if user_data['active'] == 1 else False

        else:
            raise UserNotFound(f"ERROR: No user found with userid {id}.")

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

    def add(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass


if __name__ == "__main__":

    db = get_db()
    u = User(1, db)
