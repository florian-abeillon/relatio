
from .Instance import InstanceModel, SafeInstance
from .utils import get_safe_class
from ..ClassInstance import ClassInstance



class ClassInstanceModel(InstanceModel):
    """
    RDFS class instance model definition
    """
    pass


SafeClassInstance = get_safe_class(class_name='SafeClassInstance', 
                                   class_model=ClassInstanceModel,  
                                   super_class=ClassInstance, 
                                   super_super_class=SafeInstance)
