
from rdflib import RDF, SKOS
from spacy.tokens.span import Span

import spacy

from ..models_ext import ExtEntity
from ...models import Instance
from ...namespaces import SPACY
from ...resources import (
    Class, Quad, ResourceStore
)


# Define SpaCy models
TYPE = Class('Type', namespace=SPACY)

MODELS = [
    TYPE
]



class Type(Instance):
    """ 
    SpaCy named entity class 
    """

    _format_label = staticmethod(lambda label: str(label).upper())
    _namespace = SPACY
    _type = TYPE


    def __init__(self, label:          str, 
                       resource_store: ResourceStore):
                       
        super().__init__(label)

        description = spacy.explain(label)
        if description:
            self._quads.append(
                Quad( self, SKOS.definition, description )
            )



class Entity(ExtEntity):
    """ 
    SpaCy named entity 
    """

    _namespace = SPACY
    

    def __new__(cls, ent:               Span, 
                     resource_store:    ResourceStore,
                     resource_store_sp: ResourceStore):

        return super().__new__(cls, ent, 
                                    resource_store, 
                                    resource_store_ext=resource_store_sp)


    def __init__(self, ent:               Span, 
                       resource_store:    ResourceStore,
                       resource_store_sp: ResourceStore):

        super().__init__(ent, resource_store)

        # If SpaCy instance is not already set, set it
        if not hasattr(self, '_sp_set'):

            # TODO: Right label_, even if other files imported?
            if ent.label_:
                _class = Type(ent.label_, resource_store_sp)
                self._quads.append(
                    Quad( self, RDF.type, _class, namespace=SPACY )
                )

            self._sp_set = True
