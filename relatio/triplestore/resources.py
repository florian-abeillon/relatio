
from rdflib import Graph, Literal, RDF, RDFS, URIRef
from typing import Optional

from relatio.triplestore.namespaces import RELATIO, RELATIO_HD, RELATIO_LD

to_pascal_case = lambda text: text.replace("_", " ").title().replace(" ", "")
to_camel_case = lambda text: text[0].lower() + to_pascal_case(text)[1:]


class Resource:
    """ Base triplestore resource """

    def __init__(self, key: str, namespace: str, label: str = ""):
        self._key = key
        self._label = label if label else key
        self._namespace = namespace
        self.iri = self.get_uri()

    def get_uri(self) -> URIRef:
        """ Build unique resource identifier """
        return URIRef(self._namespace + self._key)

    def to_graph(self, graph: str) -> None:
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
    
    def __init__(self, label: str, namespace: str, superproperty: Optional[Resource] = None):
        label = to_camel_case(label)
        super().__init__(label, namespace)
        self._superproperty = superproperty

    def to_graph(self, graph: Graph) -> None:
        super().to_graph(graph)
        graph.add(( self.iri, RDF.type, RDF.Property ))
        
        # If a superproperty is mentionned, add subClassOf relation
        if self._superproperty is not None:
            graph.add(( self.iri, RDFS.subPropertyOf, self._superproperty.iri ))           


class ResourceStore:
    """ Store of resources to be filled into triplestore """

    def __init__(self):
        self._resources = {}

    def get_or_add(self, resource):
        key = resource.iri
        if not key in self._resources:
            self._resources[key] = resource
        return self._resources[key]

    def to_graph(self, graph: Graph) -> None:
        # Fill triplestore with every resource from self._resources
        for resource in self._resources.values():
            resource.to_graph(graph)

        

# Define 'Entity' class, in base/HD/LD namespaces
ENTITY = Class('Entity', RELATIO)
ENTITY_HD = Class('Entity', RELATIO_HD, superclass=ENTITY)
ENTITY_LD = Class('Entity', RELATIO_LD, superclass=ENTITY)
            
# Define 'relation' property, in base/HD/LD namespaces
RELATION = Property('relation', RELATIO)
RELATION_HD = Property('relation', RELATIO_HD, superproperty=RELATION)
RELATION_LD = Property('relation', RELATIO_LD, superproperty=RELATION)

# Define 'isHDInstanceOf' and 'isNegOf properties
IS_HD_INSTANCE_OF = Property('isHDInstanceOf', RELATIO)
IS_NEG_OF = Property('isNegOf', RELATIO)


BASE_RESOURCES = [
    ENTITY, ENTITY_HD, ENTITY_LD,
    RELATION, RELATION_HD, RELATION_LD,
    IS_HD_INSTANCE_OF, IS_NEG_OF
]
