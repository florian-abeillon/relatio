
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from rdflib import Dataset, Namespace
from tqdm import tqdm
from typing import List, Optional, Tuple, Union

import pandas as pd
import re

from .models import MODELS, Entity, Relation
from .namespaces import RELATIO_HD, RELATIO_LD
from .resources import ResourceStore
from .utils import bind_prefixes, save_triplestore



def build_instance(class_:         type,
                   label:          str, 
                   resource_store: ResourceStore,
                   **kwargs                     ) -> Optional[Union[Entity, Relation]]:
    """ 
    Build instance from label 
    """
    # Overlook NAs
    if pd.isna(label):
        return None
    return class_(label, resource_store, **kwargs)


def build_hd_ld_instances(class_:         type,
                          row:            pd.Series,
                          key:            str, 
                          resource_store: ResourceStore,
                          **kwargs                     ) -> Tuple[Optional[Union[Entity, Relation]],
                                                                  Optional[Union[Entity, Relation]]]:
    """ 
    Build HD and LD instances from row 
    """

    # Prepare kwargs
    kwargs_hd, kwargs_ld = {}, {}
    if 'is_neg_key' in kwargs:
        kwargs_hd['is_neg'] = row[kwargs['is_neg_key'] + 'highdim']
        kwargs_ld['is_neg'] = row[kwargs['is_neg_key'] + 'lowdim']

    # Build instances
    instance_hd = build_instance(class_, row[key + 'highdim'], resource_store, **kwargs_hd)
    instance_ld = build_instance(class_, row[key + 'lowdim'],  resource_store, **kwargs_ld)

    # Link HD and LD instances (if neither is None)
    if not (instance_hd is None or instance_ld is None):
        instance_hd.set_lowDim(instance_ld)

    return instance_hd, instance_ld


def add_relation(subject:   Entity, 
                 relation:  Relation, 
                 object_:   Entity  ,
                 namespace: Namespace) -> None:
    """ 
    Add relation from subject to object  
    """

    if relation is None or ( subject is None and object_ is None ):
        return

    if subject is None:
        subject = object_
    elif object_ is None:
        object_ = subject
    
    subject.add_object(relation, object_, namespace)


def link_partOf(i:              int,
                key_label_list: List[Tuple[str, str]],
                is_relations:   bool                  = False) -> List[Tuple[str, 
                                                                           Union[Entity, Relation]]]:
    """
    Function to be used in multiprocessing link_partOf_instances()
    """
    
    key, label = key_label_list[i]
    if is_relations:
        label_neg = Relation.get_neg(label)

    partOf_list = [
        key_partOf for key_partOf, label_partOf in key_label_list
        if (
            # If instance_partOf is contained in instance, and
            label_partOf in label and 
            # Instance_partOf is not exactly instance, and
            len(label_partOf) < len(label) and
            # Instance_partOf is not negated instance, and
            ( not is_relations or label_neg != label_partOf ) and
            # If instance_partOf is *really* contained in instance
            re.search(fr"\b{label_partOf}\b", label) 
        )
    ]

    return key, partOf_list
    

def link_partOf_instances(instances:    ResourceStore,
                          is_relations: bool          = False) -> None:
    """ 
    Link partOf instances to their containing instance  
    """

    # Use multiprocessing to speed up the process
    with ProcessPoolExecutor() as executor:
        
        # ResourceStore cannot be passed to multiprocess (pickle calls __init__ of instances)
        key_label_list = [ 
            ( key, str(instance) ) for key, instance in instances.items() 
        ]
        partOf_list = list(tqdm(executor.map(partial(link_partOf,
                                                     key_label_list=key_label_list,
                                                     is_relations=is_relations),
                                             range(len(instances))), 
                                total=len(instances), 
                                desc=f"Linking partOf {'Relations' if is_relations else 'Entities'}.."))

    # Link objects
    for key, key_partOf_list in partOf_list:
        for key_partOf in key_partOf_list:
            instances[key].add_partOf(instances[key_partOf])


# TODO: To put in other file?
# def link_partOf_instances(instances:    ResourceStore,
#                           is_relations: bool          = False) -> None:
#     """ 
#     Link partOf instances to their containing instance  
#     """

#     for key, instance in tqdm(instances.items(), 
#                     total=len(instances), 
#                     desc=f"Linking partOf {'Relations' if is_relations else 'Entities'}.."):

#         label = str(instance)
#         if is_relations:
#             label_neg = Relation.get_neg(label)

#         for instance_partOf in instances.values():
#             label_partOf = str(instance_partOf)

#             if (
#                 # If instance_partOf is contained in instance, and
#                 label_partOf in label and 
#                 # Instance_partOf is not exactly instance, and
#                 len(label_partOf) < len(label) and
#                 # Instance_partOf is not negated instance, and
#                 ( not is_relations or label_neg != label_partOf ) and
#                 # If instance_partOf is *really* contained in instance
#                 re.search(fr"\b{label_partOf}\b", label) 
#             ):
#                 instances[key].add_partOf(instance_partOf)


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
        subject_hd,   subject_ld   = build_hd_ld_instances(Entity,   row, 'ARG0_', entities                           )
        predicate_hd, predicate_ld = build_hd_ld_instances(Relation, row, 'B-V_',  relations, is_neg_key='B-ARGM-NEG_')
        object_hd,    object_ld    = build_hd_ld_instances(Entity,   row, 'ARG1_', entities                           )
    
        # Create triple of instances in appropriate namespace
        add_relation(subject_hd, predicate_hd, object_hd, RELATIO_HD)
        add_relation(subject_ld, predicate_ld, object_ld, RELATIO_LD)

    # Link partOf instances
    link_partOf_instances(entities)
    link_partOf_instances(relations, is_relations=True)     # Rather link neg?

    return entities, relations


async def build_triplestore(df:       pd.DataFrame,
                            path:     str          = "./",
                            filename: str          = 'triplestore.nq') -> Dataset:
    """ 
    Main function 
    """

    # Initialize triplestore
    ds = Dataset()
    bind_prefixes(ds, relatio=True)

    # Build resources
    classes_and_props = ResourceStore(MODELS)
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
