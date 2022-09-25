
from nltk.corpus.reader.wordnet import Synset as NltkSynset
from pydantic import Field
from rdflib import SKOS

from .resources import LEXNAME, POS, SYNSET
from ....namespaces import WORDNET
from ....resources import (
    ClassInstance, Model, 
    Quad, ResourceStore
)




class SynsetModel(Model):
    """
    WordNet synset model definition
    """

    synset:         NltkSynset    = Field(..., description="NLTK synset")
    resource_store: ResourceStore = Field(..., description="ResourceStore to put synset into")



class Synset(ClassInstance):
    """ 
    WordNet synonyms set 
    """

    _format_label = staticmethod(lambda label: label.lower())
    _namespace = WORDNET
    _type = SYNSET


    def __new__(cls, synset:         NltkSynset, 
                     resource_store: ResourceStore):
        # Check arguments types
        _ = SynsetModel(synset=synset, resource_store=resource_store)
        return super().__new__(cls, synset.name(), resource_store=resource_store)


    def __init__(self, synset:         NltkSynset, 
                       resource_store: ResourceStore):

        super().__init__(synset.name(), resource_store=resource_store)

        # If instance is not already set, set it
        if self.is_set():
            return

        definition = synset.definition().capitalize()
        if definition:
            self._quads.append(
                Quad( self, SKOS.definition, definition )
            )

        lexname = synset.lexname()
        if lexname:
            self._quads.append(
                Quad( self, LEXNAME, lexname )
            )

        pos = synset.pos()
        if pos:
            self._quads.append(
                Quad( self, POS, pos )
            )

        # TODO: Extract more info from WordNet
        # self._lemmas = self.set_lemmas(synset, class_, resource_store)


    # @staticmethod
    # def set_lemmas(synset:         Synset, 
    #                class_:         type, 
    #                resource_store: ResourceStore) -> List[Instance]:
    #     """ 
    #     Add relation of self to a synset 
    #     """
    #     return [ 
    #         class_(lemma, resource_store, to_set=False) 
    #         for lemma in synset.lemma_names() 
    #     ]
