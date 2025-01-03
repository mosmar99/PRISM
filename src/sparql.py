from SPARQLWrapper import SPARQLWrapper, JSON
import json, csv

endpoint_url = "https://query.wikidata.org/sparql"
sparql = SPARQLWrapper(endpoint_url)
sparql.addCustomHttpHeader("User-Agent", "MySPARQLQuery/1.0 (example@example.com)")

def query_drug_id(drug_name):
    query = f"""
    SELECT ?drug
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

def query_symptom_id(symptom_name):
    query = f"""
    SELECT ?symptom
    WHERE {{
    ?symptom rdfs:label "{symptom_name}"@en.
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    id_link = results['results']['bindings'][0]['symptom']['value']
    symptom_code = id_link.split("/")[-1]
    return symptom_code

def get_all_meds():
    has_use = "wdt:P366"
    medication = "wd:Q12140"

    query = f"""
    SELECT ?drug ?drugLabel
    WHERE {{
    ?drug {has_use} {medication}.  
    ?drug rdfs:label ?drugLabel.
    FILTER (LANG(?drugLabel) = "en")
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    meds = []
    for drug in results['results']['bindings']:
        meds.append(drug['drugLabel']['value'])
    
    output_file = 'medications.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for med in meds:
            writer.writerow([med])

    print(f"Medications have been written to {output_file}.")

def find_medicine_on_symptom_treated(symptom):

    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT DISTINCT ?medicine ?medicine_label
    WHERE {{
      ?medicine wdt:P2175 {symptom}.
      ?medicine rdfs:label ?medicine_label
    FILTER (LANG(?medicine_label) = "en")
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()

    # print(result)
    formatted_result = []
    for item in result["results"]["bindings"]:
        formatted_result.append(f"{item["medicine_label"]["value"]}")
        
    #print(formatted_result)
    return formatted_result

def get_all_symptoms():
    instance_of = "wdt:P31"
    symptom = "wd:Q112965645"
    disease = "wd:Q112193867"
    treatment_drug = "wdt:P2176"

    query = f"""
      SELECT DISTINCT ?medicalCondition ?medicalConditionLabel WHERE {{
      {{?medicalCondition {instance_of} {symptom}}}
      UNION
      {{?medicalCondition {instance_of} {disease}}}.
      ?medicalCondition {treatment_drug} ?medicine.

      ?medicalCondition rdfs:label ?medicalConditionLabel.
      FILTER (LANG(?medicalConditionLabel) = "en")
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    symptoms = []

    for result in results["results"]["bindings"]:
        symptoms.append(result["medicalConditionLabel"]["value"])

    output_file = "symptoms.csv"
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(symptoms)

    print(f"Conditions have been written to {output_file}")

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