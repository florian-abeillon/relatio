
from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
from typing import List

import spacy

from .models import (
    CLASSES_AND_PROPS_WN,
    WnEntity, WnRelation
)
from ..models import ReEntity, ReInstance, ReRelation
from ..resources import ResourceStore


nlp = spacy.load('en_core_web_sm')
nlp.add_pipe("spacy_wordnet", after='tagger', config={ 'lang': nlp.lang })



def remove_ents(sentence: Doc, labels: List[str] = [ 'PERSON', 'ORG' ]) -> Doc:
    """ Remove entities with specific labels from sentence """
    for ent in sentence.ents:
        if ent.label_ in labels:
            start, end = ent.start_char, ent.end_char
            sentence = sentence[start:end]
    return sentence



def init_wn_instance(instance_wn: Token, 
                     class_wn: type, 
                     instance: ReInstance, 
                     resources_wn: ResourceStore) -> None:
    """ Initialize WordNet instances """

    instance_wn = class_wn(instance_wn, resources_wn)
    instance_wn.set_re_instance(instance)



def build_wn_instances(class_: type,
                       class_wn: type,
                       resources: ResourceStore, 
                       resources_wn: ResourceStore) -> None:
    """ Build instances from WordNet results """

    # Iterate over all resources
    instances = list(resources.values())
    for instance in instances:

        # NER on instance
        label = nlp(instance._label)
        # Remove Person/Organization entities
        label = remove_ents(label)

        if str(label[0]).lower() == instance._label.lower():
            init_wn_instance(label[0], class_wn,instance,  resources_wn)
            continue

        for instance_wn in label:
            # Build partOf Relatio entity
            re_instance = class_(instance_wn, resources)
            instance.add_partOf_instance(re_instance)

            init_wn_instance(instance_wn, class_wn, re_instance, resources_wn)



def build_wn_resources(entities: ResourceStore, relations: ResourceStore) -> ResourceStore:
    """ Main function """

    # Initialize ResourceStore with WordNet class and properties
    resources_wn = ResourceStore(CLASSES_AND_PROPS_WN)

    # Build WordNet instances from entities/relations
    build_wn_instances(ReEntity,   WnEntity,   entities,  resources_wn)
    build_wn_instances(ReRelation, WnRelation, relations, resources_wn)

    return resources_wn








