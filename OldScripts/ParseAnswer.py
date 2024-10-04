import spacy
import re

# Charger le modèle de langue française de spaCy
nlp = spacy.load("fr_core_news_sm")

# Charger les règles de phrases depuis phrases.txt
def load_rules(filename="phrases.txt"):
    rules = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            detect_match = re.search(r'Detect:"(.*?)"', line)
            answer_match = re.search(r'Answer:"(.*?)"', line)
            if detect_match and answer_match:
                rules.append({
                    "detect": detect_match.group(1),
                    "answer": answer_match.group(1)
                })
    return rules

# Fonction pour capturer un groupe nominal complexe
def get_full_noun_chunk(token):
    components = []
    for child in token.lefts:
        if child.dep_ in {"det", "amod"}:  # Déterminants et adjectifs à gauche
            components.append(child.text)
    components.append(token.text)  # Nom principal
    for child in token.rights:
        if child.dep_ == "amod":  # Adjectifs à droite
            components.append(child.text)
        elif child.dep_ in {"punct", "cc"}:  # Arrête la capture à la ponctuation ou conjonction
            break
    return " ".join(components)

# Analyser la phrase pour capturer les objets, verbes et sujets
def parse_message(message):
    doc = nlp(message)
    parsed_structure = {
        "full_sentence": message,
        "objects": [],
        "verbs": [],
        "subjects": []
    }

    # Extraction des groupes nominaux complexes
    for token in doc:
        if token.dep_ in {"nsubj", "dobj", "pobj"}:  # Sujets, objets directs, objets de préposition
            noun_chunk = get_full_noun_chunk(token)
            if noun_chunk and not noun_chunk.lower().startswith("et"):  # Exclure les conjonctions
                parsed_structure["objects"].append(noun_chunk)

    # Extraction des verbes et des sujets associés
    for token in doc:
        if token.pos_ == "VERB":
            subject = [child.text for child in token.children if child.dep_ == "nsubj"]
            parsed_structure["verbs"].append({
                "lemma": token.lemma_,
                "text": token.text,
                "subject": subject[0] if subject else None
            })

    return parsed_structure

# Générer une réponse en fonction des règles et du message analysé
def generate_answer(parsed_message, user, rules):
    all_responses = []
    for rule in rules:
        detect = rule["detect"]
        answer = rule["answer"]
        response = ""

        # Détection des objets
        if "[objects]" in detect and parsed_message["objects"]:
            obj_response = answer
            for obj in parsed_message["objects"]:
                obj_response = obj_response.replace("[objects]", obj, 1)
            response += obj_response

        # Détection de sujet et verbe
        for verb_data in parsed_message["verbs"]:
            subject = verb_data["subject"]
            verb = verb_data["lemma"]

            if "[verb]" in detect:
                verb_response = answer.replace("[verb]", verb)
                if subject:
                    if "1stgrp" in detect and subject.lower() in {"je", "j'"}:
                        response += verb_response.replace("[user]", user)
                    elif "3stgrp" in detect and subject.lower() not in {"je", "j'", "tu"}:
                        response += verb_response.replace("[user]", user)

        if response:
            all_responses.append(response)

    # Afficher toutes les réponses possibles
    return "\n".join(all_responses) if all_responses else "Aucune réponse appropriée trouvée."

# Exemple d'utilisation
rules = load_rules()  # Charger les règles de phrases
message = "J'adore les chaussures bleues, et les pizzas sorties du four"
parsed_message = parse_message(message)
user = "User123"

# Générer et afficher toutes les réponses possibles
response = generate_answer(parsed_message, user, rules)
print(response)
