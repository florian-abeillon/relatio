
import hashlib


def get_hash(class_: str, label: str) -> str:
    """ Generates hash of instance of class_ with label label_ """
    return f"{class_}/{hashlib.sha1(label.encode('utf-8')).hexdigest()}"


to_pascal_case = lambda text: "".join([ 
    token[0].upper() + token[1:] 
    for token in text.replace("_", " ").split() 
])

to_camel_case = lambda text: text[0].lower() + to_pascal_case(text)[1:]


def add_two_way(graph_or_resource_store, triple: tuple) -> None:
    """ Add triple and its inverse to graph/ResourceStore """
    graph_or_resource_store.add(triple)
    graph_or_resource_store.add(triple.inverse())
