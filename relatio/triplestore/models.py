
from spacy.tokens.span import Span
from spacy.tokens.token import Token
from rdflib import Graph, OWL
from typing import Optional, Union

from .namespaces import RELATIO, RELATIO_HD, RELATIO_LD
from .resources import Class, Instance, Property, ResourceStore, Triple
from .utils import add_two_way

            
# Define base class and properties
ENTITY    = Class('Entity',  RELATIO   )
ENTITY_HD = Class('Entity',  RELATIO_HD)
ENTITY_LD = Class('Entity',  RELATIO_LD)
            
RELATION    = Property('relation', RELATIO,    domain=ENTITY,    range=ENTITY   )
RELATION_HD = Property('relation', RELATIO_HD, domain=ENTITY_HD, range=ENTITY_HD)
RELATION_LD = Property('relation', RELATIO_LD, domain=ENTITY_LD, range=ENTITY_LD)

IS_HD_INSTANCE_OF = Property('isHDInstanceOf', RELATIO, domain=ENTITY_HD, range=ENTITY_LD)
CONTAINS          = Property('contains',       RELATIO, domain=ENTITY,    range=ENTITY   )

CLASSES_AND_PROPS = [
    ENTITY, ENTITY_HD, ENTITY_LD,
    RELATION, RELATION_HD, RELATION_LD,
    IS_HD_INSTANCE_OF, CONTAINS
]



class ReInstance(Instance):
    """ Instance of a class/property extracted with Relatio """
    
    def __init__(self, label: str, 
                       type_: Union[Class, Property],
                       resource_store: ResourceStore,
                       hd: bool = False,
                       ld: bool = False,
                       resource_store_base: Optional[ResourceStore] = None):

        assert not ( hd and ld ), 'ReInstance cannot be both HD and LD'
        namespace = RELATIO_HD if hd else RELATIO_LD if ld else RELATIO
        super().__init__(label, namespace, type_, resource_store)

        # If instance not already in ResourceStore, set it
        if self.to_set:

            self._base_instance = None
            self._ld_instance = None
            self._partOf_instances = set()

            if hd or ld:
                assert resource_store_base is not None, 'Please provide resource_store_base for HD/LD instances construction'
                self.set_base_instance(label, resource_store_base)


    def set_base_instance(self, label: str, resource_store: ResourceStore) -> None:
        """ Declare base instance of HD/LD instance """
        is_neg = label.startswith('not ')
        if is_neg:
            label = label[4:]
        self._base_instance =  self.__class__(label, resource_store, hd=False, ld=False, is_neg=is_neg)


    def set_ld_instance(self, ld_instance: Instance) -> None:
        """ Declare LD instance of HD instance """
        self._ld_instance = ld_instance

    def add_partOf_instance(self, partOf_instance: Instance) -> None:
        """ Add partOf instance of base instance """
        if self.iri != partOf_instance:
            self._partOf_instances.add(partOf_instance)


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)

        if self._base_instance is not None:
            add_two_way(graph, Triple( self.iri, OWL.sameAs, self._base_instance.iri ))

        if self._ld_instance is not None:
            graph.add(Triple( self.iri, IS_HD_INSTANCE_OF.iri, self._ld_instance.iri ))

        for partOf_instance in self._partOf_instances:
            graph.add(Triple( self.iri, CONTAINS.iri, partOf_instance.iri ))
            
    

class ReRelation(ReInstance):
    """ Relation between entities extracted with Relatio """
    
    def __init__(self, label: Union[str, Span, Token], 
                       resource_store: ResourceStore,
                       hd: bool = False,
                       ld: bool = False, 
                       is_neg: bool = False,
                       resource_store_base: Optional[ResourceStore] = None):

        label = str(label).lower()
        if is_neg:
            label = "not " + label

        type_ = RELATION_HD if hd else RELATION_LD if ld else RELATION
        super().__init__(label, type_, resource_store, 
                         hd=hd, ld=ld, resource_store_base=resource_store_base)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._pos_instance = None
            if is_neg:
                self.set_pos_instance(label[4:], resource_store, 
                                      hd=hd, ld=ld, resource_store_base=resource_store_base)

        
    def set_pos_instance(self, label: str, 
                               resource_store: ResourceStore,
                               hd: bool = False,
                               ld: bool = False,
                               resource_store_base: Optional[ResourceStore] = None) -> None:
        """ Declare negative relation of self """
        self._pos_instance = ReRelation(label, resource_store, 
                                        hd=hd, ld=ld, resource_store_base=resource_store_base, is_neg=False)


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        
        # Add two-way link to/from negated relation 
        if self._pos_instance is not None:
            add_two_way(graph, Triple( self.iri, OWL.inverseOf, self._pos_instance.iri ))
    

    
class ReEntity(ReInstance):
    """ Entity, ie. a concept, extracted with Relatio """
    
    def __init__(self, label: Union[str, Span, Token], 
                       resource_store: ResourceStore,
                       hd: bool = False,
                       ld: bool = False,
                       resource_store_base: Optional[ResourceStore] = None,
                       **kwargs):

        label = str(label).capitalize()
        type_ = ENTITY_HD if hd else ENTITY_LD if ld else ENTITY
        super().__init__(label, type_, resource_store, 
                         hd=hd, ld=ld, resource_store_base=resource_store_base)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._objects = set()


    def add_object(self, relation: ReRelation, object_: ReInstance) -> None:
        """ Add relation of self to an object """
        self._objects.add(( relation, object_ ))


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)

        for relation, object_ in self._objects:
            graph.add(Triple( self.iri, relation.iri, object_.iri ))
