
from rdflib import OWL, RDF, RDFS, URIRef
from requests import HTTPError
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, List, Union

import os
import re
import spacy
import time

from .models import (
    CLASSES_AND_PROPS_WD,
    WdEntity, WdRelation
)
from ..models import ReEntity
from ..namespaces import WIKIDATA
from ..resources import ResourceStore, Triple


nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('opentapioca')

URL = 'https://query.wikidata.org/sparql'

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'query.sparql')
with open(path) as f:
    QUERY = f.read()



def add_eq_properties(resources: ResourceStore) -> None:
    """ Link equivalent properties """
        
    # From https://www.wikidata.org/wiki/Wikidata:Relation_between_properties_in_RDF_and_in_Wikidata
    equivalent_props = [
        ( URIRef(WIKIDATA + 'P31'),   RDF.type           ),
        ( URIRef(WIKIDATA + 'P279'),  RDFS.subClassOf    ),
        ( URIRef(WIKIDATA + 'P1647'), RDFS.subPropertyOf )
    ]

    for prop1, prop2 in equivalent_props:
        resources.add(Triple( prop1, OWL.sameAs, prop2 ))
        resources.add(Triple( prop2, OWL.sameAs, prop1 ))


def clean_res(res: Dict[str, str]) -> List[Dict[str, Union[str, List[str]]]]:
    """ Format res and remove uninformative Wikidata attributes """

    res_clean = []
    print("res['results']['bindings']", res['results']['bindings'])

    for r in res['results']['bindings']:

        # Format results
        r_clean = { 
            'predicate': { 
                'label': r['p_label']['value'], 
                'iri': r['p_iri']['value'] 
            } 
        }

        # TODO: To improve
        # Whether to keep or not result
        if (
            # If attribute is an ID, or
            re.findall("ID( *\(.*\))? *$", r_clean['predicate']['label']) or
            # If attribute label is in uppercase (likely not informative), or
            r_clean['predicate']['label'].isupper()
        ):
            continue


        # TODO: IRIs and labels duplicated
        # Parse o_list
        o_list = r['o_list']['value'].split('|')
        objects, attributes = [], []

        for o in o_list:

            o = o.split("\\")

            # TODO: To improve
            # Whether to keep or not object/attribute
            if (
                not o or not o[0] or 

                # If attribute is a mixture of letters and numbers, or
                ( not o[0].isalpha() and not o[0].isnumeric() ) or

                # If attribute is likely not informative (Wikidata ID, or like 'Category:', 'Template:', etc.)
                re.match(r"Q\d+", o[0]) or re.match(r"[A-Z][a-z]+\:\w+", o[0])
            ):
                continue

            if len(o) == 2 and o[0] != o[1]:
                object_ = { 'label': o[0], 'iri': o[1] }
                objects.append(object_)
            else:
                attribute = { 'label': o[0] }
                attributes.append(attribute)

        r_clean['objects'] = objects
        r_clean['attributes'] = attributes
        
        res_clean.append(r_clean)

    print("res_clean", res_clean)
    return res_clean
        


# TODO: Add timer to regulate number of requests
# TODO: Batch queries
def query_wd(iri: str) -> List[Dict[str, Union[str, List[str]]]]:
    """ Query Wikidata knowledge base """

    # Prepare query
    sparql = SPARQLWrapper(URL)
    sparql.setReturnFormat(JSON)
    query = QUERY.format(iri=iri)
    sparql.setQuery(query)

    # Query Wikidata
    try:
        res = sparql.queryAndConvert()
    except HTTPError:
        print(res)
        # If too many requests, wait for a bit
        time.sleep(res.header['Retry-After'])
        res = sparql.queryAndConvert()

    # Format and clean result
    res = clean_res(res)

    return res



def build_instances(entity: WdEntity, resources: ResourceStore) -> None:
    """ Build instances from Wikidata results """

    # Iterate over each set of relation/objects returned from Wikidata
    res = query_wd(entity.iri)

    for r in res:

        # Build and add relation property
        relation = WdRelation(r['predicate']['label'], resources, r['predicate']['iri'])

        # Add objects to entity
        objects = [
            WdEntity(object_['label'], resources, iri=object_['iri'])
            for object_ in r['objects']
        ]
        entity.add_objects(relation, objects)

        # Add attributes to entity
        attributes = [ attribute['label'] for attribute in r['objects'] ]
        entity.add_attributes(relation, attributes)



def build_wd_resources(resources: ResourceStore) -> ResourceStore:
    """ Main function """

    # Initialize ResourceStore with Wikidata class and properties
    resources_wd = ResourceStore(CLASSES_AND_PROPS_WD)

    # Link equivalent properties
    add_eq_properties(resources)

    # Iterate over every base entity
    entities = list(resources.values())
    for entity in entities:

        # NER on entity
        label = nlp(entity._label)
        ents = label.ents

        if not ents:
            continue

        for entity_wd in ents:

            # Build partOf Relatio entity
            re_entity = ReEntity(entity_wd, resources)
            entity.add_partOf_instance(re_entity)

            # Build Wikidata entity, and link them to Relatio entity
            entity_wd = WdEntity(entity_wd, resources_wd)
            entity_wd.set_re_entity(re_entity)

        # Query WikiWikidataData, and add triples
        build_instances(entity_wd, resources_wd)

    return resources_wd
