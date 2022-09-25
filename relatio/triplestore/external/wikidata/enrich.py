
from rdflib import OWL, RDF, RDFS

from .models import RESOURCES, WikidataInstance
from ...namespaces import WIKIDATA
from ...resources import ResourceStore, Quad
from ...utils import MULTIPROCESSING, MULTITHREADING

# Appropriate import depending on the use of multiprocessing (or not)
if MULTIPROCESSING:
    from .utils.multiprocessing import build_entities
else:
    from .utils import build_entities

# Appropriate import depending on the use of multithreading (or not)
if MULTITHREADING:
    from .utils.multithreading import enrich_entities
else:
    from .utils import enrich_entities




def add_eq_wd_properties(resource_store: ResourceStore) -> None:
    """ 
    Link equivalent properties 
    """
        
    # From https://www.wikidata.org/wiki/Wikidata:Relation_between_properties_in_RDF_and_in_Wikidata
    equivalent_props = [
        ( WikidataInstance.generate_iri_wd('P31'),   RDF.type           ),
        ( WikidataInstance.generate_iri_wd('P279'),  RDFS.subClassOf    ),
        ( WikidataInstance.generate_iri_wd('P1647'), RDFS.subPropertyOf )
    ]

    for prop1, prop2 in equivalent_props:
        resource_store.add(Quad( prop1, OWL.sameAs, prop2, WIKIDATA ))
        # TODO: Necessary? (same for OWL.inverseOf)
        resource_store.add(Quad( prop2, OWL.sameAs, prop1, WIKIDATA ))



def build_resources(resource_store: ResourceStore) -> ResourceStore:
    """ 
    Main function 
    """

    # Initialize ResourceStore with Wikidata class and properties
    resource_store_wd = ResourceStore(RESOURCES)
    # Link equivalent properties
    add_eq_wd_properties(resource_store_wd)

    # Spot Wikidata entities
    entity_wd_set = build_entities(resource_store, resource_store_wd)

    # Enrich Wikidata entities
    enrich_entities(entity_wd_set, resource_store, resource_store_wd)

    return resource_store_wd
