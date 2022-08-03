
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import List

import re

from relatio.triplestore.namespaces import WIKIDATA


URL = 'https://query.wikidata.org/sparql'
with open('query.sparql') as f:
    QUERY = f.read()



class WdResource:
    """ Wikidata resource """
    
    def __init__(self, label: str, iri: str = ""):
        self.label = label
        
        if iri:
            self.is_attr = False
            self.iri = self.format_iri(iri)
            self.has_prefix = iri != self.iri
        else:
            self.is_attr = True
            self.iri = ""
            self.has_prefix = False
            
    @staticmethod
    def format_iri(iri: str) -> str:
        """ Format IRI with appropriate prefix (if known) """
        return iri.replace(WIKIDATA, "wd:")
        
    def __repr__(self) -> str:
        return self.label
    def __str__(self) -> str:
        return self.label
    
    def __hash__(self) -> str:
        """ Hash IRI or label, to get unique hash """
        return hash(self.iri if self.iri else self.label)


class NamedEntity:
    """ Named entity, enriched with WikiData information """
    
    def __init__(self, ent):
        self.label = ent.text
        self.type = ent.label_
        self.desc = ent._.description
        
        self.wid = ent.kb_id_
        self.iri = "wd:" + self.wid
        self.wd_ent = WdResource(self.label, iri=self.iri)
        
        self.query = QUERY.format(iri=self.iri)
        self.attributes, self.relations = defaultdict(list), defaultdict(list)
        self.relations_intra, self.relations_extra = defaultdict(list), defaultdict(list)
        
    def __repr__(self) -> str:
        return self.label
    def __str__(self) -> str:
        return self.label
                
                
    def clean_attributes(self) -> None:
        """ Remove uninformative WikiData attributes """

        to_del = []
        for p, o_list in self.attributes.items():
            
            if (
                # If attribute is an ID, or
                re.findall("ID( *\(.*\))? *$", p.label) or
                # If attribute label is in uppercase (likely not informative), or
                p.label.isupper() or
                # TODO: To improve
                # If attribute is a mixture of letters and numbers (likely not informative)
                (
                    o_list[0].label[0].isalpha() and
                    any(( not all(( char.isalpha() for char in o.label )) for o in o_list ))
                ) or
                (
                    o_list[0].label[0].isnumeric() and
                    any(( not all(( char.isnumeric() for char in o.label )) for o in o_list ))
                )
            ):
                to_del.append(p)
                
        for p in to_del:
            del self.attributes[p]
        
    
    def query_ent(self) -> None:
        """ Query WikiData knowledge base to enrich named entity """
        
        # Query WikiData knowledge base
        sparql = SPARQLWrapper(URL)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(self.query)
        res = sparql.queryAndConvert()
        
        # For every set of results
        for r in res['results']['bindings']:
            
            # Build predicate as a WdResource
            p = WdResource(r['p_label']['value'], iri=r['p_iri']['value'])

            o_list = r['o_list']['value'].split('|')
            for o in o_list:
                # For every object returned, build it as a WdResource
                o = WdResource(*o.split("\\"))
                if o.is_attr:
                    self.attributes[p].append(o)
                else:
                    self.relations[p].append(o)
                
        self.clean_attributes()
                
                
    def link_ents(self, ents: list) -> None:
        """ Link self to other named entities """

        # For every predicate
        for p, o_list in self.relations.items():
            # For every object
            for o in o_list:

                # If o is in named entities list, add to self.relations_intra
                if o.iri in ents:
                    self.relations_intra[p].append(o)
                # Otherwise, add to self.relations_extra
                else:
                    self.relations_extra[p].append(o)
                    
                
    def format_triples(self, p_o_dict: dict, prettify: bool = False, is_attr: bool = False) -> List[tuple]:
        """ Format list of predicate/objects into triples """

        def format_triple(s, p, o) -> tuple:
            if prettify:
                return s, p, o
            return s.iri, p.iri, ( o.label if is_attr else o.iri )
        
        return [
            format_triple(self.wd_ent, p, el)
            for p, o in p_o_dict.items()
            for el in o 
        ]
    
    def get_triples(self, prettify: bool = False) -> List[tuple]:
        """ Return formatted attributes and relations to other named entities """
        return (
            self.format_triples(self.attributes,      prettify=prettify, is_attr=True) +
            self.format_triples(self.relations_intra, prettify=prettify              ) +
            self.format_triples(self.relations_extra, prettify=prettify, is_attr=True)
        )
