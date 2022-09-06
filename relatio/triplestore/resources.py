
from rdflib import (
    OWL, RDF, RDFS,
    Dataset, Literal, URIRef
)
from typing import List, Optional, Union

from .namespaces import PREFIXES
from .utils import get_hash, to_camel_case, to_pascal_case



class Quad(tuple):
    """ RDF quad """

    def __new__(cls, s: Union[str, URIRef], 
                     p: Union[str, URIRef], 
                     o: Union[str, URIRef], 
                     n: Optional[Union[str, URIRef]] = None):

        def format_component(el: Union[str, URIRef]) -> Union[str, URIRef]:
            if not isinstance(el, URIRef) and el.startswith("http://"):
                el = URIRef(el)
            return el
        
        s = format_component(s)
        p = format_component(p)
        o = format_component(o)
        if n is not None:
            n = format_component(n)
            
        quad = ( s, p, o, n )
        return super().__new__(cls, quad)
    

    def __init__(self, s: Union[str, URIRef], 
                       p: Union[str, URIRef], 
                       o: Union[str, URIRef], 
                       n: Optional[Union[str, URIRef]] = None):
        label = ", ".join([ f"<{el}>" for el in ( s, p, o, n ) ])
        self._label = f"( {label} )"
        

    def __repr__(self) -> str:
        return self._label
    def __str__(self) -> str:
        return self._label
    def __hash__(self) -> str:
        return hash(self._label)


    def inverse(self, namespace: Optional[URIRef] = None) -> tuple:
        """ 
        Returns inverse of self, in other namespace 
        """
        s, p, o, _ = self
        return Quad( o, p, s, namespace )
        

    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with quad 
        """
        ds.add(self)



class Resource:
    """ Base triplestore resource """

    def __init__(self, label:     str, 
                       namespace: str, 
                       iri:       Optional[URIRef] = None):
                       
        self._label = str(label)
        self._namespace = namespace
        self.iri = iri if iri is not None else self.get_iri()
        

    def __repr__(self) -> str:
        return self._label
    def __str__(self) -> str:
        return self._label
    def __hash__(self) -> str:
        return hash(self.iri)


    def get_iri(self) -> URIRef:
        """ 
        Build unique resource identifier 
        """
        return URIRef(self._namespace + self._label)


    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with resource's label 
        """
        ds.add(Quad( self.iri, RDFS.label, Literal(self._label), self._namespace ))



class Class(Resource):
    """ 
    Class of resources 
    """
    
    def __init__(self, label:     str, 
                       namespace: str):
                       
        label = to_pascal_case(label)
        super().__init__(label, namespace)


    def to_graph(self, ds: Dataset) -> None:
        super().to_graph(ds)
        ds.add(Quad( self.iri, RDFS.subClassOf, OWL.Class, self._namespace ))



class Property(Resource):
    """ 
    Link between resources 
    """
    
    def __init__(self, label:     str, 
                       namespace: str, 
                       domain:    Optional[Class] = None,
                       range:     Optional[Class] = None):

        label = to_camel_case(label)
        super().__init__(label, namespace)
        self._domain = domain
        self._range = range


    def to_graph(self, ds: Dataset) -> None:
        super().to_graph(ds)
        ds.add(Quad( self.iri, RDFS.subPropertyOf, RDF.Property, self._namespace ))

        # If a domain/range is mentionned, add appropriate relation
        if self._domain is not None:
            ds.add(Quad( self.iri, RDFS.domain, self._domain.iri, self._namespace ))
        if self._range is not None:
            range = self._range if isinstance(self._range, URIRef) else self._range.iri
            ds.add(Quad( self.iri, RDFS.range, range, self._namespace ))           



class ResourceStore(dict):
    """ 
    Store of resources to be filled into triplestore 
    """

    def __init__(self, resources: List[Resource] = []):
        for resource in resources:
            self.add(resource)


    def __or__(self, resource_store: dict) -> dict:
        return ResourceStore({ **self, **resource_store })


    def add(self, resource: Resource) -> None:
        """ 
        Add a resource to self 
        """
        self[resource] = resource


    def get_or_add(self, resource: Resource) -> Resource:
        """ 
        Get a resource from self, or add it to self if necessary 
        """
        if not resource in self:
            self.add(resource)
        return self[resource]


    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with every resource from self 
        """
        for resource in self.values():
            resource.to_graph(ds)



class Instance(Resource):
    """ 
    Instance of class/property 
    """


    def __init__(self, label:          str, 
                       namespace:      str, 
                       type_:          Union[Class, Property],
                       resource_store: ResourceStore,
                       iri:            Optional[URIRef] = None):

        super().__init__(label, namespace, iri=iri)
        
        # Get or add resource from ResourceStore
        self.to_set = not self in resource_store
        self = resource_store.get_or_add(self)

        # If instance not already in ResourceStore, set it
        if self.to_set:
            self._type = type_
            self._alt_label = f"{PREFIXES[self._namespace]}:{self._type._label}/{self._label}"


    def get_iri(self) -> URIRef:
        """ 
        Build unique resource identifier 
        """
        key = get_hash(self.__class__.__name__, self._label)
        return URIRef(self._namespace + key)


    def to_graph(self, ds: Dataset) -> None:
        super().to_graph(ds)
        ds.add(Quad( self.iri, RDF.type, self._type.iri, self._namespace ))
