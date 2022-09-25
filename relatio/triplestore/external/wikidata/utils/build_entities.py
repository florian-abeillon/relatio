
from tqdm import tqdm

from .utils import get_contained_entities
from ..models import WikidataEntity
from ....resources import ResourceStore


def build_entities(resource_store:    ResourceStore, 
                   resource_store_wd: ResourceStore) -> set:
    """ 
    Build entities from Wikidata results 
    """

    # Iterate over all resources
    entities = list(resource_store.values())
    entity_wd_set = set()

    for entity in tqdm(entities, desc=f"Spotting Wikidata named entities.."):

        entities_wd, is_contained = get_contained_entities(str(entity))

        if is_contained:
            entity_wd = WikidataEntity(entities_wd[0], resource_store, resource_store_wd)
            entity_wd_set.add(entity_wd)
            continue

        for entity_wd in entities_wd:
            # Build partOf entity
            entity_wd = WikidataEntity(entity_wd, resource_store, resource_store_wd)
            entity_wd_set.add(entity_wd)
            entity.add_partOf(entity_wd)

    return entity_wd_set
