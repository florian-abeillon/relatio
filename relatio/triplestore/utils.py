
import hashlib


def get_hash(class_: str, label: str) -> str:
    """ Generates hash of instance of class_ with label label_ """
    return f"{class_}/{hashlib.sha1(label.encode('utf-8')).hexdigest()}"
