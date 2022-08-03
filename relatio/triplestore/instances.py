
from rdflib import Graph, OWL, RDF

import hashlib

from relatio.triplestore.resources import Resource, ENTITY, IS_HD_INSTANCE_OF, IS_NEG_OF, RELATION

            
class Instance(Resource):
    """ Instance of a class """
    
    def __init__(self, label: str, namespace: str):
        key = f"{self.__class__.__name__}/{hashlib.sha1(label.encode('utf-8')).hexdigest()}"
        super().__init__(key, namespace, label=label)
        self._base_instance = None
        self._ld_instance = None
        
    def set_base_instance(self, base_instance):
        """ Declare base instance of HD/LD instance """
        self._base_instance = base_instance
        
    def set_ld_instance(self, ld_instance):
        """ Declare LD instance of HD instance """
        self._ld_instance = ld_instance

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)

        if self._base_instance is not None:
            graph.add(( self._base_instance, OWL.sameAs, self.iri ))
        if self._ld_instance is not None:
            graph.add(( self.iri, IS_HD_INSTANCE_OF.iri, self._ld_instance.iri ))
    
    
class Entity(Instance):
    """ Entity, ie. a concept """

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, ENTITY.iri ))
    
    
class Relation(Instance):
    """ Relation between entities """
    
    def __init__(self, label: str, namespace: str, is_neg: bool = False):
        if is_neg:
            label = "not " + label
        label = label.lower()
        super().__init__(label, namespace)
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
