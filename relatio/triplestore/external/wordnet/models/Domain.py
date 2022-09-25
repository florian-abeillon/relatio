
from pydantic import Field

from .resources import DOMAIN
from ....namespaces import WORDNET
from ....resources import (
    ClassInstance, Model, ResourceStore
)


class DomainModel(Model):
    """
    WordNet domain model definition
    """

    label:          str           = Field(..., description="Label of domain")
    resource_store: ResourceStore = Field(..., description="ResourceStore to put domain into")



class Domain(ClassInstance):
    """ 
    WordNet domain 
    """

    _format_label = staticmethod(lambda label: label.replace("_", " ").capitalize())
    _namespace = WORDNET
    _type = DOMAIN


    def __new__(cls, label:          str, 
                     resource_store: ResourceStore):
        # Check arguments types
        _ = DomainModel(label=label, resource_store=resource_store)
        return super().__new__(cls, label, resource_store=resource_store)


    def __init__(self, label:          str, 
                       resource_store: ResourceStore):

        super().__init__(label, resource_store=resource_store)
