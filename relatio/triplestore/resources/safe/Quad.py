
from pydantic import Field
from rdflib import Namespace, URIRef
from typing import Any, Optional, Union

from .Model import Model
from .utils import get_safe_class
from ..Quad import Quad



class QuadModel(Model):
    """
    Quad model definition
    """

    subject:   Union[URIRef,      Any] = Field(..., description="Subject of quad")
    predicate: Union[URIRef,      Any] = Field(..., description="Predicate of quad")
    object:    Union[URIRef, str, Any] = Field(..., description="Object of quad")
    namespace: Optional[Namespace]     = Field(None, description="Named graph of quad")


def __new__(cls, subject, predicate, object_, **kwargs):

    # Check arguments types
    _ = QuadModel(subject=subject, 
                  predicate=predicate, 
                  object=object_, 
                  **kwargs)

    return super(SafeQuad, cls).__new__(cls, subject, predicate, object_, **kwargs)


SafeQuad = get_safe_class(class_name='SafeQuad',
                          class_model=QuadModel,  
                          super_class=Quad,
                          __new__=__new__)
