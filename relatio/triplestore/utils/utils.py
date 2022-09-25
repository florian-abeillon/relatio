
from rdflib import Dataset
import os

from ..namespaces import (
    PREFIXES, DEFAULT,
    SPACY, WIKIDATA, WORDNET
)

MULTIPROCESSING = True
MULTITHREADING  = True

EXTENSIONS = {
    'ttl': 'turtle',
    'nt': 'ntriples',
    'nq': 'nquads'
}



def bind_prefixes(ds:       Dataset, 
                  spacy:    bool    = False, 
                  wikidata: bool    = False, 
                  wordnet:  bool    = False) -> None:
    """
    Bind prefixes to each base namespace 
    """

    namespaces = [DEFAULT]

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
