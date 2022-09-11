
from rdflib import URIRef
from spacy.tokens.span import Span
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError
from typing import List, Union
from urllib.error import HTTPError

import os
import re
import time

from ..models_ext import ExtEntity, ExtRelation
from ..utils import query_triplestore
from ...namespaces import WIKIDATA
from ...models import ENTITY, RELATION, Quad
from ...resources import Class, Property, ResourceStore


URL = 'https://query.wikidata.org/sparql'

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'query.sparql')
with open(path) as f:
    QUERY = f.read()


# Define Wikidata class and property
ENTITY_WD = Class('Entity', WIKIDATA, super_class=ENTITY)

RELATION_WD = Property('relation',    WIKIDATA, super_property=RELATION)
WD_IRI      = Property('wikidataIri', WIKIDATA                         )

MODELS = [ 
    ENTITY_WD, RELATION_WD, WD_IRI
]



class WdInstance:
    """ 
    Wikidata instance of a class/property
    """

    _namespace = WIKIDATA


    def __new__(cls, ent:               Union[str, Span], 
                     resource_store:    ResourceStore,
                     resource_store_wd: ResourceStore,
                     **kwargs                           ):

        return super().__new__(cls, ent,
                                    resource_store, 
                                    resource_store_ext=resource_store_wd)
    

    def __init__(self, ent:               Union[str, Span], 
                       resource_store:    ResourceStore,
                       resource_store_wd: ResourceStore,
                       iri_wd:            str              = ""):

        iri_wd = URIRef(iri_wd) if iri_wd else self.generate_wd_iri(ent.kb_id_)
        super().__init__(ent, resource_store, iri=iri_wd)

        # If Wikidata entity is not already set, set it
        if not hasattr(self, '_wd_set'):

            self._iri_wd = iri_wd
            self._quads.append(
                Quad( self, WD_IRI, self._iri_wd )
            )

            self._wd_set = True


    @staticmethod
    def generate_wd_iri(id_wd: str) -> URIRef:
        """ 
        Build unique resource identifier from id_wd
        """
        return URIRef(WIKIDATA + id_wd)



class Relation(WdInstance, ExtRelation): 
    """ 
    Wikidata relation 
    """

    _type = RELATION_WD
                  


class Entity(WdInstance, ExtEntity):
    """ 
    Wikidata entity 
    """

    _type = ENTITY_WD


    def query_triplestore(self) -> List[dict]:
        """
        Queries Wikidata triplestore
        """

        # Iterate over each set of relation/objects returned from Wikidata
        query = QUERY.format(iri=self._iri_wd)

        try:
            res = query_triplestore(URL, query)

        except EndPointInternalError as err:
            # TODO: Send requests with LIMIT/OFFSET
            # Timeout from Wikidata
            print(f'Error: {err.msg} (timeout) when querying Wikidata for "{self.label}" ({self._iri_wd})')
            res = []

        except HTTPError as err:
            if err.getcode() == 429:
                # If too many requests, wait for a bit and then try again
                print("Sleeping for", err.headers['Retry-After'], "seconds..")
                start = time.time()
                time.sleep(err.headers['Retry-After'])
                print(time.time() - start)
                res = self.query_triplestore()
            else:
                # If other error, print it
                print('Error:', str(err))
                res = []

        return res

                
    @staticmethod
    def clean_res(res: List[dict]) -> List[dict]:
        """ 
        Remove uninformative Wikidata attributes 
        """

        res_clean = []

        # TODO: To improve
        for r in res:

            # Whether to keep or not result
            if (
                # If attribute is an ID, or
                re.findall("ID( *\(.*\))? *$", r['predicate']['label']) or
                # If attribute label is in uppercase (likely not informative), or
                r['predicate']['label'].isupper()
            ):
                continue

            for key in [ 'objects', 'attributes', 'subjects' ]:
                r[key] = [
                    el for el in r[key]
                    if (
                        # If attribute is not a mixture of letters and numbers, and
                        ( el['label'].isalpha() or el['label'].isnumeric() ) and
                        # If attribute is likely informative (not a Wikidata ID, or like 'Category:', 'Template:', etc.)
                        not re.match(r"Q\d+",             el['label']) and 
                        not re.match(r"[A-Z][a-z]+\:\w+", el['label'])
                    )
                ]

            res_clean.append(r)

        return res_clean


    def enrich_entity(self, resource_store:    ResourceStore,
                            resource_store_wd: ResourceStore) -> None:
        """ 
        Retrieve objects/attributes from Wikidata database 
        """

        # Query Wikidata
        res = self.query_triplestore()
        res = self.clean_res(res)

        for r in res:

            # Build and add relation property
            relation = Relation(r['predicate']['label'], 
                                resource_store, 
                                resource_store_wd,
                                iri_wd=r['predicate']['iri'])

            # Add objects to entity
            for object_ in r['objects']:

                object_ = Entity(object_['label'], 
                                 resource_store, 
                                 resource_store_wd,
                                 iri_wd=object_['iri'])
                self._quads.append(
                    Quad( self, relation, object_ )
                )

            # Add attributes to entity
            for attribute in r['attributes']:
                self._quads.append(
                    Quad( self, relation, attribute['label'] )
                )

            # Add entity to subjects
            for subject in r['subjects']:

                subject = Entity(subject['label'], 
                                 resource_store, 
                                 resource_store_wd,
                                 iri_wd=subject['iri'])
                subject._quads.append(
                    Quad( subject, relation, self, namespace=WIKIDATA )
                )
