# generation.py

import random

def load_templates(file_path):
    """
    Charge les templates de réponse à partir d'un fichier texte.

    Les templates contenant {nom} sont ajoutés à TEMPLATES_NOM,
    et ceux contenant {verb} sont ajoutés à TEMPLATES_VERB.

    Parameters:
        file_path (str): Chemin vers le fichier de templates.

    Returns:
        tuple: (TEMPLATES_NOM, TEMPLATES_VERB)
    """
    TEMPLATES_NOM = []
    TEMPLATES_VERB = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):  # Ignorer les lignes vides et les commentaires
                    continue
                if '{nom}' in line and '{verb}' in line:
                    # Ignorer les templates contenant les deux placeholders
                    print(f"Avertissement : Le template contient à la fois {{nom}} et {{verb}} et sera ignoré.\nTemplate : {line}")
                    continue
                elif '{nom}' in line:
                    TEMPLATES_NOM.append(line)
                elif '{verb}' in line:
                    TEMPLATES_VERB.append(line)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {file_path} n'a pas été trouvé.")
    
    return TEMPLATES_NOM, TEMPLATES_VERB

def generer_reponses(groupes_nominaux, verbes, user, templates_file='phrases.txt'):
    """
    Génère des réponses basées sur les groupes nominaux et les verbes extraits en utilisant des templates.

    Parameters:
        groupes_nominaux (list): Liste des groupes nominaux extraits.
        verbes (list): Liste des verbes extraits.
        templates_file (str): Chemin vers le fichier de templates.

    Returns:
        list: Liste des réponses générées.
    """
    TEMPLATES_NOM, TEMPLATES_VERB = load_templates(templates_file)
    
    if not TEMPLATES_NOM and groupes_nominaux:
        print("Avertissement : Aucun template pour les groupes nominaux n'a été trouvé.")
    if not TEMPLATES_VERB and verbes:
        print("Avertissement : Aucun template pour les verbes n'a été trouvé.")
    
    reponses = []
    
    # Générer des réponses pour les groupes nominaux
    for gn in groupes_nominaux:
        if TEMPLATES_NOM:
            template = random.choice(TEMPLATES_NOM)
            # Utiliser 'nom' au lieu de 'phrase'
            reponse = template.format(nom=gn, user=user)
            reponses.append(reponse)

    # Générer des réponses pour les verbes
    for vb in verbes:
        if TEMPLATES_VERB:
            template = random.choice(TEMPLATES_VERB)
            reponse = template.format(verb=vb, user=user)
            reponses.append(reponse)
    
    return reponses
