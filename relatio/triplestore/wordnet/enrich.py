
from spacy_wordnet.wordnet_annotator import WordnetAnnotator

import spacy

from .models import (
    ENTITY_WN, RELATION_WN, IS_WN_INSTANCE_OF,
    DOMAIN, HAS_DOMAIN,
    SYNSET, HAS_SYNSET, HAS_LEMMA, 
    DEFINITION, LEXNAME, POS,
    Domain, Synset,
    WnEntity, WnRelation
)
from ..resources import ResourceStore


nlp = spacy.load('en_core_web_sm')
nlp.add_pipe("spacy_wordnet", after='tagger', config={ 'lang': nlp.lang })



def add_resources(resources: ResourceStore) -> None:
    """ Add WordNet classes and properties """

    # Add classes
    _ = resources.get_or_add(ENTITY_WN)
    _ = resources.get_or_add(DOMAIN)
    _ = resources.get_or_add(SYNSET)

    # Add properties
    _ = resources.get_or_add(RELATION_WN)
    _ = resources.get_or_add(IS_WN_INSTANCE_OF)
    _ = resources.get_or_add(HAS_DOMAIN)
    _ = resources.get_or_add(HAS_SYNSET)
    _ = resources.get_or_add(HAS_LEMMA)
    _ = resources.get_or_add(DEFINITION)
    _ = resources.get_or_add(LEXNAME)
    _ = resources.get_or_add(POS)



def build_instances(resources: ResourceStore, class_: type) -> None:
    """ Build instances from WordNet results """

    # Iterate over all resources
    instances = list(resources.values())
    for instance in instances:

        instance_wn = nlp(instance._label)

        try:
            # Overlook proper nouns
            if instance_wn.ents[0].label_ in [ 'PERSON', 'ORG' ]:
                continue
            # TODO: Not keep only the first entity
            token = instance_wn[0]
        except IndexError:
            continue

        instance_wn = class_(token, resource_store=resources)
        # TODO: Adds relation to HD/LD instances as well, because of owl:sameAs relation?
        instance_wn.set_relatio_instance(instance)


        # Add domains
        domains = [
            Domain(domain, resource_store=resources)
            for domain in token._.wordnet.wordnet_domains()
        ]
        instance_wn.set_domains(domains)


        # Add synsets
        synsets = []
        for synset in token._.wordnet.synsets():

            lemmas = synset.lemma_names()

            synset = Synset(synset, resource_store=resources)

            # If synset is new to resources
            if synset not in resources:
                # Add lemmas to synset
                lemmas = [
                    class_(lemma, resource_store=resources)
                    for lemma in lemmas
                ]
                synset.set_lemmas(lemmas)

            synsets.append(synset)

        instance_wn.set_synsets(synsets)



def build_wn_resources(entities: ResourceStore, relations: ResourceStore) -> ResourceStore:
    """ Main function """

    resources_wn = ResourceStore()

    # Add WordNet class and properties
    add_resources(resources_wn)

    # Build WordNet instances from entities/relations
    build_instances(entities, WnEntity)
    build_instances(relations, WnRelation)

    return resources_wn








