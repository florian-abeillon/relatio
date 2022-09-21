
from pydantic import Field
from rdflib import RDFS, Namespace, URIRef
from typing import Optional, Union

from .Model import Model
from .Resource import SafeResource
from .ResourceStore import SafeResourceStore
from .utils import get_safe_class
from ..Class import Class



class ClassModel(Model):
    """
    Class model definition
    """

    label:          str                         = Field(...,        description="Label of class")
    namespace:      Optional[Namespace]         = Field(None,       description="Named graph of class")
    resource_store: Optional[SafeResourceStore] = Field(None,       description="ResourceStore to put class into")
    superclass:     Union[URIRef, SafeResource] = Field(RDFS.Class, description="Super-class of class")


SafeClass = get_safe_class(class_name='SafeClass', 
                           class_model=ClassModel,  
                           super_class=Class, 
                           super_super_class=SafeResource)
