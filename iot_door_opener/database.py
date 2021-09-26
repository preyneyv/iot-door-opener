import sqlite3

from .helpers import data_path, random_phrase

connection = sqlite3.connect(data_path('data.db'))


cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS `token_requests` (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nicename TEXT NOT NULL,
    approved INTEGER DEFAULT 0 NOT NULL,
    username TEXT DEFAULT NULL, 
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
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


def get_pending_requests():
    """
    Return all pending requests from the database.
    :return: list of row tuples
    """
    cursor.execute("SELECT `id`, `nicename`, `timestamp` from `token_requests` WHERE `approved`=0")
    return cursor.fetchall()


def approve_request(idx, name):
    """
    Approve a specific request. Does not commit changes.
    :param idx: id to approve
    :param name: name of user
    """
    cursor.execute("UPDATE `token_requests` SET `approved`=1, `username`=? WHERE `id`=?", (name, idx))


def reject_request(idx):
    """
    Reject a specific request. Does not commit changes.
    :param idx: id to reject
    """
    cursor.execute("DELETE FROM `token_requests` WHERE id=?", (idx,))


def purge_requests():
    """
    Remove all unapproved requests. Does not commit changes.
    """
    cursor.execute("DELETE FROM `token_requests` WHERE `approved`=0")


def commit():
    """
    Commit any pending transactions on the connection.
    """
    connection.commit()


def rollback():
    """
    Rollback any pending transactions on the connection.
    """
    connection.rollback()
