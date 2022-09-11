
from rdflib import Dataset, Namespace
from tqdm import tqdm
from typing import (
    List, Optional, Tuple, Union
)

import pandas as pd
import re

from .models import MODELS, Entity, Relation
from .namespaces import (
    PREFIXES, 
    RELATIO_HD, RELATIO_LD, 
    SPACY, WIKIDATA, WORDNET
)
from .resources import ResourceStore
from .utils import format_path



def bind_prefixes(ds:       Dataset, 
                  relatio:  bool    = True,
                  spacy:    bool    = False, 
                  wikidata: bool    = False, 
                  wordnet:  bool    = False) -> None:
    """
    Bind prefixes to each base namespace 
    """

    namespaces = []

    if relatio:
        namespaces.extend([ 
            RELATIO_HD, RELATIO_LD 
        ])
    if spacy:
        namespaces.append(SPACY)
    if wikidata:
        namespaces.append(WIKIDATA)
    if wordnet:
        namespaces.append(WORDNET)

    for namespace in namespaces:
        ds.bind(PREFIXES[namespace], namespace)



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



def link_partOf_instances(instances: Union[List[Entity], 
                                           List[Relation]]) -> None:
    """ 
    Link partOf instances to their containing instance  
    """

    for key, instance in instances.items():
        for instance_partOf in instances.values():

            if (
                # If instance_partOf is contained in instance, and
                re.search(fr"\b{str(instance_partOf)}\b", str(instance)) and 
                # Instance_partOf is not exactly instance, and
                str(instance) != str(instance_partOf) and
                # Instance_partOf is not negated instance
                str(instance) != Relation.get_neg(str(instance_partOf))
            ):
                instances[key].add_partOf(instance_partOf)



def build_instances(df: pd.DataFrame) -> Tuple[ResourceStore,
                                               ResourceStore]:
    """ 
    Build list of triples from sets of entities/property 
    """

    entities, relations = ResourceStore(), ResourceStore()
    dims = {
        'highdim': RELATIO_HD, 'lowdim': RELATIO_LD
    }

    # Iterate over each set of entities/property
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Building Relatio instances.."):

        # For highdim and lowdim entities/property
        for key, namespace in dims.items():

            # Create instances
            subject   = build_instance(Entity,   row['ARG0_' + key], entities                                  )
            predicate = build_instance(Relation, row['B-V_'  + key], relations, is_neg=row['B-ARGM-NEG_' + key])
            object    = build_instance(Entity,   row['ARG1_' + key], entities                                  )
        
            # Create triple of instances in appropriate namespace
            add_relation(subject, predicate, object, namespace)

    # Link partOf instances
    link_partOf_instances(entities)
    link_partOf_instances(relations)

    return entities, relations



async def get_resources_ext(entities:  ResourceStore, 
                       relations: ResourceStore,
                       spacy:     bool, 
                       wikidata:  bool, 
                       wordnet:   bool         ) -> ResourceStore:
    """ 
    Fetch external data 
    """

    resources = ResourceStore()

    # Enrich entities list with SpaCy data
    if spacy:
        from .external.spacy import build_sp_resources
        resources_sp = build_sp_resources(entities)
        resources.update(resources_sp)

    # Enrich entities list with Wikidata data
    if wikidata:
        from .external.wikidata import build_wd_resources
        resources_wd = await build_wd_resources(entities)
        resources.update(resources_wd)

    # Enrich entities and relations lists with WordNet data
    if wordnet:
        from .external.wordnet import build_wn_resources
        resources_wn = build_wn_resources(entities, relations)
        resources.update(resources_wn)

    return resources



def save_triplestore(ds:       Dataset, 
                     path:     str    ,
                     filename: str    ) -> None:
    """ 
    Save triplestore into .trig file 
    """
    print("Saving triplestore..")
    path = format_path(path)
    ds.serialize(path + filename + '.trig', "trig")



async def build_triplestore(df:       pd.DataFrame, 
                            spacy:    bool         = False, 
                            wikidata: bool         = False, 
                            wordnet:  bool         = False, 
                            path:     str          = ""   ,
                            filename: str          = 'triplestore') -> Dataset:
    """ 
    Main function 
    """

    # Initialize triplestore
    ds = Dataset()
    bind_prefixes(ds, spacy=spacy, wikidata=wikidata, wordnet=wordnet)

    # Build resources
    classes_and_props = ResourceStore(MODELS)
    entities, relations = build_instances(df)

    # Enrich triplestore with external data
    resources_ext = await get_resources_ext(entities, relations, spacy, wikidata, wordnet)

    # Fill triplestore with resources
    resource_stores = [
        classes_and_props, entities,
        relations, resources_ext
    ]
    for resource_store in resource_stores:
        resource_store.to_graph(ds)

    # Save triplestore
    save_triplestore(ds, path, filename)

    print("Done!")
    return ds
