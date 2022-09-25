
from .models import RESOURCES, WordnetEntity, WordnetRelation
from ...resources import ResourceStore
# from ...utils import MULTIPROCESSING

# TODO: Does not work, because of some pb with NLTK and multiprocesses
# # Appropriate import depending on the use of multiprocessing (or not)
# if MULTIPROCESSING:
#     from .utils.multiprocessing import build_instances
# else:
#     from .utils import build_instances
from .utils import build_instances


def build_resources(entities:  ResourceStore, 
                    relations: ResourceStore) -> ResourceStore:
    """ 
    Main function 
    """

    # Initialize ResourceStore with WordNet class and properties
    resources_wn = ResourceStore(RESOURCES)

    # Build WordNet instances from entities/relations
    build_instances(WordnetEntity,   entities,  resources_wn)
    build_instances(WordnetRelation, relations, resources_wn)

    return resources_wn
