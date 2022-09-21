
from rdflib import OWL, RDF, RDFS, SKOS
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.namespace import Namespace


DEFAULT    = Namespace(DATASET_DEFAULT_GRAPH_ID + "#")
SPACY      = Namespace("http://spacy.io#")
WIKIDATA   = Namespace("http://www.wikidata.org/entity/")
WORDNET    = Namespace("http://wordnet.princeton.edu#")


PREFIXES = {
    OWL:        'owl',
    RDF:        'rdf',
    RDFS:       'rdfs',
    SKOS:       'skos',
    DEFAULT:    '',
    SPACY:      'sp',
    WIKIDATA:   'wd',
    WORDNET:    'wn'
}
