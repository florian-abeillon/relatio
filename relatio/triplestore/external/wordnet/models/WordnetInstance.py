
from pydantic import Field
from spacy.tokens.token import Token as SpacyToken

from .Domain import Domain
from .resources import HAS_DOMAIN, HAS_SYNSET
from .Synset import Synset
from ....namespaces import WORDNET
from ....resources import (
    Model, Quad, ResourceStore
)



class Token:

    def __init__(self, token: SpacyToken):
        self._label = str(token)
        self.domains = token._.wordnet.wordnet_domains()
        self.synsets = token._.wordnet.synsets()

    def __str__(self) -> str:
        return self._label



class WordnetInstanceModel(Model):
    """
    WordNet instance model definition
    """

    token:             Token         = Field(..., description="Token object returned by module")
    resource_store:    ResourceStore = Field(..., description="ResourceStore to search instance in")
    resource_store_wn: ResourceStore = Field(..., description="ResourceStore to put instance into if it is not in resource_store")




class WordnetInstance:
    """ 
    WordNet instance of a class/property 
    """

    _namespace = WORDNET


    def __new__(cls, token:             Token,
                     resource_store:    ResourceStore,
                     resource_store_wn: ResourceStore):
        # Check arguments types
        _ = WordnetInstanceModel(token=token, resource_store=resource_store, resource_store_wn=resource_store_wn)
        return super().__new__(cls, str(token), resource_store, resource_store_ext=resource_store_wn)
    

    def __init__(self, token:             Token,
                       resource_store:    ResourceStore,
                       resource_store_wn: ResourceStore):

        super().__init__(str(token), resource_store, resource_store_ext=resource_store_wn)

        # If WordNet instance is not already set, set it
        if not hasattr(self, '_is_wn_set'):

            self.set_domains(token.domains, resource_store_wn)
            self.set_synsets(token.synsets, resource_store_wn)

            self._is_wn_set = True


    def set_domains(self, domains:        list, 
                          resource_store: ResourceStore) -> None:
        """ 
        Add relations from self to domains 
        """
        for domain in domains:
            domain = Domain(domain, resource_store)
            self.add_quad(
                Quad( self, HAS_DOMAIN, domain, namespace=WORDNET )
            )


    def set_synsets(self, synsets:        list, 
                          resource_store: ResourceStore) -> None:
        """ 
        Add relations from self to synsets 
        """
        for synset in synsets:
            synset = Synset(synset, resource_store)
            self.add_quad(
                Quad( self, HAS_SYNSET, synset, namespace=WORDNET )
            )
