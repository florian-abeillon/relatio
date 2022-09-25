
from pydantic import Field
from rdflib import RDFS, Namespace, URIRef
from typing import Optional, Union

from .Model import Model
from .Quad import Quad
from .Resource import Resource
from .ResourceStore import ResourceStore
from .utils import to_pascal_case



class ClassModel(Model):
    """
    Class model definition
    """

    label:          str                     = Field(...,        description="Label of class")
    namespace:      Optional[Namespace]     = Field(None,       description="Named graph of class")
    resource_store: Optional[ResourceStore] = Field(None,       description="ResourceStore to put class into")
    superclass:     Union[URIRef, Resource] = Field(RDFS.Class, description="Super-class of class")




class Class(Resource):
    """ 
    RDFS class
    """

    _format_label = staticmethod(to_pascal_case)
    _type = RDFS.Class


    def __new__(cls, label, **kwargs):

        # Check arguments types
        _ = ClassModel(label=label, **kwargs)
        # Remove useless kwarg
        _ = kwargs.pop('superclass', None)

        return super().__new__(cls, label, **kwargs)


    def __init__(self, label:          str,
                       namespace:      Optional[Namespace]     = None,
                       resource_store: Optional[ResourceStore] = None,
                       superclass:     Union[URIRef, Resource] = RDFS.Class):
        
        # If resource is already set, do not set it
        if self.is_set():
            return

        super().__init__(label, namespace=namespace, resource_store=resource_store)
        
        self.add_quad(
            Quad( self, RDFS.subClassOf, superclass )
        )
