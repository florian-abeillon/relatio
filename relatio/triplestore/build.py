
from rdflib import Graph, OWL, RDF, RDFS
from typing import Dict, List, Tuple

import pandas as pd

from relatio.triplestore.wikidata.enrich import add_wd_triples
from relatio.triplestore.instances import Entity, Instance, Relation
from relatio.triplestore.resources import Resource, ResourceStore, BASE_RESOURCES
from relatio.triplestore.namespaces import PREFIXES, RELATIO, RELATIO_HD, RELATIO_LD, WIKIDATA


def initialize_triplestore() -> Graph:
    """ Initialize triplestore """

    graph = Graph()

    # Bind prefixes to each custom namespace
    for prefix, namespace in PREFIXES:
        graph.bind(prefix, namespace)

    # Fill triplestore with classes and properties
    for resource in BASE_RESOURCES:
        resource.to_graph(graph)

    ## Link equivalent properties
        
    # From https://www.wikidata.org/wiki/Wikidata:Relation_between_properties_in_RDF_and_in_Wikidata
    equivalent_props = [
        ( Resource('P31', WIKIDATA), Resource('type', RDF) ),
        ( Resource('P279', WIKIDATA), Resource('subClassOf', RDFS) ),
        ( Resource('P1647', WIKIDATA), Resource('subPropertyOf', RDFS) )
    ]

    # -> OWL Full (owl:sameAs between properties)
    def add_equivalent_props(graph: Graph, prop1: Resource, prop2: Resource) -> None:
        graph.add(( prop1.iri, OWL.sameAs, prop2.iri ))

    for prop1, prop2 in equivalent_props:
        add_equivalent_props(graph, prop1, prop2)

    return graph


def build_instance(class_: type,
                   label: str, 
                   namespace: str,
                   resource_store_base: ResourceStore,
                   **kwargs) -> Relation:
    """ Build instance from label """

    # Create instance in base namespace
    instance_base = class_(label, RELATIO, **kwargs)
    resource_store_base.get_or_add(instance_base)

    # Create non-negative instance if instance_base is neg
    if kwargs.get('is_neg', False):
        instance_non_neg = class_(label, RELATIO, is_neg=False)
        instance_non_neg.set_neg_instance(instance_base)
        resource_store_base.get_or_add(instance_non_neg)

    # Create instance in appropriate namespace
    instance = class_(label, namespace, **kwargs)
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

    # Create instances in HD/LD namespaces, and set isHDInstanceOf property
    instance_hd = build_instance(class_, label_hd, RELATIO_HD, resource_stores['base'], **kwargs_hd)
    instance_ld = build_instance(class_, label_ld, RELATIO_LD, resource_stores['base'], **kwargs_ld)
    instance_hd.set_ld_instance(instance_ld)

    # Add instances to appropriate ResourceStore
    resource_stores['hd'].get_or_add(instance_hd)
    resource_stores['ld'].get_or_add(instance_ld)
        
    return instance_hd, instance_ld


def build_triples(df: pd.DataFrame) -> Tuple[Dict[str, ResourceStore], 
                                             Dict[str, ResourceStore],
                                             List[tuple]]:
    """ Build list of triples from sets of entities/property """

    entities = { 'base': ResourceStore(), 'hd': ResourceStore(), 'ld': ResourceStore() }
    relations = { 'base': ResourceStore(), 'hd': ResourceStore(), 'ld': ResourceStore() }
    triples = []

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
        
        # Add HD/LD triples
        triples.append(( subject_hd.iri, relation_hd.iri, object_hd.iri ))
        triples.append(( subject_ld.iri, relation_ld.iri, object_ld.iri ))    

    return entities, relations, triples


def fill_triplestore(graph: Graph, df: pd.DataFrame) -> None:
    """ Fill triplestore with sets of entities/property """

    # Build triples
    entities, relations, triples = build_triples(df)

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


def build_triplestore(df: pd.DataFrame, wikidata: bool = False, path: str = "") -> None:
    """ Main function """

    # Build and fill triplestore with df
    graph = initialize_triplestore()
    fill_triplestore(graph, df)

    # Enrich triplestore with WikiData data
    if wikidata:
        add_wd_triples(graph, df)

    # Save triplestore
    save_triplestore(graph, path=path)
