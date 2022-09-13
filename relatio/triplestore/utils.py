
from rdflib import Dataset

import hashlib
import os

from .namespaces import (
    PREFIXES, 
    RELATIO_HD, RELATIO_LD, 
    SPACY, WIKIDATA, WORDNET
)



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


def bind_prefixes(ds:       Dataset, 
                  relatio:  bool    = False,
                  spacy:    bool    = False, 
                  wikidata: bool    = False, 
                  wordnet:  bool    = False) -> None:
    """
    Bind prefixes to each base namespace 
    """
    assert relatio or spacy or wikidata or wordnet, "No namespace passed"

    namespaces = []

    if relatio:
        namespaces.extend([ 
            RELATIO_HD, RELATIO_LD 
        ])
    if spacy:
        namespaces.append(SPACY)
    if wikidata:
        namespaces.append(WIKIDATA)
    if wordnet:
        namespaces.append(WORDNET)

    for namespace in namespaces:
        ds.bind(PREFIXES[namespace], namespace)


def get_format(filename: str) -> str:
    """
    Get file format from its extension
    """
    EXTENSIONS = {
        'ttl': 'turtle',
        'nt': 'ntriples',
        'nq': 'nquads'
    }
    format_ = filename.split('.')[-1]
    format_ = EXTENSIONS.get(format_, format_)
    return format_


def save_triplestore(ds:       Dataset, 
                     path:     str    , 
                     filename: str    ) -> None:
    """ 
    Save triplestore into file 
    """
    print(f"Saving triplestore from {filename}..")
    format_ = get_format(filename)
    ds.serialize(os.path.join(path, filename), format_)


def load_triplestore(path:     str, 
                     filename: str) -> Dataset:
    """ 
    Load triplestore from file 
    """
    print(f"Loading triplestore from {filename}..")
    ds = Dataset()
    format_ = get_format(filename)
    ds.parse(os.path.join(path, filename), format_)
    return ds
