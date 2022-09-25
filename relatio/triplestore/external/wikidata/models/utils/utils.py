
from http.client import IncompleteRead
from SPARQLWrapper import JSON, SPARQLWrapper
from typing import Dict, List


URL = 'https://query.wikidata.org/sparql'



def format_res(res: Dict[str, str]) -> List[dict]:
    """ 
    Format res
    """

    res_formatted = []

    for r in res['results']['bindings']:

        predicate = {
            'label': r['p_label']['value'], 
            'iri': r['p_iri']['value'] 
        }

        # Parse n_list
        n_list = r['n_list']['value'].split('||')
        objects, attributes, subjects = [], [], []

        for n in n_list:

            try:
                n_iri, n_label, is_obj = n.split("\\\\")
            except ValueError:
                print('ValueError with', n)

            n = { 'label': n_label, 'iri': n_iri }

            if is_obj:
                if n_iri == n_label:
                    del n['iri']
                    attributes.append(n)
                else:
                    objects.append(n)
            else:
                subjects.append(n)

        # Format results
        r_formatted = { 
            'predicate':  predicate,
            'objects':    objects,
            'attributes': attributes,
            'subjects':   subjects
        }
        res_formatted.append(r_formatted)

    return res_formatted
    


def query_triplestore(url:       str, 
                      query:     str,
                      first_try: bool = True) -> List[dict]:
    """ 
    Query triplestore knowledge base 
    """

    # Prepare query
    sparql = SPARQLWrapper(url, returnFormat=JSON)
    sparql.setQuery(query)
    
    # Query Wikidata
    res = sparql.query()
    try:
        res = res.convert()
    except IncompleteRead as err:
        if first_try:
            # If IncompleteRead error once, try again
            print('Error:', err, ', trying again')
            return query_triplestore(url, query, first_try=False)
        # If twice in a row, return empty list
        print('Error:', err, 'again, stopping')
        return []
        
    # Format and return result
    res = format_res(res)
    return res
