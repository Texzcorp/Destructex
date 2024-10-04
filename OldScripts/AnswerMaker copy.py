import spacy
import random
import re
from verbecc import Conjugator

# Charger le modèle de langue française de spaCy
nlp = spacy.load("fr_core_news_sm")

def parse_message(message):
    doc = nlp(message)
    noun_chunks = []
    for chunk in doc.noun_chunks:
        # Exclure les chunks qui sont des pronoms
        if not any(token.pos_ == 'PRON' for token in chunk):
            noun_chunks.append(chunk.text.strip())
    name = None
    verb = None
    mood = None
    tense = None
    person = None
    original_verb_form = None
    other_elements = []
    selected_chunks = []

    if noun_chunks:
        # Trier les groupes nominaux par longueur (le plus long d'abord)
        sorted_chunks = sorted(noun_chunks, key=lambda chunk: len(chunk.split()), reverse=True)

        # Sélectionner le premier groupe nominal (le plus long)
        selected_chunks.append(sorted_chunks[0])
        selected_words = set(sorted_chunks[0].split())  # Mots du premier groupe

        # Sélectionner d'autres groupes nominaux sans conflit avec le premier
        for chunk in sorted_chunks[1:]:
            chunk_words = set(chunk.split())
            if not selected_words.intersection(chunk_words):  # Si aucun mot ne se chevauche
                selected_chunks.append(chunk)
                selected_words.update(chunk_words)  # Ajouter les nouveaux mots à la sélection

        # Choisir un groupe nominal aléatoire parmi ceux sélectionnés
        name = random.choice(selected_chunks)
        print(f"Nom détecté : {name}")  # Log

    # Détection du premier verbe, de sa conjugaison, et du temps
    for token in doc:
        if token.pos_ == 'VERB':
            verb = token.lemma_  # Utiliser le lemme pour la conjugaison
            original_verb_form = token.text  # Forme originale du verbe dans le message
            person = token.morph.get('Person')[0] if token.morph.get('Person') else None
            mood = token.morph.get('Mood')[0] if token.morph.get('Mood') else 'Ind'  # Indicatif par défaut
            tense = token.morph.get('Tense')[0] if token.morph.get('Tense') else 'Pres'  # Présent par défaut
            print(f"Verbe détecté : {verb}, Forme originale : {original_verb_form}, Personne : {person}, Mood : {mood}, Temps : {tense}")  # Log
            break  # On arrête après le premier verbe

        # Détection d'autres éléments (adjectifs, adverbes, etc.)
        if token.pos_ in ['ADJ', 'ADV', 'PRON'] and not other_elements:
            other_elements.append(token.text)
            print(f"Élément détecté : {token.text}")  # Log

    return name, verb, mood, tense, person, original_verb_form, other_elements

