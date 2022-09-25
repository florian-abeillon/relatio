
from pydantic import Field
from rdflib import Dataset, Literal, Namespace, URIRef
from typing import Any, Optional, Union

from .Model import Model



class QuadModel(Model):
    """
    Quad model definition
    """

    subject:   Union[URIRef,      Any] = Field(..., description="Subject of quad")
    predicate: Union[URIRef,      Any] = Field(..., description="Predicate of quad")
    object:    Union[URIRef, str, Any] = Field(..., description="Object of quad")
    namespace: Optional[Namespace]     = Field(None, description="Named graph of quad")




class Quad(tuple):
    """ 
    RDF quad 
    """

    def __new__(cls, subject:   Union[URIRef,      Any], 
                     predicate: Union[URIRef,      Any], 
                     object_ :  Union[URIRef, str, Any],
                     namespace: Optional[Namespace]     = None):

        # Check arguments types
        _ = QuadModel(subject=subject, predicate=predicate, object=object_, namespace=namespace)

        # If no namespace was passed, get namespace of subject
        if namespace is None:
            assert hasattr(subject, '_namespace'), f"{subject} has no '_namespace' attribute"
            namespace = subject._namespace

        # Get IRI from resources
        subject   = cls.get_iri(subject)
        predicate = cls.get_iri(predicate)
        object_   = cls.get_iri(object_) if not isinstance(object_, str) or isinstance(object_, URIRef) else Literal(object_)

        quad = ( subject, predicate, object_, namespace)
        return super().__new__(cls, quad)


    @staticmethod
    def get_iri(v) -> URIRef:
        if not isinstance(v, URIRef):
            assert hasattr(v, 'iri'), f"{v} has no 'iri' attribute"
            v = v.iri
            assert isinstance(v, URIRef), f"{v} (type {type(v)}) is not of type 'URIRef'"
        return v
        

    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with quad 
        """
        ds.add(self)
