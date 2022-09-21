
from rdflib import Namespace
from typing import Optional

from ..Entity import Entity
from ...resources.safe import ClassInstanceModel, ResourceStore

            

class EntityModel(ClassInstanceModel):
    """
    Entity model definition
    """
    pass



class SafeEntity(Entity):
    """ 
    Safe entity
    """

    def __init__(self, label:          str,
                       resource_store: ResourceStore,
                       namespace:      Optional[Namespace] = None,
                       iri:            str                 = ""  ):

        # Check arguments types
        _ = EntityModel(label=label,
                        resource_store=resource_store,
                        namespace=namespace,
                        iri=iri)

        super().__init__(label, resource_store, namespace=namespace, iri=iri)
