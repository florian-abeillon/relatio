
from rdflib import Namespace

from .DefaultInstance import DefaultInstance
from .resources import ENTITY
from ..resources import (
    ClassInstance, ClassInstanceModel, 
    PropertyInstance, Quad
)


class EntityModel(ClassInstanceModel):
    """
    Entity model definition
    """
    pass



class Entity(DefaultInstance, ClassInstance):
    """ 
    Entity, ie. a concept
    """

    _type = ENTITY


    def __new__(cls, label, **kwargs):
        # Check arguments types
        _ = EntityModel(label=label, **kwargs)
        return super().__new__(cls, label, **kwargs)


    def add_object(self, relation:  PropertyInstance, 
                         object_:   ClassInstance,
                         namespace: Namespace       ) -> None:
        """ 
        Add relation of self to an object 
        """
        self.add_quad(
            Quad( self, relation, object_, namespace=namespace )
        )
