
from rdflib import OWL, RDF, RDFS, SKOS
from rdflib.namespace import Namespace

RELATIO = Namespace("http://base.relat.io#")
RELATIO_HD = Namespace("http://hd.relat.io#")
RELATIO_LD = Namespace("http://ld.relat.io#")
SPACY = Namespace("http://spacy.io#")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
WORDNET = Namespace("http://wordnet.princeton.edu#")

PREFIXES = {
    OWL: 'owl',
    RDF: 'rdf',
    RDFS: 'rdfs',
    SKOS: 'skos',
    RELATIO: 're',
    RELATIO_HD: 'rehd',
    RELATIO_LD: 'reld',
    SPACY: 'sp',
    WIKIDATA: 'wd',
    WORDNET: 'wn'
}
