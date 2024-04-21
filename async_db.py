import aiosqlite
from datetime import datetime
from typing import Optional


async def db_connection(dbname: str) -> Optional[aiosqlite.Connection]:
    """
    Make connection to database
    :param dbname: database name
    :return: DB connection object
    """
    try:
        db_conn = await aiosqlite.connect(dbname)
        return db_conn
    except aiosqlite.Error as e:
        print(f"Error connecting to database: {e}")
        return None


async def add_user(db_obj: aiosqlite.Connection, uid: int, nick: str) -> bool:
    """
    Add new user to the database
    :param db_obj: DB connection
    :param uid: user id
    :param nick: user's nickname
    :return: True if successful, False otherwise
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO users (uid, nick, is_blocked, joined) VALUES (?, ?, ?, ?)",
                (uid, nick, 0, datetime.now().isoformat())
            )
        await db_obj.commit()
        return True
    except aiosqlite.Error as e:
        print(f"Error adding user: {e}")
        return False


async def get_users(db_obj: aiosqlite.Connection) -> list:
    """
    Get list of users who isn't blocked.
    :param db_obj: DB connection
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute("SELECT uid, nick FROM users WHERE is_blocked = 0")
            result = await cursor.fetchall()
        return result
    except aiosqlite.Error as e:
        print(f"Error getting users: {e}")
        return list()


async def ban_unban_user(uid: int, action: int, db_obj: aiosqlite.Connection) -> bool:
    """
    Function to ban or unban a user
    :param db_obj: DB connection
    :param uid: user id
    :param action: 1 - ban or 0 - unban
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute("UPDATE users SET is_blocked = ? WHERE uid == ?", (action, uid))
        await db_obj.commit()
        return True
    except aiosqlite.Error as e:
        print(f"Error banning user: {e}")
        return False


async def delete_user(uid: int, db_obj: aiosqlite.Connection) -> bool:
    """
    Deletes a user from the database
    :param db_obj: DB connection
    :param uid: user id which should be deleted
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute("DELETE FROM users WHERE uid == ?", (uid,))
        await db_obj.commit()
        return True
    except aiosqlite.Error as e:
        print(f"Error deleting user: {e}")
        return False


async def is_user_exists(uid: int, db_obj: aiosqlite.Connection) -> bool:
    """
    Return true if user exists in DB, false otherwise
    :param db_obj: DB connection
    :param uid: user id
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE uid == ?", (uid,))
            user = await cursor.fetchall()
        return True if user else False
    except aiosqlite.Error as e:
        print(f"Error finding user: {e}")
        return False


async def blocklist(db_obj: aiosqlite.Connection) -> list:
    """
    Get list of users who have been blocked.
    :param db_obj: DB connection
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute("SELECT uid FROM users WHERE is_blocked == 1")
            raw_data = await cursor.fetchall()
            users = [x[0] for x in raw_data]
        return users
    except aiosqlite.Error as e:
        print(f"Error finding user: {e}")
        return list()


async def get_blocked_or_unblocked_users(db_obj: aiosqlite.Connection, state: int) -> list:
    """
    Get list of users who have been blocked or who is unblocked.
    :param db_obj: DB connection
    :param state: blocked or unblocked
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute("SELECT uid, nick FROM users WHERE is_blocked == ?", (state,))
            users = await cursor.fetchall()
        return users
    except aiosqlite.Error as e:
        print(f"Error finding user: {e}")
        return list()


async def add_message_entity(db_obj: aiosqlite.Connection, original_id: int, bot_id: int, sender: int, receiver: int) -> bool:
    """
    Add new message entity to the database.
    :param db_obj: DB connection
    :param original_id: Original message ID
    :param bot_id: Bot message ID
    :param sender: Sender's UID
    :param receiver: Receiver's UID
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (original_id, bot_id, sender, receiver))
        await db_obj.commit()
        return True
    except aiosqlite.Error as e:
        print(f"Error adding user: {e}")
        return False


async def get_message_entity(db_obj: aiosqlite.Connection, value: int) -> tuple:
    """
    Get message info from messages list.
    :param db_obj: DB connection
    :param value: Value of the column
    """
    try:
        async with db_obj.cursor() as cursor:
            await cursor.execute("SELECT * FROM messages WHERE original_id == ? or bot_id == ?", (value, value))
            data = await cursor.fetchone()
        return data
    except aiosqlite.Error as e:
        print(f"Error finding user: {e}")
        return tuple()


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
