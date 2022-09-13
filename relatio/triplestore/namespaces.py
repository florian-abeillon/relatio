
from rdflib import OWL, RDF, RDFS, SKOS
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.namespace import Namespace


DEFAULT    = Namespace(DATASET_DEFAULT_GRAPH_ID + "#")
RELATIO_HD = Namespace("http://hd.relat.io#")
RELATIO_LD = Namespace("http://ld.relat.io#")
SPACY      = Namespace("http://spacy.io#")
WIKIDATA   = Namespace("http://www.wikidata.org/entity/")
WORDNET    = Namespace("http://wordnet.princeton.edu#")


PREFIXES = {
    OWL:        'owl',
    RDF:        'rdf',
    RDFS:       'rdfs',
    SKOS:       'skos',
    DEFAULT:    '',
    RELATIO_HD: 'hd',
    RELATIO_LD: 'ld',
    SPACY:      'sp',
    WIKIDATA:   'wd',
    WORDNET:    'wn'
}
