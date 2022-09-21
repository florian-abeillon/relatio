
from rdflib import OWL, Namespace
from typing import Optional

from .DefaultInstance import DefaultInstance
from .resources import RELATION
from ..namespaces import DEFAULT
from ..resources import (
    PropertyInstance, Quad,
    ResourceStore
)



class Relation(DefaultInstance, PropertyInstance):
    """ 
    Relation between entities
    """

    _format_label = staticmethod(lambda label: str(label).lower())
    _type = RELATION


    def __init__(self, label:          str,
                       namespace:      Namespace               = DEFAULT,
                       resource_store: Optional[ResourceStore] = None,
                       iri:            str                     = ""     ):

        super().__init__(label, namespace=namespace, resource_store=resource_store, iri=iri)

        # If resource is already set, do not set it
        if self.is_set():
            return

        # Connect to the negative form of self
        label_neg = label[4:] if label.startswith('not ') else 'not ' + label
        self_neg = Relation(label_neg, namespace=namespace, resource_store=resource_store)
        self.add_quads([
            Quad( self,     OWL.inverseOf, self_neg ),
            Quad( self_neg, OWL.inverseOf, self     )
        ])
