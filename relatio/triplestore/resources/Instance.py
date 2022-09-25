
from pydantic import Field
from rdflib import RDF, Namespace, URIRef
from typing import Optional

from .Model import Model
from .Quad import Quad
from .Resource import Resource
from .ResourceStore import ResourceStore
from .utils import get_hash


class InstanceModel(Model):
    """
    RDFS instance model definition
    """

    label:          str                     = Field(...,  description="Label of class instance")
    namespace:      Optional[Namespace]     = Field(None, description="Named graph of class instance")
    resource_store: Optional[ResourceStore] = Field(None, description="ResourceStore to put instance into")



class Instance(Resource):
    """ 
    RDFS instance
    """

    _type = None


    def __new__(cls, label, **kwargs):
        # Check arguments types
        _ = InstanceModel(label=label, **kwargs)
        return super().__new__(cls, label, **kwargs)


    def __init__(self, label:          str,
                       namespace:      Optional[Namespace]     = None,
                       resource_store: Optional[ResourceStore] = None):

        # If resource is already set, do not set it
        if self.is_set():
            return

        super().__init__(label, namespace=namespace, resource_store=resource_store)

        assert self._type is not None, "Please provide a type to instance"
        self.add_quad(
            Quad( self, RDF.type, self._type )
        )


    @classmethod
    def generate_iri(cls, label:     str, 
                          type_:     str                 = "",
                          namespace: Optional[Namespace] = None) -> URIRef:
        """ 
        Build unique resource identifier from label
        """
        label = cls._format_label(label)
        if not type_:
            type_ = cls.__name__
        key = f"{type_}/{get_hash(label)}"
        return super().generate_iri(key, namespace=namespace)
