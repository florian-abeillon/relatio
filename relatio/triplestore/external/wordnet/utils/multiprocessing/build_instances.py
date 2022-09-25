
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from ..utils import get_contained_instances
from ...models import WordnetEntity
from .....resources import ResourceStore



def build_instances(class_:            type,
                    resource_store:    ResourceStore, 
                    resource_store_wn: ResourceStore) -> None:
    """ 
    Build instances from WordNet results 
    """

    # Use multiprocessing to speed up the process
    with ProcessPoolExecutor() as executor:

        # Iterate over every default instance
        instance_labels = [ str(instance) for instance in resource_store.values() ]

        instances_wn_list = list(tqdm(executor.map(get_contained_instances, instance_labels), 
                                     total=len(instance_labels), 
                                     desc=f"Spotting WordNet {'entities' if class_ == WordnetEntity else 'relations'}.."))

    # Create WordNet instances, and link them to default instances
    for instance, ( instances_wn, is_contained ) in tqdm(zip(resource_store.values(), instances_wn_list), 
                                                         total=len(resource_store), 
                                                         desc=f"Enriching WordNet {'entities' if class_ == WordnetEntity else 'relations'}.."):

        if instances_wn and not is_contained:
            _ = class_(instances_wn[0], resource_store, resource_store_wn)
            continue

        for instance_wn in instances_wn:
            instance_wn = class_(instance_wn, resource_store, resource_store_wn)
            instance.add_partOf(instance_wn)
