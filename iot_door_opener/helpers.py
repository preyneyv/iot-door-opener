import os
import random
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

NOUN_FILE = 'english-nouns.txt'
ADJECTIVE_FILE = 'english-adjectives.txt'


def env(key):
    """
    Retrieve an environment variable
    :param key: the name of the variable
    :return: the value of the variable
    """
    return os.environ[key]


def data_path(*parts):
    """
    Return the path to a file relative to the configured data folder
    :param parts: path segments
    :return: complete path
    """
    return Path(env('IDO_DATA_FOLDER')).joinpath(*parts)


def static_path(*parts):
    """
    Return the path to a file relative to the configured data folder
    :param parts: path segments
    :return: complete path
    """
    return Path(__file__).parent.joinpath('static', *parts)


def validate_request_password(pwd):
    return pwd == env('IDO_REQUEST_PWD')


def get_token_from_request(req):
    method, token = req.headers['Authorization'].split()
    assert method == 'Bearer'
    return token


def _get_word_list():
    """
    Load or download wordlists. Return tuple of adjectives and nouns.
    """
    with open(static_path(NOUN_FILE)) as file:
        nouns = file.readlines()

    with open(static_path(ADJECTIVE_FILE)) as file:
        adjectives = file.readlines()

    return nouns, adjectives


NOUNS, ADJECTIVES = _get_word_list()


def random_phrase():
    return ' '.join(random.choice(s).strip() for s in (ADJECTIVES, NOUNS))