def adjust_noun_form(noun_phrase, phrase):
    """
    Ajuste la forme du groupe nominal (singulier/pluriel) en fonction du contexte de la phrase.
    Ajoute l'article défini approprié si nécessaire.
    """
    doc = nlp(noun_phrase)
    base_form = None
    number = None
    gender = None

    for token in doc:
        if token.pos_ == 'NOUN':
            base_form = token.lemma_
            number = token.morph.get('Number', ['Sing'])[0]
            gender = token.morph.get('Gender', ['Fem'])[0]  # Féminin par défaut

    if base_form is None:
        # Aucun nom trouvé, ne pas ajuster
        print(f"Aucun nom trouvé dans '{noun_phrase}'.")  # Log
        return phrase

    # Déterminer l'article défini approprié
    if number == 'Plur':
        article = 'les'
    else:
        article = 'la' if gender == 'Fem' else 'le'

    # Construire le nom avec l'article
    noun_with_article = f"{article} {base_form}"

    # Remplacer les placeholders de manière insensible à la casse
    if re.search(r'\[nom\]', phrase, re.IGNORECASE):
        phrase = re.sub(r'\[nom\]', base_form, phrase, flags=re.IGNORECASE)
        print(f"Remplacement [nom] par '{base_form}'.")  # Log
    if re.search(r'\[nom_det\]', phrase, re.IGNORECASE):
        phrase = re.sub(r'\[nom_det\]', noun_with_article, phrase, flags=re.IGNORECASE)
        print(f"Remplacement [nom_det] par '{noun_with_article}'.")  # Log
    if re.search(r'\[nom_pluriel\]', phrase, re.IGNORECASE):
        if number == 'Plur':
            plural_form = noun_phrase
        else:
            plural_form = base_form + 's'  # Simplification
        phrase = re.sub(r'\[nom_pluriel\]', plural_form, phrase, flags=re.IGNORECASE)
        print(f"Remplacement [nom_pluriel] par '{plural_form}'.")  # Log
    if re.search(r'\[nom_pluriel_det\]', phrase, re.IGNORECASE):
        if number == 'Plur':
            plural_form = noun_phrase
        else:
            plural_form = base_form + 's'  # Simplification
        plural_with_article = f"les {plural_form}"
        phrase = re.sub(r'\[nom_pluriel_det\]', plural_with_article, phrase, flags=re.IGNORECASE)
        print(f"Remplacement [nom_pluriel_det] par '{plural_with_article}'.")  # Log

    return phrase

def adjust_person_for_response(person):
    """
    Ajuste la personne grammaticale pour la réponse du bot.
    Transforme 'je' en 'tu', 'tu' en 'je', 'nous' en 'vous', etc.
    Si 'person' est None, attribue une personne aléatoire.
    """
    person_mapping = {
        1: 2,  # 'je' -> 'tu'
        2: 1,  # 'tu' -> 'je'
        3: 3,  # 'il/elle/on' reste 'il/elle'
        4: 5,  # 'nous' -> 'vous'
        5: 4,  # 'vous' -> 'nous'
        6: 6   # 'ils/elles' restent 'ils/elles'
    }

    if person is None:
        # Attribuer une personne aléatoire si non détectée
        person = random.randint(1, 6)
        print(f"Personne non détectée, assignation aléatoire : {person}")  # Log

    try:
        person = int(person)
    except (ValueError, TypeError):
        # En cas d'erreur de conversion, assigner une personne par défaut
        person = 2  # 'tu'
        print(f"Erreur de conversion de 'person', assignation par défaut : {person}")  # Log

    return person_mapping.get(person, person)


def get_pronoun(person):
    """
    Retourne le pronom personnel correspondant à la personne grammaticale.
    """
    pronoun_mapping = {
        1: 'je',
        2: 'tu',
        3: 'il',
        4: 'nous',
        5: 'vous',
        6: 'ils'
    }
    return pronoun_mapping.get(person, '')

