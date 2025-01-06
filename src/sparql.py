from SPARQLWrapper import SPARQLWrapper, JSON
import csv
import re


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


def query_wikidata(query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


# Step 1: Check interaction
def check_interaction(medA, medB):
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT ?sideEffect ?sideEffectLabel
    WHERE {{
      {medA} wdt:P769 {medB}.
      ?statement ps:P769 {medB};
                 pq:P1909 ?sideEffect.

      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
      }}
    }}
    """
    return query_wikidata(query)

# Step 2: Find alternatives for Medication B
def find_alternatives(medB):
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT DISTINCT ?alternative ?alternativeLabel
    WHERE {{
      {medB} wdt:P2175 ?disorder.
      ?alternative wdt:P2175 ?disorder.
      FILTER(?alternative != {medB})
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
      }}
    }}
    """
    return query_wikidata(query)

# Step 3: Filter safe alternatives
def find_safe_alternatives(medA, alternatives):
    safe_alternatives = []
    for alt in alternatives:
        alt_code = alt["alternative"]["value"].split("/")[-1]
        query = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        ASK {{
          {medA} wdt:P769 wd:{alt_code}.
        }}
        """
        result = query_wikidata(query)
        if not result["boolean"]:
            safe_alternatives.append(alt)
    return safe_alternatives

def get_alternatives(medA, medB):
    
    drugA = "wd:" + query_drug_id(medA.strip().lower())
    drugB = "wd:" + query_drug_id(medB.strip().lower())

    # Step 1: Check interaction
    interaction_results = check_interaction(drugA, drugB)

    # Step 2: Find alternatives for Medication B
    alternatives_results = find_alternatives(drugB)
    alternatives = alternatives_results["results"]["bindings"]

    # Step 3: Find safe alternatives
    safe_alternatives = find_safe_alternatives(drugA, alternatives)

    
    # medication_names = re.findall(r"'value': '([^']+)'", str(safe_alternatives))
    values = [item['alternativeLabel']['value'] for item in safe_alternatives]
    returnString  = f"SAFE ALTERNATIVES FOR: {medB} WITH REGARDS TO {medA}, MEDICATION NAMES: " + str(values)

    return returnString

        


if __name__ == "__main__":
    query_sideeffects_by_name("zopiclone")