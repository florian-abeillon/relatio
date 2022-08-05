
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


def clean_res(res: Dict[str, str]) -> List[Dict[str, Union[str, List[str]]]]:
    """ Format res and remove uninformative WikiData attributes """

    res_clean = []

    for r in res['results']['bindings']:

        # Format results
        r_clean = { key: value['value'] for key, value in r.items() }

        # Parse o_list
        o_list = r_clean['o_list'].split('|')

        for i, o in enumerate(o_list):
            o = o.split("\\")
            object_ = { 'o_label': o[0] }
            if len(o) == 2:
                object_['o_iri'] = o[1]
            o_list[i] = object_
        r_clean['o_list'] = o_list

        if (
            # TODO: To improve
            # If attribute is an ID, or
            re.findall("ID( *\(.*\))? *$", r_clean['p_label']) or
            # If attribute label is in uppercase (likely not informative), or
            r_clean['p_label'].isupper() or
            # If attribute is a mixture of letters and numbers (likely not informative)
            (
                not r_clean['o_list'][0]['o_label'].isalpha() and
                not r_clean['o_list'][0]['o_label'].isnumeric()
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
        relation = WdRelation(r['p_label'], iri=r['p_iri'], resources=resources)

        for object_ in r['o_list']:

            # If object is an entity
            if len(object_) == 2:
                object_ = WdEntity(object_['o_label'], iri=object_['o_iri'], resources=resources)
                entity.add_object(relation, object_)
            else:
                entity.add_attribute(relation, object_['o_label'])


def build_wd_resources(entities: ResourceStore) -> ResourceStore:
    """ Main function """

    resources_wd = ResourceStore()

    # Add WikiData class and properties
    add_resources(resources_wd)
    # Link equivalent properties
    add_eq_properties(resources_wd)

    # Iterate over every base entity
    for entity in entities:

        # Extract named entities
        try:
            entity_wd = nlp(entity._label)
            entity_wd = entity_wd.ents[0]
        except IndexError:
            continue

        # Build WikiData entity
        entity_wd = WdEntity(entity_wd, resources=resources_wd)
        entity_wd.set_relatio_instance(entity)

        # Query WikiData, and add triples
        build_instances(entity_wd, resources_wd)

    return resources_wd
