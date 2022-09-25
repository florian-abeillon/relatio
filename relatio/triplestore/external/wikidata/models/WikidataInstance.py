
from pydantic import Field, root_validator
from rdflib import URIRef
from spacy.tokens.span import Span
from typing import Union

from .resources import WD_IRI
from ....namespaces import WIKIDATA
from ....resources import (
    Model, Quad, ResourceStore
)



class Ent:

    def __init__(self, ent: Span):
        self._label = str(ent)
        self.kb_id_ = ent.kb_id_

    def __str__(self) -> str:
        return self._label



class WikidataInstanceModel(Model):
    """
    Wikidata relation model definition
    """

    ent:               Union[Ent, str] = Field(..., description="Span object returned by module, or string label")
    resource_store:    ResourceStore   = Field(..., description="ResourceStore to search relation in")
    resource_store_wd: ResourceStore   = Field(..., description="ResourceStore to put relation into if it is not in resource_store")
    iri_wd:            str             = Field("",  description="Wikidata IRI")


    @root_validator
    def check_ent_or_iri(cls, values):
        """
        Check that an IRI is passed as iri_wd if ent is not an Ent
        """
        assert isinstance(values['ent'], Ent) or 'iri_wd' in values
        return values



class WikidataInstance:
    """ 
    Wikidata instance of a class/property
    """

    _namespace = WIKIDATA


    def __new__(cls, ent:               Union[Ent, str], 
                     resource_store:    ResourceStore,
                     resource_store_wd: ResourceStore,
                     iri_wd:            str             = ""):

        # Check arguments types
        _ = WikidataInstanceModel(ent=ent, resource_store=resource_store, resource_store_wd=resource_store_wd, iri_wd=iri_wd)

        return super().__new__(cls, str(ent), resource_store, resource_store_ext=resource_store_wd)
    

    def __init__(self, ent:               Union[Ent, str], 
                       resource_store:    ResourceStore,
                       resource_store_wd: ResourceStore,
                       iri_wd:            str             = ""):

        iri_wd = URIRef(iri_wd) if iri_wd else self.generate_iri_wd(ent.kb_id_)
        super().__init__(str(ent), resource_store, resource_store_ext=resource_store_wd)

        # If Wikidata entity is not already set, set it
        if not hasattr(self, '_wd_set'):

            self._iri_wd = iri_wd
            self.add_quad(
                Quad( self, WD_IRI, self._iri_wd )
            )

            self._wd_set = True


    @staticmethod
    def generate_iri_wd(id_wd: str) -> URIRef:
        """ 
        Build unique resource identifier from id_wd
        """
        return URIRef(WIKIDATA + id_wd)
