
from rdflib import RDFS

from .Instance import Instance


class ClassInstance(Instance):
    """ 
    Instance of a RDFS class
    """

    _format_label = staticmethod(lambda label: str(label).capitalize())
    _type = RDFS.Class
