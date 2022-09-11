
import hashlib


to_pascal_case = lambda text: "".join([ 
    token[0].upper() + token[1:] 
    for token in str(text).replace("_", " ").split() 
])

to_camel_case = lambda text: str(text)[0].lower() + to_pascal_case(text)[1:]


def get_hash(text: str) -> int:
    """ 
    Generates SHA1 hash of text
    """
    return int(hashlib.sha1(text.encode('utf-8')).hexdigest(), 16)


def format_path(path: str) -> str:
    """ Format path to end with slash """
    if path and path[-1] != "/":
        path += "/"
    return path
