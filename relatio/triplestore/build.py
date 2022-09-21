
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from rdflib import Dataset
from tqdm import tqdm
from typing import List, Optional, Tuple, Union

import pandas as pd
import re

from .models import RESOURCES, Entity, Relation
from .namespaces import DEFAULT
from .resources import ResourceStore
from .utils import bind_prefixes, save_triplestore

# To remove unnecessary warnings
pd.options.mode.chained_assignment = None




def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dataframe from NAs (among other stuff)
    """

    # Put N/As when predicate is undefined (even if it is in negative form)
    df.loc[df['B-V_highdim'].isna(), 'B-V_highdim_with_neg'] = None
    df.loc[df['B-V_lowdim'].isna(),  'B-V_lowdim_with_neg']  = None

    # Filter out useless columns
    cols = [ 'ARG0_{}', 'B-V_{}_with_neg', 'ARG1_{}']
    cols = [ col.format('highdim') for col in cols ] + [ col.format('lowdim')  for col in cols ]
    df = df[cols]

    # Add other level to columns index for better convenience
    new_cols = [ 'subject', 'predicate', 'object' ]
    new_cols = [ ( 'hd', new_col ) for new_col in new_cols ] + [ ( 'ld', new_col ) for new_col in new_cols ]
    df.columns = pd.MultiIndex.from_tuples(new_cols)

    # Format predicates
    df['hd', 'predicate'] = df['hd', 'predicate'].str.replace('_', ' ')
    df['ld', 'predicate'] = df['ld', 'predicate'].str.replace('_', ' ')

    return df



def build_hd_ld_instances(class_:         type,
                          row:            pd.Series,
                          key:            str, 
                          resource_store: ResourceStore) -> Optional[Union[Entity, Relation]]:
    """ 
    Build HD and LD instances from row 
    """

    # Build instances
    instance_hd, instance_ld = None, None
    if not row['hd'].isna().any():
        instance_hd = class_(row['hd'][key], resource_store=resource_store)
    if not row['ld'].isna().any():
        instance_ld = class_(row['ld'][key], resource_store=resource_store)

    # Link HD and LD instances (if neither is None)
    if instance_hd is not None and instance_ld is not None:
        instance_hd.set_lowDim(instance_ld)

    return instance_hd



def add_relation(subject:   Entity, 
                 relation:  Relation, 
                 object_:   Entity  ) -> None:
    """ 
    Add relation from subject to object  
    """
    if subject is None or relation is None or object_ is None:
        return
    subject.add_object(relation, object_, DEFAULT)



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



# def link_partOf_entities(entities: ResourceStore) -> None:
#     """ 
#     Link partOf entities to their containing entity  
#     """

#     for key, entity in tqdm(entities.items(), 
#                               total=len(entities), 
#                               desc=f"Linking partOf Entities.."):

#         label = str(entity)

#         for entity_partOf in entities.values():
#             label_partOf = str(entity_partOf)

#             if (
#                 # If entity_partOf is contained in entity, and
#                 label_partOf in label and 
#                 # entity_partOf is not exactly entity, and
#                 len(label_partOf) < len(label) and
#                 # If entity_partOf is *really* contained in entity
#                 re.search(fr"\b{label_partOf}\b", label) 
#             ):
#                 entities[key].add_partOf(entity_partOf)



def build_instances(df: pd.DataFrame) -> Tuple[ResourceStore,
                                               ResourceStore]:
    """ 
    Build list of triples from sets of entities/property 
    """

    entities, relations = ResourceStore(), ResourceStore()
    
    # Iterate over each set of entities/property
    for _, row in tqdm(df.iterrows(), 
                       total=len(df), 
                       desc="Building Relatio instances.."):

        # Create highdim and lowdim entities/property
        subject_hd   = build_hd_ld_instances(Entity,   row, 'subject',   entities)
        predicate_hd = build_hd_ld_instances(Relation, row, 'predicate', relations)
        object_hd    = build_hd_ld_instances(Entity,   row, 'object',    entities)
    
        # Create triple of instances
        add_relation(subject_hd, predicate_hd, object_hd)

    # Link partOf instances
    link_partOf_entities(entities)

    return entities, relations



async def build_triplestore(df:       pd.DataFrame,
                            path:     str          = "./",
                            filename: str          = 'triplestore.nq') -> Dataset:
    """ 
    Main function 
    """

    # Initialize triplestore
    ds = Dataset()
    bind_prefixes(ds)

    # Clean dataset
    df = clean_df(df)

    # Build resources
    classes_and_props = ResourceStore(RESOURCES)
    entities, relations = build_instances(df)
    
    # Fill triplestore with resources
    resource_stores = [
        classes_and_props, 
        entities,
        relations
    ]
    for resource_store in resource_stores:
        resource_store.to_graph(ds)

    # Save triplestore
    save_triplestore(ds, path, filename)

    print("Done!")
    return ds
