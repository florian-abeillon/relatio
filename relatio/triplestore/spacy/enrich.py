
from spacy.tokens.span import Span

import spacy

from .models import CLASSES_AND_PROPS_SP, SpEntity
from ..models import ReEntity
from ..resources import ResourceStore


nlp = spacy.load("en_core_web_sm")



def init_sp_instance(entity_sp: Span, 
                     entity: ReEntity,
                     resources_sp: ResourceStore) -> None:
    """ Initialize SpaCy instances """

    entity_sp = SpEntity(entity_sp, resources_sp)
    entity_sp.set_re_entity(entity)


def build_sp_resources(resources: ResourceStore) -> ResourceStore:
    """ Main function """

    # Initialize ResourceStore with SpaCy class and properties
    resources_sp = ResourceStore(CLASSES_AND_PROPS_SP)

    # Iterate over every base entity
    entities = list(resources.values())
    for entity in entities:

        # NER on entity
        label = nlp(entity._label)
        ents = label.ents

        if not ents:
            continue

        if ents[0].label_.lower() == entity._label.lower():
            init_sp_instance(ents[0], entity, resources_sp)
            continue

        for entity_sp in ents:
            # Build partOf Relatio entity
            re_entity = ReEntity(entity_sp, resources)
            entity.add_partOf_instance(re_entity)

            init_sp_instance(entity_sp, re_entity, resources_sp)

    return resources_sp
