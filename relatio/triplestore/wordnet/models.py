
from rdflib import Graph, Literal, RDF, RDFS
from typing import Optional

from ..namespaces import WORDNET
from ..models import ENTITY, Instance
from ..resources import Class, Property, Resource, ResourceStore


# Define WordNet class and properties
ENTITY_WN = Class('WnEntity', WORDNET)
RELATION_WN = Property('WnRelation', WORDNET, domain=ENTITY_WN, range=ENTITY_WN)
IS_WN_INSTANCE_OF = Property('isWnInstanceOf', WORDNET, domain=ENTITY_WN, range=ENTITY)

DOMAIN = Class('Domain', WORDNET)
HAS_DOMAIN = Property('hasDomain', WORDNET, domain=ENTITY_WN, range=DOMAIN)

SYNSET = Class('Synset', WORDNET)
HAS_SYNSET = Property('hasSynset', WORDNET, domain=ENTITY_WN, range=SYNSET)
HAS_LEMMA = Property('hasLemma', WORDNET, domain=ENTITY_WN, range=ENTITY_WN)
DEFINITION = Property('definition', WORDNET, domain=ENTITY_WN, range=RDFS.Literal)
LEXNAME = Property('lexname', WORDNET, domain=ENTITY_WN, range=RDFS.Literal)
POS = Property('pos', WORDNET, domain=ENTITY_WN, range=RDFS.Literal)



class Domain(Resource):
    """ WordNet domain """

    def __init__(self, label: str, resource_store: Optional[ResourceStore] = None):
        super().__init__(label, WORDNET, resource_store=resource_store)


class Synset(Resource):
    """ WordNet synonyms set """

    def __init__(self, synset, resource_store: Optional[ResourceStore] = None):
        super().__init__(synset.name(), WORDNET, resource_store=resource_store)
        self._definition = synset.definition()
        self._lexname = synset.lexname()
        self._pos = synset.pos()
        self._lemmas = set()

    def add_lemma(self, lemma: Resource):
        """ Add relation of self to a synset """
        self._lemmas.add(lemma)

    def to_graph(self, graph: str) -> None:
        """ Fill triplestore with synset lemmas and attributes """
        super().to_graph(graph)
        
        if self._definition:
            graph.add(( self.iri, DEFINITION.iri, Literal(self._definition) ))
        if self._lexname:
            graph.add(( self.iri, LEXNAME.iri, Literal(self._lexname) ))
        if self._pos:
            graph.add(( self.iri, POS.iri, Literal(self._pos) ))

        for lemma in self._lemmas:
            graph.add(( self.iri, HAS_LEMMA.iri, lemma.iri ))



class WnInstance(Resource):
    """ WordNet instance of a class """
    
    def __init__(self, entity, resource_store: Optional[ResourceStore] = None):
        super().__init__(entity, WORDNET, resource_store=resource_store)
        self._relatio_instance = None
        self._domains = set()
        self._synsets = set()

    def set_relatio_instance(self, relatio_instance: Instance):
        """ Declare relatio instance of WordNet instance """
        self._relatio_instance = relatio_instance

    def add_domain(self, domain: Domain):
        """ Add relation of self to a domain """
        self._domains.add(domain)

    def add_synset(self, synset: Synset):
        """ Add relation of self to a synset """
        self._synsets.add(synset)

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        
        if self._relatio_instance is not None:
            graph.add(( self.iri, IS_WN_INSTANCE_OF.iri, self._relatio_instance.iri ))

        for domain in self._domains:
            graph.add(( self.iri, HAS_DOMAIN.iri, Literal(domain) ))
        for synset in self._synsets:
            graph.add(( self.iri, HAS_SYNSET.iri, synset.iri ))


class WnEntity(WnInstance):
    """ WordNet entity """

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, ENTITY_WN.iri ))


class WnRelation(WnInstance):
    """ WordNet relation """

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, RELATION_WN.iri ))
