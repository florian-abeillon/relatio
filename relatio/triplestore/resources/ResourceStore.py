
from pydantic import Field
from rdflib import Dataset
from typing import Any, List, Optional

from .Model import Model



class ResourceStoreModel(Model):
    """
    ResourceStore model definition
    """

    resources: List[Any] = Field(default_factory=list, description="List of Resources")



class ResourceStore(dict):
    """ 
    Store of resources to be filled into triplestore 
    """

    def __new__(cls, resources: List[Any] = []):
        # Check arguments types
        _ = ResourceStoreModel(resources=resources)
        return super().__new__(cls)


    def __init__(self, resources: List[Any] = []):
        for resource in resources:
            self.add(resource)


    def add(self, resource: Any,
                  key:      Optional[int] = None) -> None:
        """ 
        Add a resource to self 
        """
        if key is None:
            key = resource
        self[key] = resource


    def get_or_add(self, resource: Any) -> Any:
        """ 
        Get a resource from self, or add it to self if necessary 
        """
        if not resource in self:
            self.add(resource)
        return self[resource]


    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with every resource from self 
        """
        for resource in self.values():
            resource.to_graph(ds)
