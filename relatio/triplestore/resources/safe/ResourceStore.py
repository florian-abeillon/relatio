
from pydantic import Field
from typing import List

from .Model import Model
from .Resource import Resource
from .utils import get_safe_class
from ..ResourceStore import ResourceStore



class ResourceStoreModel(Model):
    """
    ResourceStore model definition
    """

    resources: List[Resource] = Field(default_factory=list, description="List of Resources")


SafeResourceStore = get_safe_class(class_name='SafeResourceStore',
                                   class_model=ResourceStoreModel,  
                                   super_class=ResourceStore)
