
from nltk.corpus.reader.wordnet import Synset as NltkSynset
from rdflib import RDFS, SKOS
from spacy.tokens.token import Token

from ..models_ext import ExtEntity, ExtRelation
from ...namespaces import WORDNET
from ...models import ENTITY, RELATION, Instance
from ...resources import (
    Class, Property, Quad, ResourceStore
)


# Define WordNet class and properties
DOMAIN    = Class('Domain', WORDNET                    )
SYNSET    = Class('Synset', WORDNET                    )
ENTITY_WN = Class('Entity', WORDNET, super_class=ENTITY)

RELATION_WN = Property('relation',  WORDNET,                                   super_property=RELATION)
HAS_DOMAIN  = Property('hasDomain', WORDNET, domain=ENTITY, range=DOMAIN                              )
HAS_SYNSET  = Property('hasSynset', WORDNET, domain=ENTITY, range=SYNSET                              )
LEXNAME     = Property('lexname',   WORDNET, domain=ENTITY, range=RDFS.Literal                        )
POS         = Property('pos',       WORDNET, domain=ENTITY, range=RDFS.Literal                        )

MODELS = [
    DOMAIN, SYNSET,
    ENTITY_WN, RELATION_WN,
    HAS_DOMAIN, HAS_SYNSET,
    LEXNAME, POS
]



class Domain(Instance):
    """ 
    WordNet domain 
    """

    _format_label = staticmethod(lambda label: str(label).replace("_", " ").capitalize())
    _namespace = WORDNET
    _type = DOMAIN


    def __init__(self, label:          str, 
                       resource_store: ResourceStore):

        super().__init__(label)



class Synset(Instance):
    """ 
    WordNet synonyms set 
    """

    _format_label = staticmethod(lambda label: str(label).lower())
    _namespace = WORDNET
    _type = SYNSET


    def __new__(cls, synset:         NltkSynset, 
                     resource_store: ResourceStore):

        return super().__new__(cls, synset.name(), resource_store)


    def __init__(self, synset:         NltkSynset, 
                       resource_store: ResourceStore):

        super().__init__(synset.name())

        # If instance is not already set, set it
        if self._to_set:

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



class WnInstance:
    """ 
    WordNet instance of a class/property 
    """

    _namespace = WORDNET


    def __new__(cls, token:             Token,
                     resource_store:    ResourceStore,
                     resource_store_wn: ResourceStore):

        return super().__new__(cls, token,
                                    resource_store, 
                                    resource_store_ext=resource_store_wn)
    

    def __init__(self, token:             Token,
                       resource_store:    ResourceStore,
                       resource_store_wn: ResourceStore):

        super().__init__(token, resource_store)

        # If WordNet instance is not already set, set it
        if not hasattr(self, '_wn_set'):

            self.set_domains(token._.wordnet.wordnet_domains(), resource_store_wn)
            self.set_synsets(token._.wordnet.synsets(),         resource_store_wn)

            self._wn_set = True


    def set_domains(self, domains:        list, 
                          resource_store: ResourceStore) -> None:
        """ 
        Add relations from self to domains 
        """
        for domain in domains:
            domain = Domain(domain, resource_store)
            self._quads.append(
                Quad( self, HAS_DOMAIN, domain )
            )


    def set_synsets(self, synsets:        list, 
                          resource_store: ResourceStore) -> None:
        """ 
        Add relations from self to synsets 
        """
        for synset in synsets:
            synset = Synset(synset, resource_store)
            self._quads.append(
                Quad( self, HAS_SYNSET, synset )
            )



class Entity(WnInstance, ExtEntity):   
    """ 
    Entity from WordNet
    """

    _type = ENTITY_WN



class Relation(WnInstance, ExtRelation): 
    """ 
    Relation from WordNet
    """

    _type = RELATION_WN
