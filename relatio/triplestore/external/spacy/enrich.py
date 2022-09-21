
from concurrent.futures import ProcessPoolExecutor
from spacy.tokens.span import Span
from tqdm import tqdm
from typing import Dict, List, Tuple

from .models import MODELS, Entity
from ..utils import nlp
from ...resources import ResourceStore



# def build_resource(entity_label: str) -> Tuple[List[Span], bool]:
#     """ 
#     Function to be used in multiprocessing build_resources()
#     """

#     # NER on entity
#     label = nlp(entity_label)
#     ents = label.ents

#     if not ents:
#         return [], False

#     if str(ents[0]).lower() == entity_label.lower():
#         return [ents[0]], False

#     return [ ent for ent in ents ], True



# def build_resources(resources: ResourceStore) -> ResourceStore:
#     """ 
#     Main function 
#     """

#     # Initialize ResourceStore with SpaCy models
#     resources_sp = ResourceStore(MODELS)

#     # Use multiprocessing to speed up the process
#     with ProcessPoolExecutor() as executor:

#         # Iterate over every default entity
#         entity_labels = [ str(entity) for entity in resources.values() ]

#         entities_sp_list = list(tqdm(executor.map(build_resource, entity_labels), 
#                                      total=len(entity_labels), 
#                                      desc=f"Spotting SpaCy named entities.."))

#     # Create SpaCy entities, and link them to default entities
#     for entity, ( entities_sp, is_contained ) in tqdm(zip(resources.values(), entities_sp_list), 
#                                                       desc="Enriching SpaCy named entities.."):
#         for entity_sp in entities_sp:
#             entity_sp = Entity(entity_sp, resources, resources_sp)
#             if is_contained:
#                 entity.add_partOf(entity_sp)

#     return resources_sp



def build_resources(resources: ResourceStore) -> ResourceStore:
    """ 
    Main function 
    """

    # Initialize ResourceStore with SpaCy models
    resources_sp = ResourceStore(MODELS)

    # Iterate over every base entity
    entities = list(resources.values())
    for entity in tqdm(entities, desc="Enriching SpaCy named entities.."):

        # NER on entity
        label = nlp(str(entity))
        ents = label.ents

        if not ents:
            continue

        if str(ents[0]).lower() == str(entity).lower():
            _ = Entity(ents[0], resources, resources_sp)
            continue

        for ent in ents:
            # Build partOf entities
            entity_sp = Entity(ent, resources, resources_sp)
            entity.add_partOf(entity_sp)

    return resources_sp
