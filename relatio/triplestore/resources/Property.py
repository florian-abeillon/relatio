
from rdflib import (
    RDF, RDFS,
    Namespace, URIRef
)
from typing import Optional, Union

from .Quad import Quad
from .Resource import Resource
from .ResourceStore import ResourceStore
from .utils import to_pascal_case



class Property(Resource):
    """ 
    RDFS property
    """

    _format_label = staticmethod(to_pascal_case)


    def __init__(self, label:          str,
                       namespace:      Optional[Namespace]               = None,
                       resource_store: Optional[ResourceStore]           = None,
                       superproperty:  Union[URIRef, Resource]           = RDF.Property,
                       domain:         Optional[Union[URIRef, Resource]] = None,
                       range:          Optional[Union[URIRef, Resource]] = None        ):
                       
        # If resource is already set, do not set it
        if self.is_set():
            return

        super().__init__(label, namespace=namespace, resource_store=resource_store)

        self.add_quad(
            Quad( self, RDFS.subPropertyOf, superproperty )
        )

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
