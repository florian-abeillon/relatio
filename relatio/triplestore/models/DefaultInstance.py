
from argparse import Namespace
from typing import Optional
from rdflib import URIRef

from .resources import HAS_LOWDIM
from ..namespaces import DEFAULT
from ..resources import Resource, ResourceStore, Quad
from ..resources.utils import get_hash



class DefaultInstance:
    """
    Instance from default graph
    """

    _namespace = DEFAULT


    def __init__(self, label:          str,
                       namespace:      Namespace               = DEFAULT,
                       resource_store: Optional[ResourceStore] = None,
                       iri:            str                     = ""     ):

        assert resource_store is not None, "Please provide a ResourceStore"
        super().__init__(label, namespace=namespace, resource_store=resource_store, iri=iri)


    @classmethod
    def generate_iri(cls, label:     str, 
                          namespace: Optional[Namespace] = DEFAULT) -> URIRef:
        """ 
        Build unique resource identifier from label
        """
        label = cls._format_label(label)
        key = f"{cls.__name__}/{get_hash(label)}"

        if namespace is None:
            namespace = cls._namespace
        return namespace[key]


    def set_lowDim(self, lowDim_instance: Resource) -> None:
        """ 
        Set lowDim instance of self
        """
        self.add_quad(
            Quad( self, HAS_LOWDIM, lowDim_instance )
        )
