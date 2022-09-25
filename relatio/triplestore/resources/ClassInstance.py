
from rdflib import RDFS, Namespace, URIRef
from typing import Optional

from .Class import Class
from .Instance import Instance, InstanceModel


class ClassInstanceModel(InstanceModel):
    """
    RDFS class instance model definition
    """
    pass



class ClassInstance(Instance):
    """ 
    Instance of a RDFS class
    """

    _format_label = staticmethod(lambda label: label.capitalize())
    _type = RDFS.Class


    def __new__(cls, label, **kwargs):
        # Check arguments types
        _ = ClassInstanceModel(label=label, **kwargs)
        return super().__new__(cls, label, **kwargs)


    @classmethod
    def generate_iri(cls, label:     str, 
                          type_:     str                 = Class.__name__,
                          namespace: Optional[Namespace] = None          ) -> URIRef:
        """ 
        Build unique resource identifier from label
        """
        return super().generate_iri(label, type_=type_, namespace=namespace)
