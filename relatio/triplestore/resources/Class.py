
from rdflib import RDFS, Namespace, URIRef
from typing import Optional, Union

from .Quad import Quad
from .Resource import Resource
from .ResourceStore import ResourceStore
from .utils import to_pascal_case



class Class(Resource):
    """ 
    RDFS class
    """

    _format_label = staticmethod(to_pascal_case)
    _type = RDFS.Class


    def __init__(self, label:      str,
                       namespace:  Optional[Namespace]         = None,
                       resource_store: Optional[ResourceStore] = None,
                       superclass: Union[URIRef, Resource]     = RDFS.Class):
        
        # If resource is already set, do not set it
        if self.is_set():
            return

        super().__init__(label, namespace=namespace, resource_store=resource_store)
        
        self.add_quad(
            Quad( self, RDFS.subClassOf, superclass )
        )
