
from pydantic import Field
from rdflib import RDF, Namespace, URIRef
from typing import Optional, Union

from .Model import Model
from .Resource import Resource
from .ResourceStore import ResourceStore
from ..Property import Property




class PropertyModel(Model):
    """
    Property model definition
    """

    label:          str                     = Field(...,          description="Label of property")
    namespace:      Optional[Namespace]     = Field(None,         description="Named graph of property")
    resource_store: Optional[ResourceStore] = Field(None,         description="ResourceStore to put property into")
    superproperty:  Union[URIRef, Resource] = Field(RDF.Property, description="Super-property of property")
    domain:         Optional[URIRef]        = Field(None,         description="Domain of property")
    range:          Optional[URIRef]        = Field(None,         description="Range of property")



class SafeProperty(Property):
    """ 
    Safe RDFS property
    """

    def __init__(self, label, namespace = None, resource_store = None, superproperty = RDF.Property, domain = None, range = None):

        # Check arguments types
        _ = PropertyModel(label=label,
                          namespace=namespace,
                          resource_store=resource_store,
                          superproperty=superproperty,
                          domain=domain,
                          range=range)
                       
        super().__init__(label, namespace=namespace, resource_store=resource_store, superproperty=superproperty, domain=domain, range=range)
