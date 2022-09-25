
from rdflib import RDF, RDFS, Dataset, Graph
from typing import Tuple

from .build import bind_prefixes
from .models import Entity, Relation
from .namespaces import DEFAULT
from .resources import ResourceStore
from .utils import load_triplestore, save_triplestore



def fetch_instances(graph:  Graph,
                    class_: type ) -> ResourceStore:
    """
    Fetch instances from graph
    """
    instances = ResourceStore()

    for iri in graph.subjects(RDF.type, class_._type.iri):
        label = graph.value(iri, RDFS.label)
        instance = class_(label, resource_store=instances)
        instance._quads = set()

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



def get_resources_ext(entities:  ResourceStore, 
                      relations: ResourceStore,
                      spacy:     bool, 
                      wikidata:  bool, 
                      wordnet:   bool         ) -> ResourceStore:
    """ 
    Fetch external data 
    """

    resources = ResourceStore()

    # Enrich entities list with SpaCy data
    if spacy:
        # from .external.spacy import build_sp_resources
        from .external.spacy import build_sp_resources
        resources_sp = build_sp_resources(entities)
        resources.update(resources_sp)

    # Enrich entities list with Wikidata data
    if wikidata:
        from .external.wikidata import build_wd_resources
        # from .external.wikidata.multiprocessing import build_wd_resources
        resources_wd = build_wd_resources(entities)
        resources.update(resources_wd)

    # Enrich entities and relations lists with WordNet data
    if wordnet:
        from .external.wordnet import build_wn_resources
        # from .external.wordnet.multiprocessing import build_wn_resources
        resources_wn = build_wn_resources(entities, relations)
        resources.update(resources_wn)

    return resources



def enrich_triplestore(spacy:    bool = False, 
                       wikidata: bool = False, 
                       wordnet:  bool = False,
                       path:     str  = "",
                       filename: str  = 'triplestore.nq') -> Dataset:
    """ 
    Secondary function 
    """
    assert spacy or wikidata or wordnet, "Please provide one external source of information"

    # Initialize triplestore
    ds = load_triplestore(path, filename)
    bind_prefixes(ds, spacy=spacy, wikidata=wikidata, wordnet=wordnet)

    # Enrich triplestore with external data
    entities, relations = get_instances(ds)
    resources_ext = get_resources_ext(entities, relations, spacy, wikidata, wordnet)

    # Fill triplestore with resources
    resources_ext.to_graph(ds)

    if path:
        # Save triplestore
        save_triplestore(ds, path, filename)

    return ds
