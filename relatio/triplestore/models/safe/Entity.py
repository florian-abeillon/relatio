
from ..Entity import Entity
from ...resources.safe import (
    ClassInstanceModel, ClassInstance, 
    get_safe_class
)

            

class EntityModel(ClassInstanceModel):
    """
    Entity model definition
    """
    pass


SafeEntity = get_safe_class(class_name='SafeEntity', 
                           class_model=EntityModel,  
                           super_class=Entity, 
                           super_super_class=ClassInstance)
