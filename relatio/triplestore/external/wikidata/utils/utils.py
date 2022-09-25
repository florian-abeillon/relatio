
from typing import List, Tuple

from ..models import Ent
from ...utils import nlp


nlp.add_pipe('opentapioca')


def get_contained_entities(entity_label: str) -> Tuple[List[Ent], bool]:
    """ 
    NER on label to get contained entities
    """
    label = nlp(entity_label)
    entities = [ Ent(ent) for ent in label.ents if ent.kb_id_ ]
    is_contained = entities and str(entities[0]).lower() != entity_label.lower()
    return entities, is_contained
