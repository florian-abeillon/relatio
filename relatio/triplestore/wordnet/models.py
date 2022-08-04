
from rdflib import Graph, RDF

from relatio.triplestore.namespaces import RELATIO, WORDNET
from relatio.triplestore.models import Instance, Relation
from relatio.triplestore.resources import Class, Property, Resource


# Define WordNet class and properties
ENTITY_WN = Class('WnEntity', WORDNET)
RELATION_WN = Property('WnRelation', WORDNET)
IS_WN_INSTANCE_OF = Property('isWnInstanceOf', WORDNET)

HAS_LEMMA = Property('hasLemma', WORDNET)
DEFINITION = Property('definition', WORDNET)
LEXNAME = Property('lexname', WORDNET)
POS = Property('pos', WORDNET)


class Synset(Resource):
    """ WordNet synonyms set """

    def __init__(self, synset):
        super().__init__(synset.name(), WORDNET)
        self._lemmas = synset.lemma_names()
        self._definition = synset.definition()
        self._lexname = synset.lexname()
        self._pos = synset.pos()
        # TODO: Domain

    def to_graph(self, graph: str) -> None:
        """ Fill triplestore with synset lemmas and attributes """
        super().to_graph(graph)
        
        for lemma in self._lemmas:
            # TODO: Namespace RELATIO
            # TODO: Add it to graph here?
            lemma = Relation(lemma, RELATIO)
            graph.add(( self.iri, HAS_LEMMA.iri, lemma.iri ))
        
        if self._definition:
            graph.add(( self.iri, DEFINITION.iri, self._definition ))
        if self._lexname:
            graph.add(( self.iri, LEXNAME.iri, self._lexname ))
        if self._pos:
            graph.add(( self.iri, POS.iri, self._pos ))


SYNSET = Class('Synset', WORDNET)


class WnInstance(Resource):
    """ WordNet instance of a class """
    
    def __init__(self, label: str):
        super().__init__(label, WORDNET)
        self._relatio_instance = None

    def set_relatio_instance(self, relatio_instance: Instance):
        """ Declare relatio instance of WordNet instance """
        self._relatio_instance = relatio_instance

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        
        if self._relatio_instance is not None:
            graph.add(( self.iri, IS_WN_INSTANCE_OF.iri, self._relatio_instance.iri ))


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

