
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
from typing import List, Tuple

from ..models import Token
from ...utils import nlp


nlp.add_pipe("spacy_wordnet", config={ 'lang': nlp.lang })


def get_contained_instances(instance_label: str) -> Tuple[List[Token], bool]:
    """ 
    NER on label to get contained instances
    """
    label = nlp(instance_label)
    # Remove Person/Organization entities
    instances = [ 
        Token(instance) for instance in label 
        if not instance.ent_type_ or not instance.ent_type_ in [ 'PERSON', 'ORG' ] 
    ]
    is_contained = instances and str(instances[0]).lower() != instance_label.lower()
    return instances, is_contained
