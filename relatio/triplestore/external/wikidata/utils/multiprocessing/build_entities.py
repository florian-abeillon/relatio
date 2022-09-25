
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from ..utils import get_contained_entities
from ...models import WikidataEntity
from .....resources import ResourceStore


def build_entities(resource_store:    ResourceStore, 
                   resource_store_wd: ResourceStore) -> set:
    """ 
    Build entities from Wikidata results 
    """

    # Use multiprocessing to speed up the process
    with ProcessPoolExecutor() as executor:

        # Iterate over every default entity
        entity_labels = [ str(entity) for entity in resource_store.values() ]

        entities_wd_list = list(tqdm(executor.map(get_contained_entities, entity_labels), 
                                     total=len(entity_labels), 
                                     desc=f"Spotting Wikidata named entities.."))

    entity_wd_set = set()

    # Create Wikidata entities, and link them to default entities
    for entity, ( entities_wd, is_contained ) in zip(resource_store.values(), entities_wd_list):

        if entities_wd and not is_contained:
            entity_wd = WikidataEntity(entities_wd[0], resource_store, resource_store_wd)
            entity_wd_set.add(entity_wd)
            continue

        for entity_wd in entities_wd:
            entity_wd = WikidataEntity(entity_wd, resource_store, resource_store_wd)
            entity_wd_set.add(entity_wd)
            entity.add_partOf(entity_wd)

    return entity_wd_set
