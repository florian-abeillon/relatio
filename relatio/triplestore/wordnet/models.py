
from nltk.corpus.reader.wordnet import Synset
from rdflib import Graph, OWL, RDFS, SKOS, Literal
from spacy.tokens.token import Token
from typing import List, Union

import warnings

from ..namespaces import WORDNET
from ..models import ReInstance
from ..resources import Class, Instance, Property, ResourceStore, Triple
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
    """ WordNet domain """

    def __init__(self, label: str, resource_store: ResourceStore):
        label = label.replace("_", " ").capitalize()
        super().__init__(label, WORDNET, DOMAIN_WN, resource_store)



class WnSynset(Instance):
    """ WordNet synonyms set """

    def __init__(self, synset: Synset, class_: type, resource_store: ResourceStore):
        super().__init__(synset.name(), WORDNET, SYNSET_WN, resource_store)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            # TODO: Sometimes not empty?
            self._definition = synset.definition().capitalize()
            self._lexname = synset.lexname()
            self._pos = synset.pos()
    #         self._lemmas = self.set_lemmas(synset, class_, resource_store)


    # @staticmethod
    # def set_lemmas(synset: Synset, class_: type, resource_store: ResourceStore) -> List[Instance]:
    #     """ Add relation of self to a synset """
    #     return [ 
    #         class_(lemma, resource_store, to_set=False) 
    #         for lemma in synset.lemma_names() 
    #     ]


    def to_graph(self, graph: Graph) -> None:
        """ Fill triplestore with synset lemmas and attributes """
        super().to_graph(graph)
        
        if self._definition:
            graph.add(Triple( self.iri, SKOS.definition, Literal(self._definition) ))
        if self._lexname:
            graph.add(Triple( self.iri, LEXNAME.iri, Literal(self._lexname) ))
        if self._pos:
            graph.add(Triple( self.iri, POS.iri, Literal(self._pos) ))

        # for lemma in self._lemmas:
        #     graph.add(Triple( lemma.iri, HAS_SYNSET.iri, self.iri ))



class WnInstance(Instance):
    """ WordNet instance of a class/property """
    
    def __init__(self, token: Token,
                       type_: Union[Class, Property],
                       resource_store: ResourceStore):

        super().__init__(token, WORDNET, type_, resource_store)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._domains = self.set_domains(token._.wordnet.wordnet_domains(), resource_store)
            self._synsets = self.set_synsets(token._.wordnet.synsets(), resource_store)
            self._re_instance = None


    @staticmethod
    def set_domains(domains: list, resource_store: ResourceStore) -> List[WnDomain]:
        """ Add relation of self to a list of domains """
        return [
            WnDomain(domain, resource_store)
            for domain in domains
        ]

    def set_synsets(self, synsets: list, resource_store: ResourceStore) -> List[WnSynset]:
        """ Add relation of self to a list of synsets """
        return [
            WnSynset(synset, self.__class__, resource_store)
            for synset in synsets
        ]

    def set_re_instance(self, re_instance: ReInstance) -> None:
        """ Add Relatio instance of WordNet instance """
        self._re_instance = re_instance


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)

        for domain in self._domains:
            graph.add(Triple( self.iri, HAS_DOMAIN.iri, domain.iri ))
        for synset in self._synsets:
            graph.add(Triple( self.iri, HAS_SYNSET.iri, synset.iri ))

        # Add link to Relatio instance
        if self._re_instance is not None:
            add_two_way(graph, Triple( self.iri, OWL.sameAs, self._re_instance.iri ))
        else:
            warnings.warn(f"WdEntity {self._label} created without any linked ReInstance")



class WnEntity(WnInstance):
    """ WordNet entity """
    
    def __init__(self, token, resource_store: ResourceStore):
        super().__init__(token, ENTITY_WN, resource_store)



class WnRelation(WnInstance):
    """ WordNet relation """
    
    def __init__(self, token, resource_store: ResourceStore):
        super().__init__(token, RELATION_WN, resource_store)
