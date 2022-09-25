
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from ..utils import get_contained_entities
from ...models import RESOURCES, SpacyEntity
from .....resources import ResourceStore


def build_resources(resources: ResourceStore) -> ResourceStore:
    """ 
    Main function 
    """

    # Initialize ResourceStore with SpaCy models
    resources_sp = ResourceStore(RESOURCES)

    # Use multiprocessing to speed up the process
    with ProcessPoolExecutor() as executor:

        # Iterate over every default entity
        entity_labels = [ str(entity) for entity in resources.values() ]

        entities_sp_list = list(tqdm(executor.map(get_contained_entities, entity_labels), 
                                     total=len(entity_labels), 
                                     desc=f"Spotting SpaCy named entities.."))

    # Create SpaCy entities, and link them to default entities
    for entity, ( entities_sp, is_contained ) in tqdm(zip(resources.values(), entities_sp_list), 
                                                      total=len(resources), 
                                                      desc=f"Enriching SpaCy named entities.."):

        if entities_sp and not is_contained:
            _ = SpacyEntity(entities_sp[0], resources, resources_sp)
            continue

        for entity_sp in entities_sp:
            entity_sp = SpacyEntity(entity_sp, resources, resources_sp)
            entity.add_partOf(entity_sp)

    return resources_sp
