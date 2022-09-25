
from pydantic import Field
from typing import Optional

from ...namespaces import DEFAULT
from ...resources import Model, ResourceStore




class ExternalInstanceModel(Model):
    """
    Instance from external source model definition
    """

    label:              str                     = Field(...,  description="Label of class")
    resource_store:     ResourceStore           = Field(...,  description="ResourceStore to search named entity in")
    resource_store_ext: Optional[ResourceStore] = Field(None, description="ResourceStore to put named entity into if it is not in resource_store")



class ExternalInstance:
    """ 
    Instance from external source
    """

    def __new__(cls, label:              str,
                     resource_store:     ResourceStore,
                     resource_store_ext: Optional[ResourceStore] = None):

        # Check arguments types
        _ = ExternalInstanceModel(label=label, resource_store=resource_store, resource_store_ext=resource_store_ext)

        # Get hash in default namespace
        hash_default = hash(cls.generate_iri(label, namespace=DEFAULT))

        # If resource is already in resource_store, return it
        if hash_default in resource_store:
            instance = resource_store[hash_default]
            instance.__class__ = cls
            return instance

        # Otherwise, it must be added to resource_store_ext instead
        return super().__new__(cls, label, resource_store=resource_store_ext)


    def __init__(self, label:              str,
                       resource_store:     ResourceStore,
                       resource_store_ext: Optional[ResourceStore] = None):

        super().__init__(label, resource_store=resource_store_ext)
