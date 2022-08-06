
from rdflib import Graph
from typing import Dict, Optional, Tuple

import pandas as pd

from .wikidata import build_wd_resources
from .wordnet import build_wn_resources
from .models import (
    ENTITY, ENTITY_HD, ENTITY_LD,
    RELATION, RELATION_HD, RELATION_LD,
    IS_HD_INSTANCE_OF, IS_NEG_OF,
    Entity, Instance, Relation
)
from .resources import ResourceStore
from .namespaces import (
    PREFIXES, RELATIO, RELATIO_HD, 
    RELATIO_LD, WIKIDATA, WORDNET
)



def bind_prefixes(graph: Graph, wikidata: bool, wordnet: bool) -> None:
    """ Bind prefixes to each base namespace """

    namespaces = [ RELATIO, RELATIO_HD, RELATIO_LD ]
    if wikidata:
        namespaces.append(WIKIDATA)
    if wordnet:
        namespaces.append(WORDNET)

    for namespace in namespaces:
        graph.bind(PREFIXES[namespace], namespace)


def add_resources(entities: Dict[str, ResourceStore], relations: Dict[str, ResourceStore]) -> None:
    """ Add base classes and properties """

    # Add classes
    _ = entities['base'].get_or_add(ENTITY)
    _ = entities['hd_ld'].get_or_add(ENTITY_HD)
    _ = entities['hd_ld'].get_or_add(ENTITY_LD)

    # Add properties
    _ = relations['base'].get_or_add(RELATION)
    _ = relations['hd_ld'].get_or_add(RELATION_HD)
    _ = relations['hd_ld'].get_or_add(RELATION_LD)
    _ = relations['base'].get_or_add(IS_HD_INSTANCE_OF)
    _ = relations['base'].get_or_add(IS_NEG_OF)


def build_instance(class_: type,
                   label: str, 
                   namespace: str,
                   resource_store: Dict[str, ResourceStore],
                   **kwargs) -> Optional[Instance]:
    """ Build instance from label """

    if pd.isna(label):
        return None

    # Create instance in base namespace
    instance_base = class_(label, RELATIO, resource_store=resource_store['base'], **kwargs)

    # Create non-negative instance if instance_base is neg
    if kwargs.get('is_neg', False):
        instance_non_neg = class_(label, RELATIO, resource_store=resource_store['base'], is_neg=False)
        instance_non_neg.set_neg_instance(instance_base)

    # Create instance in appropriate namespace
    instance = class_(label, namespace, resource_store=resource_store['hd_ld'], **kwargs)
    instance.set_base_instance(instance_base)

    return instance


def build_instances(class_: type, 
                    row: pd.Series, 
                    key: str, 
                    resource_stores: Dict[str, ResourceStore],
                    **kwargs) -> Tuple[Instance, Instance]:
    """ Build HD/LD instances from extracted concepts """

    label_hd = row[f"{key}_highdim"]
    label_ld = row[f"{key}_lowdim"]
    kwargs_hd = kwargs.get('hd', {})
    kwargs_ld = kwargs.get('ld', {})

    # Create instances in HD/LD namespaces
    instance_hd = build_instance(class_, label_hd, RELATIO_HD, resource_stores, **kwargs_hd)
    instance_ld = build_instance(class_, label_ld, RELATIO_LD, resource_stores, **kwargs_ld)

    # Set isHDInstanceOf property
    if not ( instance_hd is None or instance_ld is None ):
        instance_hd.set_ld_instance(instance_ld)
        
    return instance_hd, instance_ld


def build_resources(df: pd.DataFrame) -> Tuple[Dict[str, ResourceStore], Dict[str, ResourceStore]]:
    """ Build list of triples from sets of entities/property """

    entities = { 'base': ResourceStore(), 'hd_ld': ResourceStore() }
    relations = { 'base': ResourceStore(), 'hd_ld': ResourceStore() }

    # Add base classes and properties
    add_resources(entities, relations)

    # Iterate over each set of entities/property
    for _, row in df.iterrows():
        
        # Build subject/object entities
        subject_hd, subject_ld = build_instances(Entity, row, 'ARG0', entities)
        object_hd, object_ld = build_instances(Entity, row, 'ARG1', entities)
        
        # Build relation property
        kwargs = { 
            'hd': { 'is_neg': row['B-ARGM-NEG_highdim'] }, 
            'ld': { 'is_neg': row['B-ARGM-NEG_lowdim'] } 
        }
        relation_hd, relation_ld = build_instances(Relation, row, 'B-V', relations, **kwargs)
        
        # Add HD/LD relations to objects
        if not ( subject_hd is None or relation_hd is None ):
            if object_hd is None:
                object_hd = subject_hd
            subject_hd.add_object(relation_hd, object_hd)

        if not ( subject_ld is None or relation_ld is None ):
            if object_ld is None:
                object_ld = subject_ld
            subject_ld.add_object(relation_ld, object_ld) 

    return entities, relations


def enrich_triplestore(wikidata: bool, 
                       wordnet: bool, 
                       entities: ResourceStore, 
                       relations: ResourceStore) -> ResourceStore:
    """ Fetch external data """

    resources = ResourceStore()

    # Enrich entities list with WikiData data
    if wikidata:
        resources_wd = build_wd_resources(entities)
        resources.update(resources_wd)

    # Enrich entities and relations lists with WordNet data
    if wordnet:
        resources_wn = build_wn_resources(entities, relations)
        resources.update(resources_wn)

    return resources


def save_triplestore(graph: Graph, path: str) -> None:
    """ Save triplestore into .ttl file """
    if path and path[-1] != "/":
        path += "/"
    graph.serialize(path + 'triplestore.ttl', "turtle")


def build_triplestore(df: pd.DataFrame, 
                      wikidata: bool = False, 
                      wordnet: bool = False, 
                      path: str = "") -> None:
    """ Main function """

    # Initialize triplestore
    graph = Graph()
    bind_prefixes(graph, wikidata, wordnet)

    # Build instances
    entities, relations = build_resources(df)
    resources = entities['base'] | entities['hd_ld'] | relations['base'] | relations['hd_ld']

    # Enrich triplestore with external data
    resources_ext = enrich_triplestore(wikidata, wordnet, entities['base'], relations['base'])
    resources.update(resources_ext)

    # Fill triplestore with resources and triples
    resources.to_graph(graph)

    # Save triplestore
    save_triplestore(graph, path=path)
