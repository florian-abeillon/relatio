
from pydantic import Field
from rdflib import SKOS

import spacy

from .resources import TYPE
from ....namespaces import SPACY
from ....resources import (
    ClassInstance, Model,
    Quad, ResourceStore
)



class TypeModel(Model):
    """
    Instance from external source model definition
    """

    label:          str           = Field(...,  description="Label of type")
    resource_store: ResourceStore = Field(...,  description="ResourceStore to put type into")




class Type(ClassInstance):
    """ 
    SpaCy type
    """

    _format_label = staticmethod(lambda label: label.upper())
    _namespace = SPACY
    _type = TYPE


    def __new__(cls, label:          str, 
                     resource_store: ResourceStore):
        # Check arguments types
        _ = TypeModel(label=label, resource_store=resource_store)
        return super().__new__(cls, label, resource_store=resource_store)


    def __init__(self, label:          str, 
                       resource_store: ResourceStore):
                       
        super().__init__(label, resource_store=resource_store)

        # If resource is already set, do not set it
        if self.is_set():
            return

        description = spacy.explain(label)
        if description:
            self.add_quad(
                Quad( self, SKOS.definition, description )
            )
