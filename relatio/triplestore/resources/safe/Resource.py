
from pydantic import Field
from rdflib import Namespace
from typing import Optional

from .Model import Model
from .utils import get_safe_class
from ..Resource import Resource



class ResourceModel(Model):
    """
    Resource model definition
    """

    label:          str                 = Field(...,  description="Label of resource")
    namespace:      Optional[Namespace] = Field(None, description="Named graph of class instance")
    resource_store: Optional[dict]      = Field(None, description="ResourceStore to put resource into")
    iri:            str                 = Field("",   description="IRI of resource")


SafeResource = get_safe_class(class_name='SafeResource',
                              class_model=ResourceModel,  
                              super_class=Resource)
