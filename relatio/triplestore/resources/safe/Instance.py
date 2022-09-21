
from pydantic import Field
from rdflib import Namespace
from typing import Optional

from .Model import Model
from .Resource import SafeResource
from .ResourceStore import SafeResourceStore
from .utils import get_safe_class
from ..Instance import Instance



class InstanceModel(Model):
    """
    RDFS instance model definition
    """

    label:          str                         = Field(...,  description="Label of class instance")
    namespace:      Optional[Namespace]         = Field(None, description="Named graph of class instance")
    resource_store: Optional[SafeResourceStore] = Field(None, description="ResourceStore to put instance into")
    iri:            str                         = Field("",   description="IRI of class instance")


SafeInstance = get_safe_class(class_name='SafeInstance', 
                              class_model=InstanceModel,  
                              super_class=Instance, 
                              super_super_class=SafeResource)
