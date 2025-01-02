def read_meds():
    with open('medications.csv', 'r', encoding='utf-8') as file:
        meds = [line.strip() for line in file if line.strip()] 
    return meds

def read_symptoms():
    with open('symptoms.csv', 'r', encoding='utf-8') as file:
        symptoms = [line.strip() for line in file if line.strip()]
    return symptoms