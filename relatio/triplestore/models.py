
from rdflib import (
    OWL, RDF,
    Namespace, URIRef
)

from .namespaces import DEFAULT
from .resources import (
    Class, Resource, Property, 
    Quad, ResourceStore
)
from .utils import get_hash

            
# Define default models
ENTITY = Class('Entity')
RELATION   = Property('relation',  domain=ENTITY, range=ENTITY)
CONTAINS   = Property('contains',  domain=ENTITY, range=ENTITY)
HAS_LOWDIM = Property('hasLowDim', domain=ENTITY, range=ENTITY)

MODELS = [
    ENTITY, RELATION, 
    CONTAINS, HAS_LOWDIM
]



class Instance(Resource):
    """ 
    Instance of class/property 
    """

    _namespace = DEFAULT
    _type = None


    def __new__(cls, label:          str,
                     resource_store: ResourceStore):
        
        # Get resource from appropriate ResourceStore (if exists)
        hash_ = hash(cls.generate_iri(label))
        if hash_ in resource_store:
            return resource_store[hash_]

        # Otherwise, create new instance and add it to appropriate ResourceStore
        instance = super().__new__(cls)
        resource_store.add(instance, key=hash_)
        return instance


    def __init__(self, label: str,
                       iri:   str = ""):

        self._to_set = not self.__dict__

        # If instance is not already set, set it
        if self._to_set:
            super().__init__(label, iri=iri)

            self._quads.append(
                Quad( self, RDF.type, self._type )
            )


    @classmethod
    def generate_iri(cls, label:   str, 
                          default: bool = False) -> URIRef:
        """ 
        Build unique resource identifier from label
        """
        label = cls._format_label(label)
        key = f"{cls.__name__}/{get_hash(label)}"
        namespace = DEFAULT if default else cls._namespace
        return namespace[key]


    def add_partOf(self, partOf_instance: Resource) -> None:
        """ 
        Add partOf instance of self
        """
        if str(self).lower() != str(partOf_instance).lower():
            self._quads.append(
                Quad( self, CONTAINS, partOf_instance, namespace=partOf_instance._namespace )
            )


    def set_lowDim(self, lowDim_instance: Resource) -> None:
        """ 
        Set lowDim instance of self
        """
        self._quads.append(
            Quad( self, HAS_LOWDIM, lowDim_instance )
        )
            

    

class Relation(Instance):
    """ 
    Relation between entities
    """

    _format_label = staticmethod(lambda label: str(label).lower())
    _type = RELATION


    def __new__(cls, label:          str,
                     resource_store: ResourceStore,
                     is_neg:         bool          = False,
                     **kwargs                             ):

        if is_neg:
            label = cls.get_neg(label)
        return super().__new__(cls, label, resource_store, **kwargs)


    def __init__(self, label:          str, 
                       resource_store: ResourceStore,
                       is_neg:         bool          = False,
                       **kwargs                             ):

        if is_neg:
            label_pos = label
            label = self.get_neg(label)
        super().__init__(label, **kwargs)

        # If instance is not already set, set it
        if self._to_set:

            if is_neg:
                relation_pos = Relation(label_pos, resource_store, is_neg=False)

                self._quads.extend([
                    Quad( self,         OWL.inverseOf, relation_pos ),
                    Quad( relation_pos, OWL.inverseOf, self,        )
                ])


    @staticmethod
    def get_neg(label: str) -> str:
        """
        Build the negation of label
        """
        label = label.lower()
        if label.startswith('not '):
            return label[4:]
        return 'not ' + label


    def add_partOf(self, partOf_instance: Resource) -> None:
        """ 
        Add partOf relation of base relation 
        """
        if self.label != self.get_neg(str(partOf_instance)):
            super().add_partOf(partOf_instance)
    


class Entity(Instance):
    """ 
    Entity, ie. a concept
    """

    _format_label = staticmethod(lambda label: str(label).capitalize())
    _type = ENTITY


    def __new__(cls, label:          str,
                     resource_store: ResourceStore,
                     **kwargs                     ):

        return super().__new__(cls, label, resource_store, **kwargs)
                                    
    
    def __init__(self, label:          str, 
                       resource_store: ResourceStore,
                       **kwargs                     ):

        super().__init__(label, **kwargs)


    def add_object(self, relation:  Relation, 
                         object_:   Instance,
                         namespace: Namespace) -> None:
        """ 
        Add relation of self to an object 
        """
        self._quads.append(
            Quad( self, relation, object_, namespace=namespace )
        )
