from SPARQLWrapper import SPARQLWrapper, JSON
import json

endpoint_url = "https://query.wikidata.org/sparql"
sparql = SPARQLWrapper(endpoint_url)
sparql.addCustomHttpHeader("User-Agent", "MySPARQLQuery/1.0 (example@example.com)")

def query_drug_id(drug_name):
    query = f"""
    SELECT ?drug ?drugLabel
    WHERE {{
    ?drug rdfs:label "{drug_name}"@en.
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    id_link = results['results']['bindings'][0]['drug']['value']
    med_code = id_link.split("/")[-1]
    return med_code

def query_sideeffects_by_name(drug_name):

    med_code = query_drug_id(drug_name)

    drug = f"wd:{med_code}"  
    interaction_property = "p:P769"
    interaction_statement = "ps:P769"
    side_effect_qualifier = "pq:P1909"

    query = f"""
    SELECT ?interactingDrugLabel (GROUP_CONCAT(?sideEffectLabel; separator=", ") AS ?sideEffects) WHERE {{
    {drug} {interaction_property} ?statement.
    ?statement {interaction_statement} ?interactingDrug.
    ?interactingDrug rdfs:label ?interactingDrugLabel.
    FILTER (LANG(?interactingDrugLabel) = "en")

    OPTIONAL {{
        ?statement {side_effect_qualifier} ?sideEffect.
        ?sideEffect rdfs:label ?sideEffectLabel.
        FILTER (LANG(?sideEffectLabel) = "en")
    }}
    }} GROUP BY ?interactingDrugLabel
    """

    # Set query and format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    # Execute query
    results = sparql.query().convert()

    # Prepare data for JSON
    output_data = {}

    for binding in results['results']['bindings']:
        interacting_drug_label = binding['interactingDrugLabel']['value']
        side_effects = binding.get('sideEffects', {}).get('value', 'No side effects listed')
        side_effects_list = side_effects.split(', ') if side_effects != 'No side effects listed' else []
        output_data[interacting_drug_label] = side_effects_list

    return output_data

if __name__ == "__main__":
    query_sideeffects_by_name("zopiclone")