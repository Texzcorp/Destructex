import spacy
import re

# Charger le modèle linguistique français de spaCy
nlp = spacy.load("fr_core_news_md")

def nettoyer_message(text):
    """
    Nettoie le message en supprimant ou en isolant les émoticônes et les symboles.
    """
    # Supprimer les émoticônes et les symboles courants de Twitch (approche simplifiée)
    # Garder les apostrophes et les tirets pour les contractions et les mots composés
    text = re.sub(r'[^\w\s\'-]', '', text)
    return text

def extraire_phrases_cle(text):
    """
    Extrait les groupes nominaux complets (incluant les relations prépositionnelles) et les verbes principaux du texte.
    Élimine les groupes nominaux partiels qui sont inclus dans des groupes nominaux plus complets.
    Élimine les groupes nominaux dont le noyau est un pronom.
    
    Retourne :
        - groupes_nominaux_finals : Liste des groupes nominaux extraits
        - verbes : Liste des verbes extraits
    """
    # Nettoyer le message
    text = nettoyer_message(text)
    
    doc = nlp(text)
    groupes_nominaux = []
    verbes = []

    # Extraire les verbes principaux (ROOT) et les verbes auxiliaires
    for token in doc:
        if token.pos_ == "VERB" and (token.dep_ == "ROOT" or token.dep_ == "aux"):
            verbes.append(token.lemma_)  # Utiliser le lemme pour une forme de base

    # Extraire les groupes nominaux complets en utilisant la subtree
    for chunk in doc.noun_chunks:
        # Exclure les groupes nominaux dont le noyau est un pronom
        if chunk.root.pos_ == "PRON":
            continue
        # Obtenir tous les tokens dans le sous-arbre du chunk
        subtree = list(chunk.root.subtree)
        # Trier les tokens par leur position dans le texte
        subtree = sorted(subtree, key=lambda x: x.i)
        # Reconstituer la phrase
        extended_phrase = ' '.join([token.text for token in subtree])
        # Nettoyer les espaces après les apostrophes (ex: "l' arbre" -> "l'arbre")
        extended_phrase = extended_phrase.replace("l' ", "l'").replace("d' ", "d'").replace("c' ", "c'")
        groupes_nominaux.append(extended_phrase)

    # Enlever les doublons
    groupes_nominaux = list(set(groupes_nominaux))

    # Filtrer les groupes nominaux partiels
    # Garder uniquement les groupes nominaux qui ne sont pas entièrement inclus dans un autre
    groupes_nominaux_finals = []
    for gn in groupes_nominaux:
        if not any((gn != autre) and (gn in autre) for autre in groupes_nominaux):
            groupes_nominaux_finals.append(gn)

    return groupes_nominaux_finals, verbes

def traiter_phrase(message):
    """
    Traite une seule phrase : extraction des groupes nominaux et des verbes.
    
    Retourne :
        - dict contenant la phrase originale, les groupes nominaux extraits et les verbes extraits
    """
    groupes_nominaux, verbes = extraire_phrases_cle(message)
    resultat = {
        "phrase": message,
        "groupes_nominaux": groupes_nominaux,
        "verbes": verbes
    }
    return resultat

def main():
    """
    Fonction principale pour traiter plusieurs messages.
    
    Retourne :
        - liste de dictionnaires contenant les résultats d'extraction pour chaque message
    """
    # Liste de phrases de chat Twitch pour les tests (debate, chill)
    messages = [
        "Je pense que la stratégie utilisée par le streamer pourrait être améliorée.",
        "À mon avis, ce sujet mérite une discussion plus approfondie.",
        "Je ne suis pas d'accord avec cette approche, voici pourquoi...",
        "Peut-on explorer une autre perspective sur ce point ?",
        "C'est intéressant ce que tu dis, mais qu'en est-il de...",
        "Je me demande comment cela affectera le gameplay à long terme.",
        "Pourriez-vous clarifier ce dernier point ?",
        "Je comprends ton point de vue, cependant..."
    ]

    resultats = []

    for message in messages:
        resultat = traiter_phrase(message)
        resultats.append(resultat)

    return resultats

if __name__ == "__main__":
    resultats = main()
    for res in resultats:
        print(f"**Phrase :** {res['phrase']}\n")
        print("Groupes nominaux extraits :")
        for gn in res['groupes_nominaux']:
            print(f"- {gn}")
        print("\nVerbes extraits :")
        for vb in res['verbes']:
            print(f"- {vb}")
        print("\n" + "-"*80 + "\n")
