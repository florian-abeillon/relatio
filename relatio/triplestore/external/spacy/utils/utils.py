
from typing import List, Tuple

from ..models import Ent
from ...utils import nlp


def get_contained_entities(entity_label: str) -> Tuple[List[Ent], bool]:
    """ 
    NER on label to get contained entities
    """
    label = nlp(entity_label)
    ents = [ Ent(ent) for ent in label.ents ]
    is_contained = ents and str(ents[0]).lower() != entity_label.lower()
    return ents, is_contained
