
from rdflib import URIRef
from typing import Optional
import hashlib


to_pascal_case = lambda text: "".join([ 
    token[0].upper() + token[1:] 
    for token in text.replace("_", " ").split() 
])

to_camel_case = lambda text: text[0].lower() + to_pascal_case(text)[1:]


def get_hash(class_: str, 
             label:  str) -> str:
    """ 
    Generates hash of instance of class_ with label label_ 
    """
    return f"{class_}/{hashlib.sha1(label.encode('utf-8')).hexdigest()}"


def add_two_way(graph_or_resource_store, 
                quad:                    tuple,
                other_namespace:         Optional[URIRef] = None) -> None:
    """ 
    Add triple and its inverse to graph/ResourceStore 
    """
    graph_or_resource_store.add(quad)
    graph_or_resource_store.add(quad.inverse(namespace=other_namespace))


def format_path(path: str) -> str:
    """ Format path to end with slash """
    if path and path[-1] != "/":
        path += "/"
    return path
