
from nltk.corpus.reader.wordnet import Synset
from rdflib import (
    OWL, RDFS, SKOS, 
    Dataset, Literal
)
from spacy.tokens.token import Token
from typing import List, Union

import warnings

from ..namespaces import RELATIO, WORDNET
from ..models import ReInstance
from ..resources import Class, Instance, Property, Quad, ResourceStore
from ..utils import add_two_way


# Define WordNet class and properties
ENTITY_WN = Class('Entity', WORDNET)
DOMAIN_WN = Class('Domain', WORDNET)
SYNSET_WN = Class('Synset', WORDNET)

RELATION_WN = Property('Relation',   WORDNET                                      )
HAS_DOMAIN  = Property('hasDomain',  WORDNET, domain=ENTITY_WN, range=DOMAIN_WN   )
HAS_SYNSET  = Property('hasSynset',  WORDNET, domain=ENTITY_WN, range=SYNSET_WN   )
LEXNAME     = Property('lexname',    WORDNET, domain=ENTITY_WN, range=RDFS.Literal)
POS         = Property('pos',        WORDNET, domain=ENTITY_WN, range=RDFS.Literal)

CLASSES_AND_PROPS_WN = [
    ENTITY_WN, DOMAIN_WN, SYNSET_WN,
    RELATION_WN, HAS_DOMAIN, HAS_SYNSET,
    LEXNAME, POS
]



class WnDomain(Instance):
    """ 
    WordNet domain 
    """

    def __init__(self, label:          str, 
                       resource_store: ResourceStore):

        label = label.replace("_", " ").capitalize()
        super().__init__(label, WORDNET, DOMAIN_WN, resource_store)



class WnSynset(Instance):
    """ 
    WordNet synonyms set 
    """

    def __init__(self, synset:         Synset, 
                       resource_store: ResourceStore):

        super().__init__(synset.name(), WORDNET, SYNSET_WN, resource_store)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._definition = synset.definition().capitalize()
            self._lexname = synset.lexname()
            self._pos = synset.pos()
            # TODO: Extract more info from WordNet
    #         self._lemmas = self.set_lemmas(synset, class_, resource_store)


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


    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with synset lemmas and attributes 
        """
        super().to_graph(ds)
        
        if self._definition:
            ds.add(Quad( self.iri, SKOS.definition, Literal(self._definition), self._namespace ))
        else:
            warnings.warn(f"WnSynset {self._label} created without any definition")
        
        if self._lexname:
            ds.add(Quad( self.iri, LEXNAME.iri, Literal(self._lexname), self._namespace ))
        else:
            warnings.warn(f"WnSynset {self._label} created without any lexname")
        
        if self._pos:
            ds.add(Quad( self.iri, POS.iri, Literal(self._pos), self._namespace ))
        else:
            warnings.warn(f"WnSynset {self._label} created without any pos")
        

        # for lemma in self._lemmas:
        #     ds.add(Quad( lemma.iri, HAS_SYNSET.iri, self.iri, self._namespace ))



class WnInstance(Instance):
    """ 
    WordNet instance of a class/property 
    """
    
    def __init__(self, token:          Token,
                       type_:          Union[Class, Property],
                       resource_store: ResourceStore):

        super().__init__(token, WORDNET, type_, resource_store)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._domains = self.set_domains(token._.wordnet.wordnet_domains(), resource_store)
            self._synsets = self.set_synsets(token._.wordnet.synsets(), resource_store)
            self._re_instance = None


    @staticmethod
    def set_domains(domains:        list, 
                    resource_store: ResourceStore) -> List[WnDomain]:
        """ 
        Add relation of self to a list of domains 
        """
        return [
            WnDomain(domain, resource_store)
            for domain in domains
        ]


    def set_synsets(self, synsets:        list, 
                          resource_store: ResourceStore) -> List[WnSynset]:
        """ 
        Add relation of self to a list of synsets 
        """
        return [
            WnSynset(synset, resource_store)
            for synset in synsets
        ]


    def set_re_instance(self, re_instance: ReInstance) -> None:
        """ 
        Add Relatio instance of WordNet instance 
        """
        self._re_instance = re_instance


    def to_graph(self, ds: Dataset) -> None:
        super().to_graph(ds)

        for domain in self._domains:
            ds.add(Quad( self.iri, HAS_DOMAIN.iri, domain.iri, self._namespace ))
        for synset in self._synsets:
            ds.add(Quad( self.iri, HAS_SYNSET.iri, synset.iri, self._namespace ))

        # Add link to Relatio instance
        if self._re_instance is not None:
            quad = Quad( self.iri, OWL.sameAs, self._re_instance.iri, self._namespace )
            add_two_way(ds, quad, other_namespace=RELATIO)
        else:
            warnings.warn(f"WdEntity {self._label} created without any linked ReInstance")



class WnEntity(WnInstance):
    """ 
    WordNet entity 
    """
    
    def __init__(self, token:          Token, 
                       resource_store: ResourceStore):

        super().__init__(token, ENTITY_WN, resource_store)



class WnRelation(WnInstance):
    """ 
    WordNet relation 
    """
    
    def __init__(self, token:          Token, 
                       resource_store: ResourceStore):
                       
        super().__init__(token, RELATION_WN, resource_store)
