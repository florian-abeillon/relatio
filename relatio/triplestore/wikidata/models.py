
from rdflib import Graph, Literal, OWL, URIRef
from spacy.tokens.span import Span
from typing import List, Union

import warnings

from ..models import ReEntity
from ..namespaces import WIKIDATA
from ..resources import Class, Instance, Property, ResourceStore, Triple
from ..utils import add_two_way


# Define Wikidata class and property
ENTITY_WD   = Class   ('Entity',   WIKIDATA                                   )
RELATION_WD = Property('Relation', WIKIDATA, domain=ENTITY_WD, range=ENTITY_WD)

CLASSES_AND_PROPS_WD = [ ENTITY_WD, RELATION_WD ]



class WdInstance(Instance):
    """ Wikidata instance of a class """
    
    def __init__(self, label: str, 
                       type_: Union[Class, Property],
                       resource_store: ResourceStore,
                       iri: str = ""):

        super().__init__(label, WIKIDATA, type_, resource_store, iri=URIRef(iri))



class WdRelation(WdInstance):
    """ Wikidata relation """
    
    def __init__(self, label: str, resource_store: ResourceStore, iri: str):
        label = label.lower()
        super().__init__(label, RELATION_WD, resource_store, iri)



class WdEntity(WdInstance):
    """ Wikidata entity """
    
    def __init__(self, ent: Union[str, Span], resource_store: ResourceStore, iri: str = ""):

        label = str(ent).capitalize()
        if not iri:
            iri = WIKIDATA + ent.kb_id_

        super().__init__(label, ENTITY_WD, resource_store, iri=iri)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._objects = set()
            self._attributes = set()
            self._re_entity = None


    def add_objects(self, relation: WdRelation, objects: List[WdInstance]) -> None:
        """ Add relation of self to a list of objects """
        self._objects.update({ 
            ( relation, object_ ) for object_ in objects 
        })

    def add_attributes(self, relation: WdRelation, attributes = List[str]) -> None:
        """ Add relation of self to a list of attributes """
        self._attributes.update({
            ( relation, attribute ) for attribute in attributes
        })

    def set_re_entity(self, re_entity: ReEntity) -> None:
        """ Declare Relatio instance of Wikidata instance """
        self._re_entity = re_entity


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        
        for relation, object_ in self._objects:
            graph.add(Triple( self.iri, relation.iri, object_.iri ))
        for relation, attribute in self._attributes:
            graph.add(Triple( self.iri, relation.iri, Literal(attribute) ))

        # Add link to Relatio entity
        if self._re_entity is not None:
            add_two_way(graph, Triple( self.iri, OWL.sameAs, self._re_entity.iri ))
        else:
            warnings.warn(f"WdEntity {self._label} created without any linked ReEntity")
