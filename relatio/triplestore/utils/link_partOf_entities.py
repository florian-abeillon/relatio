
from tqdm import tqdm
import re

from ..resources import ResourceStore


def link_partOf_entities(entities: ResourceStore) -> None:
    """ 
    Link partOf entities to their containing entity  
    """

    for key, entity in tqdm(entities.items(), 
                            total=len(entities), 
                            desc=f"Linking partOf Entities.."):

        label = str(entity)

        for entity_partOf in entities.values():
            label_partOf = str(entity_partOf)

            if (
                # If entity_partOf is contained in entity, and
                label_partOf in label and 
                # entity_partOf is not exactly entity, and
                len(label_partOf) < len(label) and
                # If entity_partOf is *really* contained in entity
                re.search(fr"\b{label_partOf}\b", label) 
            ):
                entities[key].add_partOf(entity_partOf)
