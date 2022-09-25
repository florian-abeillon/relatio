
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError
from typing import List
from urllib.error import HTTPError

import re
import time

from .WikidataInstance import WikidataInstance
from .WikidataRelation import WikidataRelation
from .utils import QUERY, URL, query_triplestore
from ...models import ExternalEntity
from ....namespaces import WIKIDATA
from ....resources import Quad, ResourceStore




class WikidataEntity(WikidataInstance, ExternalEntity):
    """ 
    Wikidata entity 
    """

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
                time.sleep(int(err.headers['Retry-After']))
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
            relation = WikidataRelation(r['predicate']['label'], 
                                        resource_store, 
                                        resource_store_wd,
                                        iri_wd=r['predicate']['iri'])

            # Add objects to entity
            for object_ in r['objects']:

                object_ = WikidataEntity(object_['label'], 
                                         resource_store, 
                                         resource_store_wd,
                                         iri_wd=object_['iri'])
                self.add_quad(
                    Quad( self, relation, object_, namespace=WIKIDATA )
                )

            # Add attributes to entity
            for attribute in r['attributes']:
                self.add_quad(
                    Quad( self, relation, attribute['label'], namespace=WIKIDATA )
                )

            # Add entity to subjects
            for subject in r['subjects']:

                subject = WikidataEntity(subject['label'], 
                                         resource_store, 
                                         resource_store_wd,
                                         iri_wd=subject['iri'])
                subject.add_quad(
                    Quad( subject, relation, self, namespace=WIKIDATA )
                )
