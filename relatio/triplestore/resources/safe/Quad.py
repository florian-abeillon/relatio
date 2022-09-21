
from pydantic import Field
from rdflib import Namespace, URIRef
from typing import Any, Union

from .Model import Model
from ..Quad import Quad



class QuadModel(Model):
    """
    Quad model definition
    """

    subject:   Union[URIRef,      Any] = Field(..., description="Subject of quad")
    predicate: Union[URIRef,      Any] = Field(..., description="Predicate of quad")
    object:    Union[URIRef, str, Any] = Field(..., description="Object of quad")
    namespace: Namespace               = Field(None, description="Named graph of quad")



class SafeQuad(Quad):
    """ 
    Safe RDF quad 
    """

    def __new__(cls, subject, predicate, object_, namespace = None):

        # Check arguments types
        _ = QuadModel(subject=subject, 
                      predicate=predicate, 
                      object=object_, 
                      namespace=namespace)

        return super().__new__(cls, subject, predicate, object_, namespace=namespace)
