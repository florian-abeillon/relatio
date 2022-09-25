
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from tqdm import tqdm

from ...models import WikidataEntity
from .....resources import ResourceStore



def enrich_entity(entity:            WikidataEntity, 
                  resource_store:    ResourceStore, 
                  resource_store_wd: ResourceStore) -> None: 

    entity.enrich_entity(resource_store, resource_store_wd)



def enrich_entities(entity_wd_set:     set, 
                          resource_store:    ResourceStore, 
                          resource_store_wd: ResourceStore) -> None:
    """
    Enrich Wikidata entities
    """

    # Use multithreading to speed up the process (with 5 threads, to comply with Wikidata's limitations)
    with ThreadPoolExecutor(5) as executor:

        _ = list(tqdm(executor.map(partial(enrich_entity, 
                                           resource_store=resource_store, 
                                           resource_store_wd=resource_store_wd), 
                                   entity_wd_set), 
                      total=len(entity_wd_set), 
                      desc=f"Enriching Wikidata named entities.."))