def conjugate_verb(verb, mood=None, tense=None, person=None, original_verb_form=None):
    """
    Conjugue le verbe selon le mode, le temps et la personne fournis.
    Si la conjugaison échoue, retourne la forme originale du verbe du message de l'utilisateur.
    """
    conjugator = Conjugator('fr')

    mood_mapping = {
        'Ind': 'Indicatif',
        'Subj': 'Subjonctif',
        'Imp': 'Impératif',
        'Cond': 'Conditionnel',
        'Inf': 'Infinitif',
        'Part': 'Participe',
        'Ger': 'Gérondif',
        # Ajout des formes complètes en minuscules
        'indicative': 'Indicatif',
        'imperative': 'Impératif',
        'conditional': 'Conditionnel',
        'subjunctive': 'Subjonctif',
        'participle': 'Participe',
        'infinitive': 'Infinitif',
        'indicatif': 'Indicatif',
        'impératif': 'Impératif',
        'conditionnel': 'Conditionnel',
        'subjonctif': 'Subjonctif',
        'participe': 'Participe',
        'infinitif': 'Infinitif'
    }

    tense_mapping = {
        'Pres': 'Présent',
        'Fut': 'Futur',
        'Imp': 'Imparfait',
        'Past': 'Passé composé',
        'Pqp': 'Plus-que-parfait',
        'Pass': 'Passé simple',
        'Présent': 'Présent',
        'Imparfait': 'Imparfait',
        'Futur': 'Futur',
        'Passé': 'Passé',
        'Passé composé': 'Passé composé',
        'Plus-que-parfait': 'Plus-que-parfait'
    }

    person_mapping = {
        '1': '1s',  # je
        '2': '2s',  # tu
        '3': '3s',  # il/elle/on
        '4': '1p',  # nous
        '5': '2p',  # vous
        '6': '3p'   # ils/elles
    }

    # Convertir les valeurs de mood, tense, person en chaînes de caractères en minuscules
    mood = mood.lower() if mood else 'indicatif'
    tense = tense.lower() if tense else 'présent'
    person = str(person) if person else None

    # Map the mood and tense using the corrected mappings
    mood = mood_mapping.get(mood, 'Indicatif')
    if mood in ['Infinitif', 'Participe', 'Gérondif']:
        person = None
        if mood == 'Infinitif':
            tense = 'Présent'
        elif mood == 'Participe':
            tense = 'Passé' if tense == 'passé' else 'Présent'
        else:
            tense = 'Présent'
    else:
        tense = tense_mapping.get(tense, 'Présent')
        # Personne est déjà gérée dans adjust_person_for_response
        # Ici, on laisse person à None pour que adjust_person_for_response le gère

    try:
        conjugations = conjugator.conjugate(verb)
        if 'moods' not in conjugations:
            print(f"Conjugations not found for verb '{verb}'")
            return original_verb_form if original_verb_form else verb  # Return original verb form

        moods = conjugations['moods']
        if mood not in moods:
            print(f"Mood '{mood}' not found in conjugations for verb '{verb}'")
            return original_verb_form if original_verb_form else verb

        tenses = moods[mood]
        if tense not in tenses:
            print(f"Tense '{tense}' not found in mood '{mood}' for verb '{verb}'")
            return original_verb_form if original_verb_form else verb

        if person is not None:
            response_person = adjust_person_for_response(person)
            person_key = person_mapping.get(str(response_person))
            if person_key is None or person_key not in tenses[tense]:
                print(f"Person '{person_key}' not found in tense '{tense}' for verb '{verb}'")
                return original_verb_form if original_verb_form else verb
            conjugated_verb = tenses[tense][person_key]
            print(f"Conjugué : {conjugated_verb}")  # Log
        else:
            conjugated_verb = tenses[tense]
            if isinstance(conjugated_verb, dict):
                # Si le participe renvoie un dict, prendre le 'Passé' ou 'Présent'
                conjugated_verb = conjugated_verb.get('Passé') or conjugated_verb.get('Présent')
            print(f"Conjugué (sans personne) : {conjugated_verb}")  # Log
    except Exception as e:
        print(f"Erreur lors de la conjugaison du verbe '{verb}': {e}")
        conjugated_verb = original_verb_form if original_verb_form else verb

    return conjugated_verb

