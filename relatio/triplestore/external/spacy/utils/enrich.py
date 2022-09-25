
from tqdm import tqdm

from .utils import get_contained_entities
from ..models import RESOURCES, SpacyEntity
from ....resources import ResourceStore



def build_resources(resources: ResourceStore) -> ResourceStore:
    """ 
    Main function 
    """

    # Initialize ResourceStore with SpaCy models
    resources_sp = ResourceStore(RESOURCES)

    # Iterate over every base entity
    entities = list(resources.values())
    for entity in tqdm(entities, desc="Enriching SpaCy named entities.."):

        entities_sp, is_contained = get_contained_entities(str(entity))

        if is_contained:
            _ = SpacyEntity(entities_sp[0], resources, resources_sp)
            continue

        for entity_sp in entities_sp:
            # Build partOf entities
            entity_sp = SpacyEntity(entity_sp, resources, resources_sp)
            entity.add_partOf(entity_sp)

    return resources_sp
