
from rdflib import RDF, RDFS, Namespace, URIRef
from typing import Optional

from .Instance import Instance
from .Quad import Quad
from .ResourceStore import ResourceStore
from .utils import to_camel_case



class PropertyInstance(Instance):
    """ 
    Instance of a RDFS property 
    """

    _format_label = staticmethod(to_camel_case)
    _type = RDF.Property


    def __init__(self, label:          str,
                       namespace:      Optional[Namespace]     = None,
                       resource_store: Optional[ResourceStore] = None,
                       iri:            str                     = ""  ,
                       domain:         Optional[URIRef]        = None,
                       range:          Optional[URIRef]        = None):

        super().__init__(label, namespace=namespace, resource_store=resource_store, iri=iri)

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
