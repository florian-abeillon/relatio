
from rdflib import (
    RDFS,
    Dataset, Literal, Namespace, URIRef
)
from typing import List, Optional, Union

from .namespaces import DEFAULT
from .utils import (
    to_camel_case, to_pascal_case, get_hash
)



class Quad(tuple):
    """ 
    RDF quad 
    """

    def __new__(cls, subject,
                     predicate,
                     object_, 
                     namespace: Optional[Namespace] = None):
        
        def format(el, is_object: bool = False) -> URIRef:
            if is_object and isinstance(el, str):
                return Literal(el)
            if not isinstance(el, URIRef):
                return el.iri
            return el

        quad = ( 
            format(subject),
            format(predicate),
            format(object_, is_object=True),
            namespace if namespace is not None else subject._namespace
        )
        return super().__new__(cls, quad)
        

    def __init__(self, subject,
                       predicate,
                       object_, 
                       namespace: Optional[Namespace] = None):

        if namespace is None:
            namespace = subject._namespace
        self._label = f"( {subject}, {predicate}, {object_}, {namespace} )"
        

    def __repr__(self) -> str:
        return self._label
    def __str__(self) -> str:
        return self._label
    def __hash__(self) -> str:
        return get_hash(self._label)
        

    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with quad 
        """
        ds.add(self)



class Resource:
    """ 
    Base triplestore resource 
    """

    _format_label = staticmethod(lambda label: str(label))
    _namespace = None


    def __init__(self, label: str,
                       iri:   str = ""):
        self._label = label
        self._iri = URIRef(iri) if iri else self.generate_iri(label)
        self._quads = [
            Quad( self, RDFS.label, self.label )
        ]


    @property
    def label(self) -> str:
        return self.__class__._format_label(self._label)

    @property
    def iri(self) -> URIRef:
        return self._iri
    @iri.setter
    def iri(self, value) -> URIRef:
        self._iri = URIRef(value)
        

    def __repr__(self) -> str:
        return self.label
    def __str__(self) -> str:
        return self.label
    def __hash__(self) -> str:
        return get_hash(self.iri)


    @classmethod
    def generate_iri(cls, label: str) -> URIRef:
        """ 
        Build unique resource identifier 
        """
        return cls._namespace[label]


    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with resource's label 
        """
        for quad in self._quads:
            quad.to_graph(ds)



class Class(Resource):
    """ 
    Class of resources 
    """

    _format_label = staticmethod(lambda label: to_pascal_case(label))


    def __init__(self, label:     str, 
                       namespace: Namespace = DEFAULT):
                       
        self.__class__._namespace = namespace
        super().__init__(label)



class Property(Resource):
    """ 
    Link between resources 
    """

    _format_label = staticmethod(lambda label: to_camel_case(label))


    def __init__(self, label:     str,    
                       namespace: Namespace                      = DEFAULT, 
                       domain:    Optional[Class]                = None,
                       range:     Optional[Union[Class, URIRef]] = None   ):

        self.__class__._namespace = namespace
        super().__init__(label)

         # If a domain/range is mentionned, add appropriate relation
        if domain is not None:
            self._quads.append(
                Quad( self, RDFS.domain, domain )
            )
        if range is not None:
            self._quads.append(
                Quad( self, RDFS.range, range )
            )



class ResourceStore(dict):
    """ 
    Store of resources to be filled into triplestore 
    """

    def __init__(self, resources: List[Resource] = []):
        for resource in resources:
            self.add(resource)


    def add(self, resource: Resource,
                  key:      Optional[int] = None) -> None:
        """ 
        Add a resource to self 
        """
        if key is None:
            key = resource
        self[key] = resource


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
