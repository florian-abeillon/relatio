
import spacy

from .models import CLASSES_AND_PROPS_SP, SpEntity
from ..models import ReEntity
from ..resources import ResourceStore


nlp = spacy.load("en_core_web_sm")



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
            # Build SpaCy entity, and link it to Relatio entity
            entity_wd = SpEntity(ents[0], resources_sp)
            entity_wd.set_re_entity(entity)
            continue

        for entity_wd in ents:

            # Build partOf Relatio entity
            re_entity = ReEntity(entity_wd, resources)
            entity.add_partOf_instance(re_entity)

            # Build SpaCy entity, and link it to Relatio entity
            entity_wd = SpEntity(entity_wd, resources_sp)
            entity_wd.set_re_entity(re_entity)

    return resources_sp
