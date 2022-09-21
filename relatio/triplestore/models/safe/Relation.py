
from pydantic import Field
from rdflib import Namespace
from typing import Optional

from ...resources.safe import PropertyInstanceModel, ResourceStore
from ..Relation import Relation



class RelationModel(PropertyInstanceModel):
    """
    Relation model definition
    """

    is_pos: bool = Field(False, description="Whether relation is in its positive form")



class SafeRelation(Relation):
    """ 
    Safe relation between entities
    """

    def __init__(self, label:          str,
                       namespace:      Optional[Namespace]     = None,
                       resource_store: Optional[ResourceStore] = None,
                       iri:            str                     = ""  ,
                       is_pos:         bool                    = False):

        # Check arguments types
        _ = RelationModel(label=label,
                          namespace=namespace,
                          resource_store=resource_store,
                          iri=iri,
                          is_pos=is_pos)

        super().__init__(label, namespace=namespace, resource_store=resource_store, iri=iri)
