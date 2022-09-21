
from pydantic import Field
from typing import List

from .Model import Model
from .Resource import Resource
from ..ResourceStore import ResourceStore



class ResourceStoreModel(Model):
    """
    ResourceStore model definition
    """

    resources: List[Resource] = Field(default_factory=list,  
                                      description="List of Resources")



class SafeResourceStore(ResourceStore):
    """ 
    Store of resources to be filled into triplestore 
    """

    def __init__(self, resources = []):

        # Check arguments types
        _ = ResourceStoreModel(resources=resources)

        return super().__init__(resources=resources)
