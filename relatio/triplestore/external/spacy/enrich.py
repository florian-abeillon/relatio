
from tqdm import tqdm

from .models import MODELS, Entity
from ..utils import nlp
from ...resources import ResourceStore



def build_resources(resources: ResourceStore) -> ResourceStore:
    """ 
    Main function 
    """

    # Initialize ResourceStore with SpaCy models
    resources_sp = ResourceStore(MODELS)

    # Iterate over every base entity
    entities = list(resources.values())
    for entity in tqdm(entities, desc="Enriching SpaCy named entities.."):

        # NER on entity
        label = nlp(str(entity))
        ents = label.ents

        if not ents:
            continue

        if str(ents[0]).lower() == str(entity).lower():
            _ = Entity(ents[0], resources, resources_sp)
            continue

        for ent in ents:
            # Build partOf entities
            entity_sp = Entity(ent, resources, resources_sp)
            entity.add_partOf(entity_sp)

    return resources_sp
