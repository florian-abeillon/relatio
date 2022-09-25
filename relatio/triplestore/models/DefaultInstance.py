
from argparse import Namespace
from typing import Optional
from rdflib import URIRef

from .resources import CONTAINS, HAS_LOWDIM
from ..namespaces import DEFAULT
from ..resources import (
    ClassInstance, Resource, 
    ResourceStore, Quad
)



class DefaultInstance:
    """
    Instance from default graph
    """

    _namespace = DEFAULT


    def __new__(cls, label:          str,
                     namespace:      Namespace               = DEFAULT,
                     resource_store: Optional[ResourceStore] = None   ):

        assert resource_store is not None, "Please provide a ResourceStore"
        return super().__new__(cls, label, namespace=namespace, resource_store=resource_store)


    @classmethod
    def generate_iri(cls, label:     str, 
                          namespace: Namespace = DEFAULT) -> URIRef:
        """ 
        Build unique resource identifier from label
        """
        type_ = cls._type.label
        return super().generate_iri(label, type_=type_, namespace=namespace)


    def add_partOf(self, partOf_instance: ClassInstance) -> None:
        """ 
        Add partOf instance of self
        """
        if self.label.lower() != partOf_instance.label.lower():
            self.add_quad(
                Quad( self, CONTAINS, partOf_instance, namespace=partOf_instance._namespace )
            )


    def set_lowDim(self, lowDim_instance: Resource) -> None:
        """ 
        Set lowDim instance of self
        """
        self.add_quad(
            Quad( self, HAS_LOWDIM, lowDim_instance )
        )
