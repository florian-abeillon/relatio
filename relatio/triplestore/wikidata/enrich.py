
from rdflib import OWL, RDF, RDFS, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, List, Union

import os
import re
import spacy

from .models import (
    ENTITY_WD, IS_WD_INSTANCE_OF, RELATION_WD, 
    WdEntity, WdRelation
)
from ..namespaces import WIKIDATA
from ..resources import ResourceStore, Triple


nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('opentapioca')

URL = 'https://query.wikidata.org/sparql'

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'query.sparql')
with open(path) as f:
    QUERY = f.read()



def add_resources(resources: ResourceStore) -> None:
    """ Add WikiData classes and properties """
    _ = resources.get_or_add(ENTITY_WD)
    _ = resources.get_or_add(IS_WD_INSTANCE_OF)
    _ = resources.get_or_add(RELATION_WD)



def add_eq_properties(resources: ResourceStore) -> None:
    """ Link equivalent properties """
        
    # From https://www.wikidata.org/wiki/Wikidata:Relation_between_properties_in_RDF_and_in_Wikidata
    equivalent_props = [
        ( URIRef(WIKIDATA + 'P31'), RDF.type ),
        ( URIRef(WIKIDATA + 'P279'), RDFS.subClassOf ),
        ( URIRef(WIKIDATA + 'P1647'), RDFS.subPropertyOf )
    ]

    for prop1, prop2 in equivalent_props:
        _ = resources.get_or_add(Triple(( prop1, OWL.sameAs, prop2 )))
        _ = resources.get_or_add(Triple(( prop2, OWL.sameAs, prop1 )))



def clean_res(res: Dict[str, str]) -> List[Dict[str, Union[str, List[str]]]]:
    """ Format res and remove uninformative WikiData attributes """

    res_clean = []

    for r in res['results']['bindings']:

        # Format results
        r_clean = { 
            'predicate': { 
                'label': r['p_label']['value'], 
                'iri': r['p_iri']['value'] 
            } 
        }

        # Parse o_list
        o_list = r['o_list']['value'].split('|')
        objects, attributes = [], []

        for o in o_list:
            o = o.split("\\")

            if len(o) == 2:
                object_ = { 'label': o[0], 'iri': o[1] }
                objects.append(object_)
            else:
                attribute = { 'label': o[0] }
                attributes.append(attribute)

        r_clean['objects'] = objects
        r_clean['attributes'] = attributes
        

        # TODO: To improve
        # Whether to keep or not o_list
        if (
            # If attribute is an ID, or
            re.findall("ID( *\(.*\))? *$", r_clean['predicate']['label']) or

            # If attribute label is in uppercase (likely not informative), or
            r_clean['predicate']['label'].isupper() or

            # If attribute is a mixture of letters and numbers (likely not informative)
            (
                not r_clean['attributes'][0]['label'].isalpha() and
                not r_clean['attributes'][0]['label'].isnumeric()
            )
        ):
            continue
        
        res_clean.append(r_clean)

    return res_clean
        


# TODO: Add timer to regulate number of requests
def query_wd(iri: str) -> List[Dict[str, str]]:
    """ Query WikiData knowledge base """

    # Prepare query
    sparql = SPARQLWrapper(URL)
    sparql.setReturnFormat(JSON)
    query = QUERY.format(iri=iri)
    sparql.setQuery(query)

    # Query WikiData
    res = sparql.queryAndConvert()

    # Format and clean result
    res = clean_res(res)

    return res



def build_instances(entity: WdEntity, resources: ResourceStore) -> None:
    """ Build instances from WikiData results """

    # Iterate over each set of relation/objects returned from WikiData
    res = query_wd(entity.iri)

    for r in res:

        # Build and add relation property
        relation = WdRelation(r['predicate']['label'], 
                              iri=r['predicate']['iri'], 
                              resource_store=resources)

        # Add objects to entity
        objects = [
            WdEntity(object_['label'], 
                     iri=object_['iri'], 
                     resource_store=resources)
            for object_ in r['objects']
        ]
        entity.set_objects(relation, objects)

        # Add attributes to entity
        attributes = [
            attribute['label']
            for attribute in r['objects']
        ]
        entity.set_attributes(relation, attributes)



def build_wd_resources(entities: ResourceStore) -> ResourceStore:
    """ Main function """

    resources_wd = ResourceStore()

    # Add WikiData class and properties
    add_resources(resources_wd)
    # Link equivalent properties
    add_eq_properties(resources_wd)

    # Iterate over every base entity
    for entity in entities.values():
        print(entity._label)

        # Extract named entities
        try:
            entity_wd = nlp(entity._label)
            print(entity_wd)
            entity_wd = entity_wd.ents[0]
            print(entity_wd)
        except IndexError:
            print()
            continue
        print()
        # Build WikiData entity
        entity_wd = WdEntity(entity_wd, resource_store=resources_wd)
        entity_wd.set_relatio_instance(entity)

        # Query WikiData, and add triples
        build_instances(entity_wd, resources_wd)

    return resources_wd