def generate_answer(name, verb, mood, tense, person, original_verb_form, user, prefix="MrDestructoid "):
    if not name and not verb:
        return None

    # Lire le fichier phrases.txt en ignorant les lignes vides et les commentaires
    with open('phrases.txt', 'r', encoding='utf-8') as f:
        phrases = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                phrases.append(line)
    print(f"Phrases chargées : {phrases}")  # Log

    detected_tags = []
    if name:
        detected_tags.extend(["[nom]", "[nom_det]", "[nom_pluriel]", "[nom_pluriel_det]"])
    if verb:
        detected_tags.extend(["[verbe]", "[verbe_pron]", "[verbe_inf]", "[verbe_pp]"])
    if user:
        detected_tags.append("[user]")

    print(f"Tags détectés : {detected_tags}")  # Log

    # Calcul des scores pour les phrases
    phrase_scores = []
    for phrase in phrases:
        score = sum(1 for tag in detected_tags if tag.lower() in phrase.lower())
        if score > 0:
            phrase_scores.append((score, phrase))

    print(f"Phrases avec score : {phrase_scores}")  # Log

    if not phrase_scores:
        print("Aucune phrase correspondante trouvée.")  # Log
        return None

    # Trier les phrases par score décroissant
    phrase_scores.sort(reverse=True)
    highest_score = phrase_scores[0][0]
    best_phrases = [phrase for score, phrase in phrase_scores if score == highest_score]

    print(f"Meilleures phrases : {best_phrases}")  # Log

    # Choisir une phrase au hasard parmi celles avec le score le plus élevé
    phrase = random.choice(best_phrases)
    print(f"Phrase sélectionnée : {phrase}")  # Log

    if name:
        phrase = adjust_noun_form(name, phrase)
        print(f"Phrase après ajustement du nom : {phrase}")  # Log

    if verb:
        if re.search(r'\[verbe_pron\]', phrase, re.IGNORECASE):
            # Ajuster la personne pour la réponse
            response_person = adjust_person_for_response(person)
            conjugated = conjugate_verb(verb, mood, tense, response_person, original_verb_form)
            pronoun = get_pronoun(response_person)
            # Gérer l'élision pour 'je' devant une voyelle ou un 'h' muet
            if pronoun.lower() == 'je' and conjugated[0].lower() in 'aeiouh':
                pronoun = "j'"
                verb_phrase = f"{pronoun}{conjugated}"
            else:
                verb_phrase = f"{pronoun} {conjugated}"
            phrase = re.sub(r'\[verbe_pron\]', verb_phrase, phrase, flags=re.IGNORECASE)
            print(f"Phrase après remplacement [verbe_pron] : {phrase}")  # Log

        if re.search(r'\[verbe\]', phrase, re.IGNORECASE):
            # Conjuguer le verbe sans le pronom
            response_person = adjust_person_for_response(person)
            conjugated = conjugate_verb(verb, mood, tense, response_person, original_verb_form)
            phrase = re.sub(r'\[verbe\]', conjugated, phrase, flags=re.IGNORECASE)
            print(f"Phrase après remplacement [verbe] : {phrase}")  # Log

        if re.search(r'\[verbe_inf\]', phrase, re.IGNORECASE):
            # Utiliser la forme infinitive
            infinitive = conjugate_verb(verb, mood='Inf', tense='Pres', original_verb_form=original_verb_form)
            phrase = re.sub(r'\[verbe_inf\]', infinitive, phrase, flags=re.IGNORECASE)
            print(f"Phrase après remplacement [verbe_inf] : {phrase}")  # Log

        if re.search(r'\[verbe_pp\]', phrase, re.IGNORECASE):
            # Utiliser le participe passé
            participle = conjugate_verb(verb, mood='Part', tense='Past', original_verb_form=original_verb_form)
            phrase = re.sub(r'\[verbe_pp\]', participle, phrase, flags=re.IGNORECASE)
            print(f"Phrase après remplacement [verbe_pp] : {phrase}")  # Log

    # Remplacer [user] de manière insensible à la casse
    if re.search(r'\[user\]', phrase, re.IGNORECASE):
        replacement_user = user if user else "Utilisateur"
        phrase = re.sub(r'\[user\]', replacement_user, phrase, flags=re.IGNORECASE)
        print(f"Phrase après remplacement [user] : {phrase}")  # Log

    response = phrase

    # Vérifier s'il reste des placeholders
    remaining_placeholders = re.findall(r'\[.*?\]', response)
    if remaining_placeholders:
        print(f"Placeholders restants détectés : {remaining_placeholders}")  # Log
        # Ne pas envoyer la réponse et logguer l'événement
        print("Réponse contenant des placeholders non remplacés. La réponse ne sera pas envoyée.")
        return None

    response = response.strip()
    print(f"Phrase finale avant renvoi : {response}")  # Log

    if response and not re.search(r'\[.*?\]', response):
        return f"{prefix}{response}"
    return None
