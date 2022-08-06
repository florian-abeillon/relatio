
from rdflib import Graph, Literal, RDF, URIRef
from typing import List, Optional

from ..models import ENTITY, Instance
from ..namespaces import WIKIDATA
from ..resources import Class, Property, Resource, ResourceStore
from ..utils import get_hash


# Define WikiData class and properties
ENTITY_WD = Class('WdEntity', WIKIDATA)
RELATION_WD = Property('WdRelation', WIKIDATA, domain=ENTITY_WD, range=ENTITY_WD)
IS_WD_INSTANCE_OF = Property('isWDInstanceOf', WIKIDATA, domain=ENTITY_WD, range=ENTITY)



class WdInstance(Resource):
    """ Wikidata instance of a class """
    
    def __init__(self, label: str, 
                       iri: str = "", 
                       resource_store: Optional[ResourceStore] = None):

        super().__init__(label, WIKIDATA, resource_store=resource_store)
        if iri:
            self.iri = URIRef(iri)


    def get_iri(self) -> URIRef:
        """ Build unique resource identifier """
        key = get_hash(self.__class__.__name__, self._label)
        return URIRef(self._namespace + key)



class WdRelation(WdInstance):
    """ WikiData relation """

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, RELATION_WD.iri ))



class WdEntity(WdInstance):
    """ WikiData entity """
    
    def __init__(self, ent, 
                       iri: str = "", 
                       resource_store: Optional[ResourceStore] = None):
        
        # If ent is an entity extracted with opentapioca
        # (only WikiData results are passed an iri)
        if not iri:
            iri = WIKIDATA + ent.kb_id_
            self._type = ent.label_
            self._desc = ent._.description

        super().__init__(ent, iri=iri, resource_store=resource_store)
        self._relatio_instance = None
        self._objects = set()
        self._attributes = set()


    def set_relatio_instance(self, relatio_instance: Instance) -> None:
        """ Declare relatio instance of WikiData instance """
        self._relatio_instance = relatio_instance

    def set_objects(self, relation: WdRelation, objects: List[WdInstance]) -> None:
        """ Add relation of self to a list of objects """
        self._objects = set([ ( relation, object_ ) for object_ in objects ])

    def set_attributes(self, relation: WdRelation, attributes = list) -> None:
        """ Add relation of self to a list of attributes """
        self._attributes = set([ ( relation, attribute ) for attribute in attributes ])


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, ENTITY_WD.iri ))

        if self._relatio_instance is not None:
            graph.add(( self.iri, IS_WD_INSTANCE_OF.iri, self._relatio_instance.iri ))
        
        for relation, object_ in self._objects:
            graph.add(( self.iri, relation.iri, object_.iri ))
        for relation, attribute in self._attributes:
            graph.add(( self.iri, relation.iri, Literal(attribute) ))
