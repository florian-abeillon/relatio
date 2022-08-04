
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
from typing import List, Tuple

import spacy

from relatio.triplestore.wordnet.models import (
    ENTITY_WN, IS_WN_INSTANCE_OF, RELATION_WN, 
    HAS_LEMMA, DEFINITION, LEXNAME,
    POS, SYNSET,
    WnEntity, WnRelation
)
from relatio.triplestore.resources import ResourceStore

# TODO
# python -m nltk.downloader wordnet
# python -m nltk.downloader omw

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe("spacy_wordnet", after='tagger', config={ 'lang': nlp.lang })



def add_resources(resources: ResourceStore) -> None:
    """ Add WordNet classes and properties """
    resources.get_or_add(ENTITY_WN)
    resources.get_or_add(IS_WN_INSTANCE_OF)
    resources.get_or_add(RELATION_WN)
    resources.get_or_add(HAS_LEMMA)
    resources.get_or_add(DEFINITION)
    resources.get_or_add(LEXNAME)
    resources.get_or_add(POS)
    resources.get_or_add(SYNSET)


def get_wn_triples(entities: ResourceStore, relations: ResourceStore) -> Tuple[ResourceStore,
                                                                               List[tuple]]:
    """ Main function """

    resources_wn = ResourceStore()
    triples_wn = []

    # Add WordNet class and properties
    add_resources(resources_wn)

    for entity in entities:

        entity_wn = nlp(entity._label)

        if entity_wn.ents and entity_wn.ents[0].label_ in [ 'PERSON', 'ORG' ]:
            continue

        instance = WnEntity(entity_wn)
        instance.set_domains(entity_wn._.wordnet.wordnet_domains())

        for synset in entity_wn._.wordnet.synsets():
            synset = Synset(synset)
            resources_wn.get_or_add(synset)
            instance.add_synset(synset)

    return resources_wn, triples_wn








