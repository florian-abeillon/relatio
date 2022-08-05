
from rdflib import Graph, OWL, RDF, URIRef
from typing import Optional

from .namespaces import RELATIO, RELATIO_HD, RELATIO_LD
from .resources import Class, Property, Resource, ResourceStore
from .utils import get_hash

            
# Define base class and properties
ENTITY = Class('Entity', RELATIO)
ENTITY_HD = Class('Entity', RELATIO_HD, superclass=ENTITY)
ENTITY_LD = Class('Entity', RELATIO_LD, superclass=ENTITY)
            
RELATION = Property('relation', RELATIO, domain=ENTITY, range=ENTITY)
RELATION_HD = Property('relation', RELATIO_HD, superproperty=RELATION, domain=ENTITY_HD, range=ENTITY_HD)
RELATION_LD = Property('relation', RELATIO_LD, superproperty=RELATION, domain=ENTITY_LD, range=ENTITY_LD)

IS_HD_INSTANCE_OF = Property('isHDInstanceOf', RELATIO, domain=ENTITY_HD, range=ENTITY_LD)
IS_NEG_OF = Property('isNegOf', RELATIO, domain=ENTITY, range=ENTITY)



class Instance(Resource):
    """ Instance of a class """
    
    def __init__(self, label: str, namespace: str, resources: Optional[ResourceStore] = None):
        super().__init__(label, namespace, resources=resources)
        self._base_instance = None
        self._ld_instance = None

    def get_iri(self) -> URIRef:
        """ Build unique resource identifier """
        key = get_hash(self.__class__.__name__, self._label)
        return URIRef(self._namespace + key)
        
    def set_base_instance(self, base_instance):
        """ Declare base instance of HD/LD instance """
        self._base_instance = base_instance
        
    def set_ld_instance(self, ld_instance):
        """ Declare LD instance of HD instance """
        self._ld_instance = ld_instance

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)

        if self._base_instance is not None:
            graph.add(( self._base_instance.iri, OWL.sameAs, self.iri ))
        if self._ld_instance is not None:
            graph.add(( self.iri, IS_HD_INSTANCE_OF.iri, self._ld_instance.iri ))
    
    
class Relation(Instance):
    """ Relation between entities """
    
    def __init__(self, label: str, 
                       namespace: str, 
                       is_neg: bool = False, 
                       resources: Optional[ResourceStore] = None):
        if is_neg:
            label = "not " + str(label)
        label = label.lower()
        super().__init__(label, namespace, resources=resources)
        self._neg_instance = None
        
    def set_neg_instance(self, neg_instance):
        """ Declare negative relation of self """
        self._neg_instance = neg_instance

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, RELATION.iri ))
        
        # Add two-way link with negated relation 
        if self._neg_instance is not None:
            graph.add(( self.iri, IS_NEG_OF.iri, self._neg_instance.iri ))
            graph.add(( self._neg_instance.iri, IS_NEG_OF.iri, self.iri ))   
    
    
class Entity(Instance):
    """ Entity, ie. a concept """
    
    def __init__(self, label: str, namespace: str, resources: Optional[ResourceStore] = None):
        super().__init__(label, namespace, resources=resources)
        self._objects = set()

    def add_object(self, relation: Relation, object_: Instance):
        """ Add relation of self to an object """
        self._objects.add(( relation, object_ ))

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, ENTITY.iri ))

        for relation, object_ in self._objects:
            graph.add(( self.iri, relation.iri, object_.iri ))         
