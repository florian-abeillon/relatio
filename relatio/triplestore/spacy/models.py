
from rdflib import Graph, Literal, OWL, RDF, SKOS
from spacy.tokens.span import Span

import spacy
import warnings

from ..models import ReEntity
from ..namespaces import SPACY
from ..resources import Class, Instance, Property, ResourceStore, Triple
from ..utils import add_two_way


# Define SpaCy class and properties
ENTITY_SP = Class('Entity', SPACY)
CLASS_SP  = Class('Class',  SPACY)
TYPE_SP = Property('type', SPACY, domain=ENTITY_SP, range=CLASS_SP)
        
CLASSES_AND_PROPS_SP = [
    ENTITY_SP, CLASS_SP, TYPE_SP
]



class SpClass(Instance):
    """ SpaCy named entity class """

    def __init__(self, label: str, resource_store: ResourceStore):
        label = label.upper()
        super().__init__(label, SPACY, CLASS_SP, resource_store)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._description = spacy.explain(label)


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)

        if self._description:
            graph.add(Triple( self.iri, SKOS.definition, Literal(self._description) ))



class SpEntity(Instance):
    """ SpaCy named entity """
    
    def __init__(self, ent: Span, resource_store: ResourceStore):

        label = str(ent).capitalize()
        super().__init__(label, SPACY, ENTITY_SP, resource_store)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._ent_class = SpClass(ent.label_, resource_store) if ent.label_ else None
            self._re_entity = None


    def set_re_entity(self, re_entity: ReEntity) -> None:
        """ Declare Relatio instance of SpaCy instance """
        self._re_entity = re_entity


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)

        # Add link to SpaCy named entity domain
        if self._ent_class is not None:
            graph.add(Triple( self.iri, RDF.type, self._ent_class.iri ))
        else:
            warnings.warn(f"SpEntity {self._label} has an empty SpDomain")

        # Add link to Relatio entity
        if self._re_entity is not None:
            add_two_way(graph, Triple( self.iri, OWL.sameAs, self._re_entity.iri ))
        else:
            warnings.warn(f"SpEntity {self._label} created without any linked ReEntity")
