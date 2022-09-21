
from pydantic import Field
from rdflib import URIRef
from typing import Optional

from .Instance import InstanceModel
from ..PropertyInstance import PropertyInstance



class PropertyInstanceModel(InstanceModel):
    """
    RDFS property instance model definition
    """

    domain: Optional[URIRef] = Field(None, description="Domain of property instance")
    range:  Optional[URIRef] = Field(None, description="Range of property instance")



class SafePropertyInstance(PropertyInstance):
    """ 
    Safe instance of a RDFS property 
    """

    def __init__(self, label namespace = None, resource_store = None, iri = "", domain = None, range = None):

        # Check arguments types
        _ = PropertyInstanceModel(label=label, 
                                  namespace=namespace, 
                                  resource_store=resource_store, 
                                  iri=iri,
                                  domain=domain,
                                  range=range)

        super().__init__(label, namespace=namespace, resource_store=resource_store, iri=iri, domain=domain, iri=iri)
