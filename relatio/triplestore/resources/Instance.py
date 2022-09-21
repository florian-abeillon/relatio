
from rdflib import RDF, Namespace
from typing import Optional

from .Quad import Quad
from .Resource import Resource
from .ResourceStore import ResourceStore



class Instance(Resource):
    """ 
    RDFS instance
    """

    _type = None


    def __init__(self, label:          str,
                       namespace:      Optional[Namespace]     = None,
                       resource_store: Optional[ResourceStore] = None,
                       iri:            str                     = ""  ,
                       **kwargs                                      ):

        # If resource is already set, do not set it
        if self.is_set():
            return

        super().__init__(label, namespace=namespace, resource_store=resource_store, iri=iri)

        assert self._type is not None, "Please provide a type to instance"
        self.add_quad(
            Quad( self, RDF.type, self._type )
        )
