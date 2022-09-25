
from tqdm import tqdm

from .utils import get_contained_instances
from ....resources import ResourceStore


def build_instances(class_:            type,
                    resource_store:    ResourceStore, 
                    resource_store_wn: ResourceStore) -> None:
    """ 
    Build instances from WordNet results 
    """

    # Iterate over all resources
    instances = list(resource_store.values())
    for instance in tqdm(instances, desc=f"Enriching WordNet {class_.__name__}s.."):

        instances_wn, is_contained = get_contained_instances(str(instance))

        if is_contained:
            _ = class_(instances_wn[0], resource_store, resource_store_wn)
            continue

        for instance_wn in instances_wn:
            # Build partOf instance
            instance_wn = class_(instance_wn, resource_store, resource_store_wn)
            instance.add_partOf(instance_wn)
