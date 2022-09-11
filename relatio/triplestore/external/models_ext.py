
from copy import deepcopy
from typing import Optional

from ..models import Entity, Instance, Relation
from ..resources import ResourceStore



class ExtInstance(Instance):
    """ 
    Instance from external source
    """

    def __new__(cls, label:              str,
                     resource_store:     ResourceStore,
                     resource_store_ext: Optional[ResourceStore] = None):

        # Get hash in default namespace
        hash_default = hash(super().generate_iri(label, default=True))

        # If resource is already in resource_store, return it
        if hash_default in resource_store:
            instance = resource_store[hash_default]
            instance.__class__ = cls
            return instance

        # Otherwise, it must be added to resource_store_ext instead
        return super().__new__(cls, label, resource_store_ext)
                                    
    
    def __init__(self, label: str,
                       **kwargs  ):

        # If instance is not already set, set it
        if not self.__dict__:
            super().__init__(label, **kwargs)



# Change base classes inheritance
ExtEntity = deepcopy(Entity)
ExtEntity.__bases__ = (ExtInstance,)

ExtRelation = deepcopy(Relation)
ExtRelation.__bases__ = (ExtInstance,)
