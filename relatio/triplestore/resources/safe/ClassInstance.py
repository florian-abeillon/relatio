
from .Instance import InstanceModel
from ..ClassInstance import ClassInstance



class ClassInstanceModel(InstanceModel):
    """
    RDFS class instance model definition
    """
    pass



class SafeClassInstance(ClassInstance):
    """ 
    Safe instance of a RDFS class
    """

    def __init__(self, label, namespace = None, resource_store = None, iri = ""):

        # Check arguments types
        _ = ClassInstanceModel(label=label,
                               resource_store=resource_store,
                               namespace=namespace,
                               iri=iri)

        super().__init__(label, namespace=namespace, resource_store=resource_store, iri=iri)
