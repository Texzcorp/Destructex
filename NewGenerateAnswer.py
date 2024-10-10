import random

def load_templates(filepath):
    """
    Charge les templates de réponse à partir d'un fichier texte.

    Les templates contenant {nom} sont ajoutés à TEMPLATES_NOM,
    et ceux contenant {verb} sont ajoutés à TEMPLATES_VERB.

    Parameters:
        filepath (str): Chemin vers le fichier de templates défini dans le mode.

    Returns:
        tuple: (TEMPLATES_NOM, TEMPLATES_VERB)
    """
    TEMPLATES_NOM = []
    TEMPLATES_VERB = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):  # Ignorer les lignes vides et les commentaires
                    continue
                if '{nom}' in line and '{verb}' in line:
                    print(f"Avertissement : Le template contient à la fois {{nom}} et {{verb}} et sera ignoré.\nTemplate : {line}")
                    continue
                elif '{nom}' in line:
                    TEMPLATES_NOM.append(line)
                elif '{verb}' in line:
                    TEMPLATES_VERB.append(line)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {filepath} n'a pas été trouvé.")
    
    return TEMPLATES_NOM, TEMPLATES_VERB

def load_modes(modes_file):
    """
    Charge les modes de conjugaison à partir d'un fichier texte.

    Parameters:
        modes_file (str): Chemin vers le fichier des modes de conjugaison.

    Returns:
        dict: Dictionnaire des modes avec les conjugaisons associées et le chemin des templates.
    """
    modes = {}
    current_mode = None

    try:
        with open(modes_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('[') and line.endswith(']'):
                    # Nouveau mode détecté
                    current_mode = line[1:-1]  # Enlever les crochets []
                    modes[current_mode] = {"conjugaisons": {}, "filepath": ""}
                elif '=' in line and current_mode:
                    # Ajouter les conjugaisons ou le filepath au mode actuel
                    key, value = line.split('=')
                    key = key.strip()
                    value = value.strip()
                    if key == "filepath":
                        modes[current_mode]["filepath"] = value
                    else:
                        modes[current_mode]["conjugaisons"][key] = value
    except FileNotFoundError:
        print(f"Erreur : Le fichier {modes_file} n'a pas été trouvé.")
    
    return modes

def conjuguer_verbe_chaotique(verbe, pronom, conjugaisons):
    """
    Conjugue un verbe de manière chaotique en remplaçant les terminaisons des trois groupes.

    Parameters:
        verbe (str): Le verbe à conjuguer.
        pronom (str): Le pronom sujet.
        conjugaisons (dict): Dictionnaire des conjugaisons pour le mode choisi.

    Returns:
        str: Verbe conjugué de manière chaotique.
    """
    terminaison = conjugaisons.get(pronom.lower(), '')
    
    # On extrait la terminaison, peu importe le groupe du verbe
    if verbe.endswith('er'):
        racine = verbe[:-2]  # Enlever 'er' pour les verbes du premier groupe
    elif verbe.endswith('ir'):
        racine = verbe[:-2]  # Enlever 'ir' pour les verbes du deuxième groupe
    elif verbe.endswith('re'):
        racine = verbe[:-2]  # Enlever 're' pour les verbes du troisième groupe
    else:
        racine = verbe  # Si ce n'est aucun de ces cas, on prend tout

    return racine + terminaison

def generer_reponses(groupes_nominaux, verbes, user, mode, modes_file='modes.txt'):
    """
    Génère des réponses basées sur les groupes nominaux et les verbes extraits en utilisant des templates.
    Conjugue les verbes de manière chaotique en fonction du mode défini dans un fichier de modes.

    Parameters:
        groupes_nominaux (list): Liste des groupes nominaux extraits.
        verbes (list): Liste des verbes extraits.
        mode (str): Mode de conjugaison à utiliser.
        modes_file (str): Chemin vers le fichier des modes de conjugaison.

    Returns:
        list: Liste des réponses générées.
    """
    modes = load_modes(modes_file)
    
    if mode not in modes:
        print(f"Erreur : Le mode {mode} n'a pas été trouvé dans le fichier des modes.")
        return []

    conjugaisons = modes[mode]["conjugaisons"]
    filepath = modes[mode]["filepath"]
    
    if not filepath:
        print(f"Erreur : Aucun fichier de templates défini pour le mode {mode}.")
        return []

    TEMPLATES_NOM, TEMPLATES_VERB = load_templates(filepath)
    
    reponses = []
    
    # Générer des réponses pour les groupes nominaux
    for gn in groupes_nominaux:
        if TEMPLATES_NOM:
            template = random.choice(TEMPLATES_NOM)
            reponse = template.format(nom=gn, user=user)
            reponses.append(reponse)

    # Générer des réponses pour les verbes
    for vb in verbes:
        if TEMPLATES_VERB:
            template = random.choice(TEMPLATES_VERB)
            # Détection du pronom dans le template pour la conjugaison
            if 'je' in template:
                pronom = 'je'
            elif 'tu' in template:
                pronom = 'tu'
            elif 'il' in template or 'elle' in template:
                pronom = 'il'  # Utiliser 'il' par défaut pour la 3e personne
            elif 'nous' in template:
                pronom = 'nous'
            elif 'vous' in template:
                pronom = 'vous'
            elif 'ils' in template or 'elles' in template:
                pronom = 'ils'
            else:
                pronom = 'il'  # Par défaut si aucun pronom n'est trouvé

            # Conjuguer le verbe de manière chaotique
            verbe_conjugue = conjuguer_verbe_chaotique(vb, pronom, conjugaisons)
            
            # Remplacer le verbe dans le template
            reponse = template.format(verb=verbe_conjugue, user=user)
            reponses.append(reponse)
    
    return reponses
