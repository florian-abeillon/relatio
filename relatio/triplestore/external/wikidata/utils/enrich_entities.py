
from tqdm import tqdm

from ....resources import ResourceStore


def enrich_entities(entity_wd_set:     set, 
                    resource_store:    ResourceStore, 
                    resource_store_wd: ResourceStore) -> None:
    """
    Enrich Wikidata entities
    """

    for entity_wd in tqdm(entity_wd_set,
                          total=len(entity_wd_set), 
                          desc=f"Enriching Wikidata named entities.."):

        entity_wd.enrich_entity(resource_store, resource_store_wd)
