
from pydantic import Field
from rdflib import RDF, RDFS, Namespace, URIRef
from typing import Optional, Union

from .Instance import Instance, InstanceModel
from .Property import Property
from .Quad import Quad
from .Resource import Resource
from .ResourceStore import ResourceStore
from .utils import to_camel_case



class PropertyInstanceModel(InstanceModel):
    """
    RDFS property instance model definition
    """

    domain: Optional[Union[URIRef, Resource]] = Field(None, description="Domain of property instance")
    range:  Optional[Union[URIRef, Resource]] = Field(None, description="Range of property instance")




class PropertyInstance(Instance):
    """ 
    Instance of a RDFS property 
    """

    _format_label = staticmethod(to_camel_case)
    _type = RDF.Property


    def __new__(cls, label, **kwargs):

        # Check arguments types
        _ = PropertyInstanceModel(label=label, **kwargs)
        # Remove useless kwargs
        _ = kwargs.pop('domain', None)
        _ = kwargs.pop('range',  None)

        return super().__new__(cls, label, **kwargs)


    def __init__(self, label:          str,
                       namespace:      Optional[Namespace]               = None,
                       resource_store: Optional[ResourceStore]           = None,
                       domain:         Optional[Union[URIRef, Resource]] = None,
                       range:          Optional[Union[URIRef, Resource]] = None):

        super().__init__(label, namespace=namespace, resource_store=resource_store)

        # If resource is already set, do not set it
        if self.is_set():
            return

        # If a domain is mentionned, add appropriate relation
        if domain is not None:
            self.add_quad(
                Quad( self, RDFS.domain, domain )
            )
            
        # If a range is mentionned, add appropriate relation
        if range is not None:
            self.add_quad(
                Quad( self, RDFS.range, range )
            )


    @classmethod
    def generate_iri(cls, label:     str, 
                          type_:     str                 = Property.__name__,
                          namespace: Optional[Namespace] = None             ) -> URIRef:
        """ 
        Build unique resource identifier from label
        """
        return super().generate_iri(label, type_=type_, namespace=namespace)
