import sqlite3
from datetime import datetime


def db_connection(dbname: str) -> sqlite3.Connection:
    """
    Make connection to database
    :param dbname: database name
    """
    conn = sqlite3.connect(dbname)
    return conn


def make_table(db_obj: sqlite3.Connection) -> bool:
    """
    Make a table if it doesn't exist.
    :param db_obj: DB connection
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY NOT NULL, 
            nick TEXT NOT NULL, 
            is_blocked INTEGER NOT NULL, 
            joined TEXT NOT NULL)"""
        )
        db_obj.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        return False
    finally:
        cursor.close()


def add_user(db_obj: sqlite3.Connection, uid: int, nick: str) -> bool:
    """
    Add new user to the database
    :param db_obj: DB connection
    :param uid: user id
    :param nick: user's nickname
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute(
            "INSERT INTO users (uid, nick, is_blocked, joined) VALUES (?, ?, ?, ?)",
            (uid, nick, 0, datetime.now().isoformat())
        )
        db_obj.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
        return False
    finally:
        cursor.close()


def get_users(db_obj: sqlite3.Connection) -> list:
    """
    Get list of users who isn't blocked.
    :param db_obj: DB connection
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute("SELECT uid, nick FROM users WHERE is_blocked = 0")
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Error getting users: {e}")
        return list()
    finally:
        cursor.close()


def ban_unban_user(uid: int, action: int, db_obj: sqlite3.Connection) -> bool:
    """
    Function to ban or unban a user
    :param db_obj: DB connection
    :param uid: user id
    :param action: 1 - ban or 0 - unban
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute("UPDATE users SET is_blocked = ? WHERE uid == ?", (action, uid))
        db_obj.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error banning user: {e}")
        return False
    finally:
        cursor.close()


def delete_user(uid: int, db_obj: sqlite3.Connection) -> bool:
    """
    Deletes a user from the database
    :param db_obj: DB connection
    :param uid: user id which should be deleted
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute("DELETE * FROM users WHERE uid == ?", (uid,))
        db_obj.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        cursor.close()


def is_user_exists(uid: int, db_obj: sqlite3.Connection) -> bool:
    """
    Return true if user exists in DB, false otherwise
    :param db_obj: DB connection
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute("SELECT * FROM users WHERE uid == ?", (uid,))
        user = cursor.fetchall()
        return True if user else False
    except sqlite3.Error as e:
        print(f"Error finding user: {e}")
        return False
    finally:
        cursor.close()


def blocklist(db_obj: sqlite3.Connection) -> list:
    """
    Get list of users who have been blocked.
    :param db_obj: DB connection
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute("SELECT * FROM users WHERE is_blocked == 1")
        raw_data = cursor.fetchall()
        users = [x[0] for x in raw_data]
        return users
    except sqlite3.Error as e:
        print(f"Error finding user: {e}")
        return list()
    finally:
        cursor.close()


def get_blocked_or_unblocked_users(db_obj: sqlite3.Connection, state: int) -> list:
    """
    Get list of users who have been blocked or who is unblocked.
    :param db_obj: DB connection
    :param state: blocked or unblocked
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute("SELECT * FROM users WHERE is_blocked == ?", (state,))
        users = cursor.fetchall()
        return users
    except sqlite3.Error as e:
        print(f"Error finding user: {e}")
        return list()
    finally:
        cursor.close()


def add_message_entity(db_obj: sqlite3.Connection, original_id: int, bot_id: int, sender: int, receiver: int) -> bool:
    """
    Add new message entity to the database.
    :param db_obj: DB connection
    :param original_id: Original message ID
    :param bot_id: Bot message ID
    :param sender: Sender's UID
    :param receiver: Receiver's UID
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (original_id, bot_id, sender, receiver))
        db_obj.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
        return False
    finally:
        cursor.close()


def get_message_entity(db_obj: sqlite3.Connection, value: int) -> tuple:
    """
    Get message info from messages list.
    :param db_obj: DB connection
    :param value: Value of the column
    """
    try:
        cursor = db_obj.cursor()
        cursor.execute("SELECT * FROM messages WHERE original_id == ? or bot_id == ?", (value, value))
        data = cursor.fetchone()
        return data
    except sqlite3.Error as e:
        print(f"Error finding user: {e}")
        return list()
    finally:
        cursor.close()


if __name__ == '__main__':
    from os import environ

    # from random import choices, randint
    db = "bot.db"
    # make_table(db_connection(db))
    # for i in range(777880, 777889):
    #     b = randint(3,20)
    #     a = "".join(choices("qwertyuiopasdfghjlkzxcnvb", k=b))
    #     print(add_user(db_connection(db), i, a))
    # print(get_blocked_users(db_connection(db)))
    user_id = 456654
    # print(blocklist_cache.is_user_blocked(user_id))
