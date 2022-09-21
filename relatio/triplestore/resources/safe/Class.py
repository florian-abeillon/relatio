
from pydantic import Field
from rdflib import RDFS, Namespace, URIRef
from typing import Optional, Union

from .Model import Model
from .Resource import Resource
from .ResourceStore import ResourceStore
from ..Class import Class



class ClassModel(Model):
    """
    Class model definition
    """

    label:          str                     = Field(...,        description="Label of class")
    namespace:      Optional[Namespace]     = Field(None,       description="Named graph of class")
    resource_store: Optional[ResourceStore] = Field(None,       description="ResourceStore to put class into")
    superclass:     Union[URIRef, Resource] = Field(RDFS.Class, description="Super-class of class")



class SafeClass(Class):
    """ 
    Safe RDFS class
    """
    
    def __init__(self, label, namespace = None, resource_store = None, superclass = RDFS.Class):

        # Check arguments types
        _ = ClassModel(label=label,
                       namespace=namespace,
                       resource_store=resource_store,
                       superclass=superclass)
        
        super().__init__(label, namespace=namespace, resource_store=resource_store, superclass=superclass)
