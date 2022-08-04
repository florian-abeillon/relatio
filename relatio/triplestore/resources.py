
from rdflib import Graph, Literal, RDF, RDFS, URIRef
from typing import Optional

to_pascal_case = lambda text: text.replace("_", " ").title().replace(" ", "")
to_camel_case = lambda text: text[0].lower() + to_pascal_case(text)[1:]



class Triple(tuple):

    def __init__(self, triple: tuple):
        assert len(triple) == 3

        s, p, o = triple
        if not isinstance(s, URIRef):
            s = URIRef(s)
        if not isinstance(p, URIRef):
            p = URIRef(p)
        self = ( s, p, o )

        self._label = f"<{s}> <{p}> "
        self._label += f"<{o}>" if isinstance(o, URIRef) else o
        
    def __repr__(self) -> str:
        return self._label
    def __str__(self) -> str:
        return self._label
    def __hash__(self) -> str:
        return hash(self._label)
        
    def to_graph(self, graph: Graph) -> None:
        """ Fill triplestore with triple """
        graph.add(self)


class Resource:
    """ Base triplestore resource """

    def __init__(self, label: str, namespace: str):
        self._label = label
        self._namespace = namespace
        self.iri = self.get_iri()
        
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
        label = Literal(self._label)
        graph.add(( self.iri, RDFS.label, label ))


class Class(Resource):
    """ Class of resources """
    
    def __init__(self, label: str, namespace: str, superclass: Optional[Resource] = None):
        label = to_pascal_case(label)
        super().__init__(label, namespace)
        self._superclass = superclass

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDFS.subClassOf, RDFS.Class ))
        
        # If a superclass is mentionned, add subClassOf relation
        if self._superclass is not None:
            graph.add(( self.iri, RDFS.subClassOf, self._superclass.iri ))


class Property(Resource):
    """ Link between resources """
    
    def __init__(self, label: str, 
                       namespace: str, 
                       superproperty: Optional[Resource] = None,
                       domain: Optional[Class] = None,
                       range: Optional[Class] = None):
        label = to_camel_case(label)
        super().__init__(label, namespace)
        self._superproperty = superproperty
        self._domain = domain
        self._range = range

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, RDF.Property ))
        
        if self._superproperty is not None:
            graph.add(( self.iri, RDFS.subPropertyOf, self._superproperty.iri )) 
        if self._domain is not None:
            graph.add(( self.iri, RDFS.domain, self._domain.iri )) 
        if self._range is not None:
            graph.add(( self.iri, RDFS.range, self._range.iri ))           


class ResourceStore(dict):
    """ Store of resources to be filled into triplestore """

    def get_or_add(self, resource: Resource) -> Resource:
        """ Get a resource from self, or add it to self if necessary """
        if not resource in self:
            self[resource] = resource
        return self[resource]

    def to_graph(self, graph: Graph) -> None:
        """ Fill triplestore with every resource from self """
        for resource in self.values():
            resource.to_graph(graph)
