
from rdflib import Graph
from typing import Dict, List, Tuple

import pandas as pd

from relatio.triplestore.instances import Entity, Instance, Relation
from relatio.triplestore.resources import ResourceStore, BASE_RESOURCES
from relatio.triplestore.namespaces import PREFIXES, RELATIO_HD, RELATIO_LD


def initialize_triplestore() -> Graph:
    """ Initialize triplestore """

    graph = Graph()

    # Bind prefixes to each custom namespace
    for prefix, namespace in PREFIXES:
        graph.bind(prefix, namespace)

    # Fill triplestore with classes and properties
    for resource in BASE_RESOURCES:
        resource.to_graph(graph)

    return graph


def build_instances(row: pd.Series, 
                    key: str, 
                    class_: type, 
                    resource_stores: Dict[str, ResourceStore], 
                    **kwargs) -> Tuple[Instance, Instance]:
    """ Build HD/LD instances from extracted concepts """
    
    instance_hd = row[f"{key}_highdim"]
    instance_ld = row[f"{key}_lowdim"]
    
    # Create instance
    instance_hd = class_(instance_hd, RELATIO_HD, *kwargs.get('hd', []))
    instance_ld = class_(instance_ld, RELATIO_LD, *kwargs.get('ld', []))
    instance_hd.set_ld_instance(instance_ld)
        
    # Add instance to appropriate ResourceStore
    resource_stores['hd'].get_or_add(instance_hd)
    resource_stores['ld'].get_or_add(instance_ld)
        
    return instance_hd, instance_ld


def build_triples(df: pd.DataFrame) -> Tuple[List[tuple], 
                                             Dict[str, ResourceStore], 
                                             Dict[str, ResourceStore]]:
    """ Build list of triples from sets of entities/property """

    entities = { 'hd': ResourceStore(), 'ld': ResourceStore() }
    relations = { 'hd': ResourceStore(), 'ld': ResourceStore() }
    triples = []

    # Iterate over each set of entities/property
    for _, row in df.iterrows():
        
        # Build subject/object entities
        subject_hd, subject_ld = build_instances(row, 'ARG0', Entity, entities)
        object_hd, object_ld = build_instances(row, 'ARG1', Entity, entities)
        
        # Build relation property
        is_neg = { 'hd': [row['B-ARGM-NEG_highdim']], 'ld': [row['B-ARGM-NEG_lowdim']] }
        relation_hd, relation_ld = build_instances(row, 'B-V', Relation, relations, **is_neg)
        
        # Add HD/LD triples
        triples.append(( subject_hd.iri, relation_hd.iri, object_hd.iri ))
        triples.append(( subject_ld.iri, relation_ld.iri, object_ld.iri ))    

    return triples, entities, relations


def fill_triplestore(graph: Graph, df: pd.DataFrame) -> None:
    """ Fill triplestore with sets of entities/property """

    # Build triples
    triples, entities, relations = build_triples(df)

    # Fill triplestore with entities and relations
    resource_stores = list(entities.values()) + list(relations.values())
    for resource_store in resource_stores:
        resource_store.to_graph(graph)
        
    # Fill triplestore with triples 
    for triple in triples:
        graph.add(triple)


def save_triplestore(graph: Graph, path: str = "") -> None:
    """ Save triplestore into .ttl file """
    if path and path[-1] != "/":
        path += "/"
    graph.serialize(path + 'triplestore.ttl', "turtle")


def build_triplestore(df: pd.DataFrame, path: str = "") -> None:
    """ Main function """

    # Build and fill triplestore with df
    graph = initialize_triplestore()
    fill_triplestore(graph, df)

    # Save triplestore
    save_triplestore(graph, path=path)
