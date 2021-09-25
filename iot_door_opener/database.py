import sqlite3

from .helpers import data_path, random_phrase

connection = sqlite3.connect(data_path('data.db'))


cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS `token_requests` (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nicename TEXT NOT NULL,
    approved INTEGER DEFAULT 0 NOT NULL,
    username TEXT DEFAULT NULL
)""")
connection.commit()


def create_token_request():
    """
    Create a request for an access token.
    :return: the request information
    """
    nicename = random_phrase()
    cursor.execute("INSERT INTO `token_requests` (nicename) VALUES (?)",
                   (nicename,))
    connection.commit()
    idx = cursor.lastrowid
    return idx, nicename


def is_request_approved(idx):
    """
    Check whether the given request id approved. Also deletes the request.
    :param idx: the id to check
    :return: whether the request is approved
    """
    cursor.execute("SELECT * FROM `token_requests` WHERE id=?", (idx,))
    row = cursor.fetchone()

    if row is None:
        return None, None

    if row[2]:
        # Approved! We can delete itttttt
        cursor.execute("DELETE FROM `token_requests` WHERE id=?", (idx,))
        connection.commit()

    return bool(row[2]), row[3]
