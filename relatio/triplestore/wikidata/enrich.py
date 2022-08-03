
from rdflib import Graph
from typing import List

from relatio.triplestore.wikidata.models import NamedEntity


def add_wd_triples(graph: Graph, ents: List[str]) -> None:
    """ Main function """

    named_ents = {}
    for ent in ents:

        # Query WikiData knowledge base
        ent = NamedEntity(ent)
        ent.query_ent()

        uri = "wd:" + ent.wid
        named_ents[uri] = ent
        
        
    for ent in named_ents.values():

        # Link named entities from text
        ent.link_ents(named_ents)
        
        # Fill triplestore
        for triple in ent.get_triples():
            graph.add(triple)
