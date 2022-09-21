
from pydantic import Field

from ..Relation import Relation
from ...resources.safe import (
    PropertyInstanceModel, PropertyInstance, 
    get_safe_class
)



class RelationModel(PropertyInstanceModel):
    """
    Relation model definition
    """

    is_pos: bool = Field(False, description="Whether relation is in its positive form")


SafeRelation = get_safe_class(class_name='SafeRelation', 
                              class_model=RelationModel,  
                              super_class=Relation, 
                              super_super_class=PropertyInstance)
