
from rdflib import Dataset
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import re

from .models import (
    CLASSES_AND_PROPS,
    ReEntity, ReInstance, ReRelation
)
from .namespaces import (
    PREFIXES, 
    RELATIO, RELATIO_HD, RELATIO_LD, 
    SPACY, WIKIDATA, WORDNET
)
from .resources import ResourceStore
from .utils import format_path



def bind_prefixes(ds:       Dataset, 
                  spacy:    bool, 
                  wikidata: bool, 
                  wordnet:  bool   ) -> None:
    """
    Bind prefixes to each base namespace 
    """

    namespaces = [ RELATIO, RELATIO_HD, RELATIO_LD ]

    if spacy:
        namespaces.append(SPACY)
    if wikidata:
        namespaces.append(WIKIDATA)
    if wordnet:
        namespaces.append(WORDNET)

    for namespace in namespaces:
        ds.bind(PREFIXES[namespace], namespace)



def build_instance(class_:          type,
                   label:           str, 
                   resource_stores: Dict[str, ResourceStore],
                   hd:              bool = False,
                   **kwargs                                 ) -> Optional[ReInstance]:
    """ 
    Build instance from label 
    """

    # Overlook NAs
    if pd.isna(label):
        return None

    # Create instance in appropriate namespace
    return class_(label, 
                  resource_stores['hd_ld'], 
                  hd=hd, 
                  ld=not hd, 
                  resource_store_base=resource_stores['base'], 
                  **kwargs)



def build_hd_ld_instances(class_:          type, 
                          row:             pd.Series, 
                          key:             str, 
                          resource_stores: Dict[str, ResourceStore],
                          **kwargs                                 ) -> Tuple[ReInstance, 
                                                                              ReInstance]:
    """ 
    Build HD/LD instances from extracted concepts 
    """

    # Create instances in HD/LD namespaces
    instance_hd = build_instance(class_, 
                                 row[f"{key}_highdim"], 
                                 resource_stores,
                                 hd=True, 
                                 **kwargs.get('hd', {}))

    instance_ld = build_instance(class_, 
                                 row[f"{key}_lowdim"], 
                                 resource_stores, 
                                 hd=False, 
                                 **kwargs.get('ld', {}))

    # Set isHDInstanceOf property
    if not ( instance_hd is None or instance_ld is None ):
        instance_hd.set_ld_instance(instance_ld)
        
    return instance_hd, instance_ld



def add_relation(subject:  ReEntity, 
                 relation: ReRelation, 
                 object_:  ReEntity  ) -> None:
    """ 
    Add relation from subject to object  
    """

    if relation is None or ( subject is None and object_ is None ):
        return

    if subject is None:
        subject = object_
    elif object_ is None:
        object_ = subject
    
    subject.add_object(relation, object_)



def link_partOf_instances(instances: Union[List[ReEntity], 
                                           List[ReRelation]]) -> None:
    """ 
    Link partOf instances to their containing instance  
    """

    for key, instance in instances.items():
        for instance_partOf in instances.values():

            if (
                # If instance_partOf is contained in instance, and
                re.search(fr"\b{instance_partOf._label}\b", instance._label) and 
                # Instance_partOf is not exactly instance, and
                instance._label != instance_partOf._label and
                # Instance_partOf is not negated instance
                instance._label != "not " + instance_partOf._label
            ):
                instances[key].add_partOf_instance(instance_partOf)



def build_resources(df: pd.DataFrame) -> Tuple[Dict[str, ResourceStore], 
                                               Dict[str, ResourceStore]]:
    """ 
    Build list of triples from sets of entities/property 
    """
    print('Building Relatio resources..')

    entities  = { 'base': ResourceStore(), 'hd_ld': ResourceStore() }
    relations = { 'base': ResourceStore(), 'hd_ld': ResourceStore() }

    # Iterate over each set of entities/property
    for _, row in df.iterrows():
        
        # Build subject/object entities
        subject_hd, subject_ld = build_hd_ld_instances(ReEntity, row, 'ARG0', entities)
        object_hd,  object_ld  = build_hd_ld_instances(ReEntity, row, 'ARG1', entities)
        
        # Build relation property
        kwargs = { 
            'hd': { 'is_neg': row['B-ARGM-NEG_highdim'] }, 
            'ld': { 'is_neg': row['B-ARGM-NEG_lowdim']  } 
        }
        relation_hd, relation_ld = build_hd_ld_instances(ReRelation, row, 'B-V', relations, **kwargs)
        
        # Add HD/LD relations to objects
        add_relation(subject_hd, relation_hd, object_hd)
        add_relation(subject_ld, relation_ld, object_ld)

    # Link partOf instances
    link_partOf_instances(entities['base'])
    link_partOf_instances(relations['base'])

    return entities, relations



def get_ext_data(spacy:     bool, 
                 wikidata:  bool, 
                 wordnet:   bool, 
                 entities:  ResourceStore, 
                 relations: ResourceStore) -> ResourceStore:
    """ 
    Fetch external data 
    """

    resources = ResourceStore()

    # Enrich entities list with SpaCy data
    if spacy:
        from .spacy.enrich import build_sp_resources
        resources_sp = build_sp_resources(entities)
        resources.update(resources_sp)

    # Enrich entities list with Wikidata data
    if wikidata:
        from .wikidata.enrich import build_wd_resources
        resources_wd = build_wd_resources(entities)
        resources.update(resources_wd)

    # Enrich entities and relations lists with WordNet data
    if wordnet:
        from .wordnet.enrich import build_wn_resources
        resources_wn = build_wn_resources(entities, relations)
        resources.update(resources_wn)

    return resources



def save_triplestore(ds:   Dataset, 
                     path: str    ) -> None:
    """ 
    Save triplestore into .trig file 
    """
    print("Saving triplestore..")
    path = format_path(path)
    ds.serialize(path + 'triplestore.trig', "trig")



def build_triplestore(df:       pd.DataFrame, 
                      spacy:    bool          = False, 
                      wikidata: bool          = False, 
                      wordnet:  bool          = False, 
                      path:     str           = ""   ) -> Dataset:
    """ 
    Main function 
    """

    # Initialize triplestore
    ds = Dataset()
    bind_prefixes(ds, spacy, wikidata, wordnet)

    # Build resources
    classes_and_props = ResourceStore(CLASSES_AND_PROPS)
    entities, relations = build_resources(df)

    # Enrich triplestore with external data
    resources_ext = get_ext_data(spacy, wikidata, wordnet, entities['base'], relations['base'])

    # Fill triplestore with resources
    resource_stores = [
        classes_and_props,
        entities['base'],  entities['hd_ld'],
        relations['base'], relations['hd_ld'],
        resources_ext
    ]
    for resource_store in resource_stores:
        resource_store.to_graph(ds)

    # Save triplestore
    save_triplestore(ds, path)

    print("Done!")
    return ds



def enrich_triplestore(path:     str,
                       df:       pd.DataFrame, 
                       spacy:    bool = False, 
                       wikidata: bool = False, 
                       wordnet:  bool = False) -> Dataset:
    """ 
    Secondary function 
    """
    assert spacy or wikidata or wordnet, "Please provide one external source of information"

    # Initialize triplestore
    ds = Dataset()
    ds.parse(path, format='trig')

    # Enrich triplestore with external data
    entities, relations = build_resources(df)
    resources_ext = get_ext_data(spacy, wikidata, wordnet, entities['base'], relations['base'])

    # Fill triplestore with resources
    resources_ext.to_graph(ds)

    # Save triplestore
    save_triplestore(ds, path)

    return ds
