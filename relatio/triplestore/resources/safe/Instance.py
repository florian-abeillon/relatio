
from pydantic import Field
from rdflib import Namespace
from typing import Optional

from .Model import Model
from .ResourceStore import ResourceStore
from ..Instance import Instance



class InstanceModel(Model):
    """
    RDFS instance model definition
    """

    label:          str                     = Field(...,  description="Label of class instance")
    namespace:      Optional[Namespace]     = Field(None, description="Named graph of class instance")
    resource_store: Optional[ResourceStore] = Field(None,  description="ResourceStore to put instance into")
    iri:            str                     = Field("",   description="IRI of class instance")



class SafeInstance(Instance):
    """ 
    Safe RDFS instance
    """

    def __new__(cls, label, resource_store, namespace = None, iri = ""):

        # Check arguments types
        _ = InstanceModel(label=label, 
                          namespace=namespace, 
                          resource_store=resource_store, 
                          iri=iri)
                          
        return super().__new__(cls, label, namespace=namespace, resource_store=resource_store, iri=iri)
