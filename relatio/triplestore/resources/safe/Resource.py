
from pydantic import Field
from rdflib import Namespace
from typing import Optional

from .Model import Model
from ..Resource import Resource



class ResourceModel(Model):
    """
    Resource model definition
    """

    label:     str                 = Field(...,  description="Label of resource")
    namespace: Optional[Namespace] = Field(None, description="Named graph of class instance")
    iri:       str                 = Field("",   description="IRI of resource")



class SafeResource(Resource):
    """ 
    Safe base triplestore resource 
    """

    def __init__(self, label, namespace = None, iri = ""):

        # Check arguments types
        _ = ResourceModel(label=label,
                          namespace=namespace,
                          iri=iri)

        return super().__init__(label, namespace=namespace)
