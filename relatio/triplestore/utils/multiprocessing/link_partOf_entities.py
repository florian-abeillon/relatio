
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from tqdm import tqdm
from typing import List, Tuple, Union

import re

from ...models import Entity, Relation
from ...resources import ResourceStore



def link_partOf(i:              int,
                key_label_list: List[Tuple[str, str]]) -> List[Tuple[str, 
                                                                     Union[Entity, Relation]]]:
    """
    Function to be used in multiprocessing link_partOf_entities()
    """
    
    key, label = key_label_list[i]

    partOf_list = [
        key_partOf for key_partOf, label_partOf in key_label_list
        if (
            # If instance_partOf is contained in instance, and
            label_partOf in label and 
            # Instance_partOf is not exactly instance, and
            len(label_partOf) < len(label) and
            # If instance_partOf is *really* contained in instance
            re.search(fr"\b{label_partOf}\b", label) 
        )
    ]

    return key, partOf_list
    


def link_partOf_entities(entities: ResourceStore) -> None:
    """ 
    Link partOf entities to their containing entities  
    """

    # Use multiprocessing to speed up the process
    with ProcessPoolExecutor() as executor:
        
        # ResourceStore cannot be passed to multiprocess (pickle calls __init__ of entities)
        key_label_list = [ 
            ( key, str(entity) ) for key, entity in entities.items() 
        ]
        partOf_list = list(tqdm(executor.map(partial(link_partOf, key_label_list=key_label_list),
                                             range(len(entities))), 
                                total=len(entities), 
                                desc=f"Linking partOf Entities.."))

    # Link objects
    for key, key_partOf_list in partOf_list:
        for key_partOf in key_partOf_list:
            entities[key].add_partOf(entities[key_partOf])
