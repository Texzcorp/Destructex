import random
import re

# Charger les phrases depuis un fichier texte (phrases.txt)
def load_phrases(filename="phrases.txt"):
    with open(filename, 'r', encoding='utf-8') as f:
        phrases = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                phrases.append(line)
    return phrases

def generate_answer(parsed_message, user, prefix="MrDestructoid "):
    """
    Génère une réponse en fonction des propositions analysées et d'un ensemble de phrases prédéfinies.
    
    Args:
        parsed_message (dict): Les différentes parties du message analysé (propositions, groupes nominaux).
        user (str): Le nom de l'utilisateur ayant envoyé le message.
        prefix (str): Préfixe optionnel à ajouter au début de la réponse.
    
    Returns:
        str: La réponse générée.
    """
    phrases = load_phrases()
    
    # Détection des éléments pertinents pour générer une réponse
    noun_chunks = parsed_message.get("noun_chunks", [])
    full_propos = parsed_message.get("full_propos", [])
    detected_tags = []

    if noun_chunks:
        detected_tags.extend(["[nom]"])
    if full_propos:
        detected_tags.append("[propos]")
    if user:
        detected_tags.append("[user]")

    # Calcul des scores pour les phrases
    phrase_scores = []
    for phrase in phrases:
        score = sum(1 for tag in detected_tags if tag.lower() in phrase.lower())
        if score > 0:
            phrase_scores.append((score, phrase))

    # Si aucune phrase ne correspond, retourner None
    if not phrase_scores:
        return None

    # Trier les phrases par score décroissant
    phrase_scores.sort(reverse=True)
    highest_score = phrase_scores[0][0]
    best_phrases = [phrase for score, phrase in phrase_scores if score == highest_score]

    # Choisir une phrase au hasard parmi celles avec le score le plus élevé
    phrase = random.choice(best_phrases)

    # Remplacements dans la phrase sélectionnée
    if "[nom]" in phrase and noun_chunks:
        phrase = re.sub(r'\[nom\]', random.choice(noun_chunks), phrase, flags=re.IGNORECASE)
    if "[user]" in phrase:
        phrase = re.sub(r'\[user\]', user, phrase, flags=re.IGNORECASE)
    if "[propos]" in phrase and full_propos:
        phrase = re.sub(r'\[propos\]', random.choice(full_propos), phrase, flags=re.IGNORECASE)

    # Retourner la réponse avec le préfixe
    response = f"{prefix}{phrase}"
    return response