
from rdflib import Graph, Literal, RDF, URIRef
from typing import Optional

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
    
    def __init__(self, label: str, iri: str = "", resources: Optional[ResourceStore] = None):
        super().__init__(label, WIKIDATA, resources=resources)
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
    
    def __init__(self, ent, iri: str = "", resources: Optional[ResourceStore] = None):
        
        # If ent is a string (output of WikiData query)
        if iri:
            label = ent
        # If ent is an entity extracted with opentapioca
        else:
            label = ent.text
            iri = WIKIDATA + ent.kb_id_
            self._type = ent.label_
            self._desc = ent._.description

        super().__init__(label, iri=iri, resources=resources)
        self._relatio_instance = None
        self._objects = set()
        self._attributes = set()


    def set_relatio_instance(self, relatio_instance: Instance):
        """ Declare relatio instance of WikiData instance """
        self._relatio_instance = relatio_instance


    def add_object(self, relation: WdRelation, object_: WdInstance):
        """ Add relation of self to an object """
        self._objects.add(( relation, object_ ))

    def add_attribute(self, relation: WdRelation, attribute):
        """ Add relation of self to an attribute """
        self._attributes.add(( relation, attribute ))


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, ENTITY_WD.iri ))

        if self._relatio_instance is not None:
            graph.add(( self.iri, IS_WD_INSTANCE_OF.iri, self._relatio_instance.iri ))
        
        for relation, object_ in self._objects:
            graph.add(( self.iri, relation.iri, object_.iri ))
        for relation, attribute in self._attributes:
            graph.add(( self.iri, relation.iri, Literal(attribute) ))
