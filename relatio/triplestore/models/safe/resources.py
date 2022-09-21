
from ...namespaces import DEFAULT
from ...resources.safe import Class, Property, PropertyInstance

            
ENTITY     = Class('Entity',               namespace=DEFAULT)
RELATION   = Property('Relation',          namespace=DEFAULT, domain=ENTITY, range=ENTITY)
CONTAINS   = PropertyInstance('contains',  namespace=DEFAULT, domain=ENTITY, range=ENTITY)
HAS_LOWDIM = PropertyInstance('hasLowDim', namespace=DEFAULT, domain=ENTITY, range=ENTITY)

RESOURCES = [
    ENTITY, RELATION, 
    CONTAINS, HAS_LOWDIM
]
