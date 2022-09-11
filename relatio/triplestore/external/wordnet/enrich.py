
from spacy.tokens.doc import Doc
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
from tqdm import tqdm
from typing import List

from .models import MODELS, Entity, Relation
from ..utils import nlp
from ...resources import ResourceStore


nlp.add_pipe("spacy_wordnet", after='tagger', config={ 'lang': nlp.lang })



def remove_ents(sentence: Doc, 
                labels:   List[str] = [ 'PERSON', 'ORG' ]) -> Doc:
    """ 
    Remove entities with specific labels from sentence 
    """
    for ent in sentence.ents:
        if ent.label_ in labels:
            start, end = ent.start_char, ent.end_char
            sentence = sentence[start:end]
    return sentence


def build_instances(class_:            type,
                    resource_store:    ResourceStore, 
                    resource_store_wn: ResourceStore) -> None:
    """ 
    Build instances from WordNet results 
    """

    # Iterate over all resources
    instances = list(resource_store.values())
    for instance in tqdm(instances, desc=f"Enriching WordNet {class_.__name__}s.."):

        # NER on instance
        label = nlp(str(instance))
        # Remove Person/Organization entities
        label = remove_ents(label)

        if not label:
            continue

        if str(label[0]).lower() == str(instance).lower():
            _ = class_(label[0], resource_store, resource_store_wn)
            continue

        for instance_wn in label:
            # Build partOf entity
            instance_wn = class_(instance_wn, resource_store, resource_store_wn)
            instance.add_partOf(instance_wn)


def build_resources(entities:  ResourceStore, 
                    relations: ResourceStore) -> ResourceStore:
    """ 
    Main function 
    """

    # Initialize ResourceStore with WordNet class and properties
    resources_wn = ResourceStore(MODELS)

    # Build WordNet instances from entities/relations
    build_instances(Entity,   entities,  resources_wn)
    build_instances(Relation, relations, resources_wn)

    return resources_wn








