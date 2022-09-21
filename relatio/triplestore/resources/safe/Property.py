
from pydantic import Field
from rdflib import RDF, Namespace, URIRef
from typing import Optional, Union

from .Model import Model
from .Resource import SafeResource
from .ResourceStore import SafeResourceStore
from .utils import get_safe_class
from ..Property import Property



class PropertyModel(Model):
    """
    Property model definition
    """

    label:          str                                   = Field(...,          description="Label of property")
    namespace:      Optional[Namespace]                   = Field(None,         description="Named graph of property")
    resource_store: Optional[SafeResourceStore]           = Field(None,         description="ResourceStore to put property into")
    superproperty:  Union[URIRef, SafeResource]           = Field(RDF.Property, description="Super-property of property")
    domain:         Optional[Union[URIRef, SafeResource]] = Field(None,         description="Domain of property")
    range:          Optional[Union[URIRef, SafeResource]] = Field(None,         description="Range of property")


SafeProperty = get_safe_class(class_name='SafeProperty', 
                              class_model=PropertyModel,  
                              super_class=Property, 
                              super_super_class=SafeResource)
