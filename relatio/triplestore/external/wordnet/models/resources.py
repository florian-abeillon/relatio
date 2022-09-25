
from rdflib import RDFS

from ....namespaces import WORDNET
from ....models import ENTITY
from ....resources import Class, PropertyInstance



DOMAIN = Class('Domain', namespace=WORDNET)
SYNSET = Class('Synset', namespace=WORDNET)

HAS_DOMAIN = PropertyInstance('hasDomain', namespace=WORDNET, domain=ENTITY, range=DOMAIN      )
HAS_SYNSET = PropertyInstance('hasSynset', namespace=WORDNET, domain=ENTITY, range=SYNSET      )
LEXNAME    = PropertyInstance('lexname',   namespace=WORDNET, domain=ENTITY, range=RDFS.Literal)
POS        = PropertyInstance('pos',       namespace=WORDNET, domain=ENTITY, range=RDFS.Literal)

RESOURCES = [
    DOMAIN, SYNSET,
    HAS_DOMAIN, HAS_SYNSET,
    LEXNAME, POS
]
