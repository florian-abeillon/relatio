
from rdflib import RDF, RDFS, Dataset, Graph
from typing import Tuple

from .build import (
    bind_prefixes, get_resources_ext, save_triplestore
)
from .models import Entity, Relation
from .namespaces import DEFAULT
from .resources import ResourceStore
from .utils import format_path



def fetch_instances(graph:  Graph,
                    class_: type ) -> ResourceStore:
    """
    Fetch instances from graph
    """
    instances = ResourceStore()

    for iri in graph.subjects(RDF.type, class_._type.iri):
        label = graph.value(iri, RDFS.label)
        instance = class_(label, instances)
        instance._quads = []

    return instances



def get_instances(ds: Dataset) -> Tuple[ResourceStore,
                                        ResourceStore]:
    """
    Extract instances from DEFAULT graph
    """
    graph = ds.graph(DEFAULT)
    entities  = fetch_instances(graph, Entity)
    relations = fetch_instances(graph, Relation)
    return entities, relations



def load_triplestore(path:     str,
                     filename: str) -> Dataset:
    """ 
    Save triplestore into .trig file 
    """
    print("> Loading triplestore..")
    ds = Dataset()
    path = format_path(path)
    ds.parse(path + filename + '.trig', format='trig')
    return ds



async def enrich_triplestore(spacy:    bool = False, 
                             wikidata: bool = False, 
                             wordnet:  bool = False,
                             path:     str  = "",
                             filename: str  = 'triplestore') -> Dataset:
    """ 
    Secondary function 
    """
    assert spacy or wikidata or wordnet, "Please provide one external source of information"

    # Initialize triplestore
    ds = load_triplestore(path, filename)
    bind_prefixes(ds, spacy=spacy, wikidata=wikidata, wordnet=wordnet, relatio=False)

    # Enrich triplestore with external data
    entities, relations = get_instances(ds)
    resources_ext = await get_resources_ext(entities, relations, spacy, wikidata, wordnet)

    # Fill triplestore with resources
    resources_ext.to_graph(ds)

    # Save triplestore
    save_triplestore(ds, path, filename)

    return ds
