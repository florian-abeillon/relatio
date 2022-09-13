
from asgiref.sync import sync_to_async
from rdflib import OWL, RDF, RDFS
from tqdm import tqdm

import asyncio
import spacy

from .models import MODELS, Entity, WdInstance
from ...namespaces import WIKIDATA
from ...resources import ResourceStore, Quad


nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('opentapioca')



def add_eq_wd_properties(resource_store: ResourceStore) -> None:
    """ 
    Link equivalent properties 
    """
        
    # From https://www.wikidata.org/wiki/Wikidata:Relation_between_properties_in_RDF_and_in_Wikidata
    equivalent_props = [
        ( WdInstance.generate_wd_iri('P31'),   RDF.type           ),
        ( WdInstance.generate_wd_iri('P279'),  RDFS.subClassOf    ),
        ( WdInstance.generate_wd_iri('P1647'), RDFS.subPropertyOf )
    ]

    for prop1, prop2 in equivalent_props:
        resource_store.add(Quad( prop1, OWL.sameAs, prop2, WIKIDATA ))
        # TODO: Necessary? (same for OWL.inverseOf)
        resource_store.add(Quad( prop2, OWL.sameAs, prop1, WIKIDATA ))


# TODO: Turn into multithreading?
async def enrich_entities(entity_wd_set:     set, 
                          resource_store:    ResourceStore, 
                          resource_store_wd: ResourceStore) -> None:
    """
    Enrich Wikidata entities asynchronously
    """

    async def enrich_entity(queue:             asyncio.Queue, 
                            resource_store:    ResourceStore, 
                            resource_store_wd: ResourceStore) -> None:
        nonlocal pbar
    
        while not queue.empty():
            entity = await queue.get()
            await sync_to_async(entity.enrich_entity)(resource_store, resource_store_wd)
            pbar.update(1)

    
    entity_wd_queue = asyncio.Queue()
    for entity_wd in entity_wd_set:
        await entity_wd_queue.put(entity_wd)

    pbar = tqdm(total=len(entity_wd_set), desc='Enriching Wikidata named entities..')
    await asyncio.gather(*[ 
        enrich_entity(entity_wd_queue, resource_store, resource_store_wd) 
        for _ in range(5)
    ])


async def build_resources(resource_store: ResourceStore) -> ResourceStore:
    """ 
    Main function 
    """

    # Initialize ResourceStore with Wikidata class and properties
    resource_store_wd = ResourceStore(MODELS)
    # Link equivalent properties
    add_eq_wd_properties(resource_store_wd)

    # Iterate over every base entity
    entities = list(resource_store.values())
    entity_wd_set = set()
    for entity in tqdm(entities, desc="Spotting Wikidata named entities.."):

        # NER on entity
        label = nlp(str(entity))
        ents = [ ent for ent in label.ents if ent.kb_id_ ]

        if not ents:
            continue

        if str(ents[0]).lower() == str(entity).lower():
            entity_wd = Entity(ents[0], resource_store, resource_store_wd)
            entity_wd_set.add(entity_wd)
            continue

        for entity_wd in ents:
            # Build partOf entity
            entity_wd = Entity(entity_wd, resource_store, resource_store_wd)
            entity_wd_set.add(entity_wd)
            entity.add_partOf(entity_wd)

    # Enrich Wikidata entities
    await enrich_entities(entity_wd_set, resource_store, resource_store_wd)

    return resource_store_wd
