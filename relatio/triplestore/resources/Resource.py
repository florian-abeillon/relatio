
from rdflib import RDFS, Dataset, Namespace, URIRef
from typing import List, Optional

from .Quad import Quad
from .ResourceStore import ResourceStore
from .utils import get_hash



class Resource:
    """ 
    Base triplestore resource 
    """

    _format_label = staticmethod(lambda label: str(label))
    _namespace = None


    def __new__(cls, label:          str,
                     namespace:      Optional[Namespace]     = None,
                     resource_store: Optional[ResourceStore] = None,
                     iri:            str                     = ""  ,
                     **kwargs                                      ):
        
        # If a ResourceStore is mentionned
        if resource_store is not None:
            
            # Get resource from appropriate ResourceStore (if exists)
            hash_ = hash(cls.generate_iri(label))
            if hash_ in resource_store:
                return resource_store[hash_]

            # Otherwise, create new instance and add it to appropriate ResourceStore
            instance = super().__new__(cls)
            resource_store.add(instance, key=hash_)
            return instance

        # Otherwise, just create the instance
        return super().__new__(cls)


    def __init__(self, label:     str,
                       namespace: Optional[Namespace]          = None,
                       resource_store: Optional[ResourceStore] = None,
                       iri:       str                          = ""  ):

        # If resource is already set, do not set it
        if self.is_set():
            return

        if namespace is not None:   
            self.__class__._namespace = namespace
        assert self.__class__._namespace is not None, "Please provide a namespace to resource"

        self._label = self.__class__._format_label(label)
        self._iri = URIRef(iri) if iri else self.generate_iri(self._label)

        self._quads = {
            Quad( self, RDFS.label, self._label )
        }

        
    @property
    def label(self) -> str:
        return self._label

    @property
    def iri(self) -> URIRef:
        return self._iri
    @iri.setter
    def iri(self, value) -> URIRef:
        self._iri = URIRef(value)
        
    def __str__(self) -> str:
        return self.label
    def __repr__(self) -> str:
        return str(self.iri)
    def __hash__(self) -> int:
        return get_hash(self.iri)


    @classmethod
    def generate_iri(cls, label: str) -> URIRef:
        """ 
        Build unique resource identifier 
        """
        return cls._namespace[label]


    def is_set(self) -> bool:
        """
        Checks whether self has already been set
        """
        return bool(self.__dict__)


    def add_quad(self, quad: Quad) -> None:
        """
        Add quad to self._quads
        """
        self._quads.add(quad)


    def add_quads(self, quads: List[Quad]) -> None:
        """
        Add multiple quads to self._quads
        """
        for quad in quads:
            self.add_quad(quad)


    def to_graph(self, ds: Dataset) -> None:
        """ 
        Fill triplestore with resource's label 
        """
        for quad in self._quads:
            quad.to_graph(ds)
