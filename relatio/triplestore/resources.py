
from rdflib import Graph, Literal, OWL, RDF, RDFS, SKOS, URIRef
from typing import List, Optional, Union

from .namespaces import PREFIXES
from .utils import get_hash, to_camel_case, to_pascal_case



class Triple(tuple):
    """ RDF triple """

    def __new__(cls, s, p, o):
        
        if not isinstance(s, URIRef) and s.startswith("http://"):
            s = URIRef(s)
        if not isinstance(p, URIRef) and p.startswith("http://"):
            p = URIRef(p)
        if not isinstance(o, URIRef) and o.startswith("http://"):
            o = URIRef(o)
            
        triple = ( s, p, o )
        return super().__new__(cls, triple)
    

    def __init__(self, s, p, o, **kwargs):
        label = ", ".join([ f"<{el}>" for el in ( s, p, o ) ])
        self._label = f"( {label} )"
        

    def __repr__(self) -> str:
        return self._label
    def __str__(self) -> str:
        return self._label
    def __hash__(self) -> str:
        return hash(self._label)

    def inverse(self) -> tuple:
        """ Returns inverse of self """
        s, p, o = self
        return Triple( o, p, s )
        
    def to_graph(self, graph: Graph) -> None:
        """ Fill triplestore with triple """
        graph.add(self)



class Resource:
    """ Base triplestore resource """

    def __init__(self, label: str, namespace: str, iri: Optional[URIRef] = None):
        self._label = str(label)
        self._alt_label = f"{PREFIXES[namespace]}:{self._label}"
        self._namespace = namespace
        self.iri = iri if iri is not None else self.get_iri()
        
    def __repr__(self) -> str:
        return self._label
    def __str__(self) -> str:
        return self._label
    def __hash__(self) -> str:
        return hash(self.iri)

    def get_iri(self) -> URIRef:
        """ Build unique resource identifier """
        return URIRef(self._namespace + self._label)

    def to_graph(self, graph: Graph) -> None:
        """ Fill triplestore with resource's label """
        graph.add(Triple( self.iri, SKOS.prefLabel, Literal(self._label) ))
        graph.add(Triple( self.iri, SKOS.altLabel, Literal(self._alt_label) ))



class Class(Resource):
    """ Class of resources """
    
    def __init__(self, label: str, namespace: str):

        label = to_pascal_case(label)
        super().__init__(label, namespace)


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(Triple( self.iri, RDFS.subClassOf, OWL.Class ))



class Property(Resource):
    """ Link between resources """
    
    def __init__(self, label: str, 
                       namespace: str, 
                       domain: Optional[Class] = None,
                       range: Optional[Class] = None):

        label = to_camel_case(label)
        super().__init__(label, namespace)
        self._domain = domain
        self._range = range


    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(Triple( self.iri, RDFS.subPropertyOf, RDF.Property ))

        # If a domain/range is mentionned, add appropriate relation
        if self._domain is not None:
            graph.add(Triple( self.iri, RDFS.domain, self._domain.iri ))
        if self._range is not None:
            range = self._range if isinstance(self._range, URIRef) else self._range.iri
            graph.add(( self.iri, RDFS.range, range ))           



class ResourceStore(dict):
    """ Store of resources to be filled into triplestore """

    def __init__(self, resources: List[Resource] = []):
        for resource in resources:
            self[resource] = resource

    def __or__(self, resource_store: dict) -> dict:
        return ResourceStore({ **self, **resource_store })

    def get_or_add(self, resource: Resource) -> Resource:
        """ Get a resource from self, or add it to self if necessary """
        if not resource in self:
            self[resource] = resource
        return self[resource]

    def to_graph(self, graph: Graph) -> None:
        """ Fill triplestore with every resource from self """
        for resource in self.values():
            resource.to_graph(graph)



class Instance(Resource):
    """ Instance of class/property """


    def __init__(self, label: str, 
                       namespace: str, 
                       type_: Union[Class, Property],
                       resource_store: ResourceStore,
                       iri: Optional[URIRef] = None):

        super().__init__(label, namespace, iri=iri)
        
        # Get or add resource from ResourceStore
        self.to_set = not self in resource_store
        self = resource_store.get_or_add(self)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._type = type_
            self._alt_label = f"{PREFIXES[self._namespace]}:{self._type._label}/{self._label}"


    def get_iri(self) -> URIRef:
        """ Build unique resource identifier """
        key = get_hash(self.__class__.__name__, self._label)
        return URIRef(self._namespace + key)

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(Triple( self.iri, RDF.type, self._type.iri ))
