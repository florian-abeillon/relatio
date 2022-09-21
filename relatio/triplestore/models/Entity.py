
from rdflib import Namespace

from .DefaultInstance import DefaultInstance
from .resources import CONTAINS, ENTITY
from ..resources import (
    ClassInstance, PropertyInstance, 
    Quad
)



class Entity(DefaultInstance, ClassInstance):
    """ 
    Entity, ie. a concept
    """

    _type = ENTITY


    def add_partOf(self, partOf_instance: ClassInstance) -> None:
        """ 
        Add partOf instance of self
        """
        if self.label.lower() != partOf_instance.label.lower():
            self.add_quad(
                Quad( self, CONTAINS, partOf_instance, namespace=partOf_instance._namespace )
            )


    def add_object(self, relation:  PropertyInstance, 
                         object_:   ClassInstance,
                         namespace: Namespace       ) -> None:
        """ 
        Add relation of self to an object 
        """
        self.add_quad(
            Quad( self, relation, object_, namespace=namespace )
        )
