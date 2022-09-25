
from spacy.tokens.span import Span
from pydantic import Field
from rdflib import RDF

from .Type import Type
from ...models import ExternalEntity
from ....namespaces import SPACY
from ....resources import (
    Model, Quad, ResourceStore
)



class Ent:

    def __init__(self, ent: Span):
        self._label = str(ent)
        self.label_ = ent.label_

    def __str__(self) -> str:
        return self._label



class SpacyEntityModel(Model):
    """
    SpaCy named entity model definition
    """

    ent:               Ent           = Field(..., description="Span object returned by module")
    resource_store:    ResourceStore = Field(..., description="ResourceStore to search named entity in")
    resource_store_sp: ResourceStore = Field(..., description="ResourceStore to put named entity into if it is not in resource_store")




class SpacyEntity(ExternalEntity):
    """ 
    SpaCy named entity 
    """

    _namespace = SPACY
    

    def __new__(cls, ent:               Ent, 
                     resource_store:    ResourceStore,
                     resource_store_sp: ResourceStore):

        # Check arguments types
        _ = SpacyEntityModel(ent=ent, resource_store=resource_store, resource_store_sp=resource_store_sp)
        
        return super().__new__(cls, str(ent), resource_store, resource_store_ext=resource_store_sp)


    def __init__(self, ent:               Ent, 
                       resource_store:    ResourceStore,
                       resource_store_sp: ResourceStore):

        super().__init__(str(ent), resource_store, resource_store_ext=resource_store_sp)

        # If SpacyEntity is not already set, set it
        if not hasattr(self, '_is_sp_set'):

            # TODO: Right label_, even if other files imported?
            if ent.label_:
                _class = Type(ent.label_, resource_store_sp)
                self.add_quad(
                    # TODO: namespace needed?
                    # Quad( self, RDF.type, _class )
                    Quad( self, RDF.type, _class, namespace=SPACY )
                )

            self._is_sp_set = True
