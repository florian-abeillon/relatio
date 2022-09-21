
from pydantic import Field
from rdflib import URIRef
from typing import Optional, Union

from .Instance import InstanceModel, SafeInstance
from .Resource import SafeResource
from .utils import get_safe_class
from ..PropertyInstance import PropertyInstance



class PropertyInstanceModel(InstanceModel):
    """
    RDFS property instance model definition
    """

    domain: Optional[Union[URIRef, SafeResource]] = Field(None, description="Domain of property instance")
    range:  Optional[Union[URIRef, SafeResource]] = Field(None, description="Range of property instance")


SafePropertyInstance = get_safe_class(class_name='SafePropertyInstance', 
                                      class_model=PropertyInstanceModel,  
                                      super_class=PropertyInstance, 
                                      super_super_class=SafeInstance)
