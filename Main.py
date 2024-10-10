import webbrowser
import urllib.parse
import random
import string
import time
import requests
from twitchio.ext import commands
from ParseNewMethod import traiter_phrase
from NewGenerateAnswer import generer_reponses

# Fonction pour charger les informations de configuration depuis un fichier
def load_config():
    config = {}
    with open('config.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

# Fonction pour sauvegarder le token OAuth dans le fichier config.txt (remplace l'ancien)
def save_oauth_token(token):
    lines = []
    with open('config.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # On cherche à remplacer la ligne contenant le token OAuth s'il existe déjà
    with open('config.txt', 'w', encoding='utf-8') as f:
        token_updated = False
        for line in lines:
            if line.startswith('oauth_token='):
                f.write(f"\noauth_token={token}\n")
                token_updated = True
            else:
                f.write(line)
        
        # Si aucune ligne de token n'a été trouvée, on l'ajoute à la fin
        if not token_updated:
            f.write(f"\noauth_token={token}\n")

# Générer un état aléatoire pour éviter les attaques CSRF
def generate_state(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Créer l'URL d'autorisation
def create_authorization_url(client_id, redirect_uri, scope, state):
    base_url = "https://id.twitch.tv/oauth2/authorize"
    params = {
        "response_type": "token",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

# Fonction pour extraire le token de l'URL de redirection
def extract_token_from_url():
    redirect_url = input("Copie-colle ici l'URL de redirection complète après l'autorisation : ")
    fragment = urllib.parse.urlparse(redirect_url).fragment
    params = dict(x.split('=') for x in fragment.split('&'))
    access_token = params.get('access_token', None)
    return access_token

# Vérifier si le token OAuth est valide
def is_token_valid(token):
    validation_url = "https://id.twitch.tv/oauth2/validate"
    headers = {"Authorization": f"OAuth {token}"}
    response = requests.get(validation_url, headers=headers)
    return response.status_code == 200

# Fonction pour charger les modes depuis le fichier modes.txt
def load_modes_from_file():
    modes = []
    try:
        with open('modes.txt', 'r', encoding='utf-8') as f:
            current_mode = None
            mode_data = {}
            for line in f:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    if current_mode:
                        modes.append(mode_data)
                    current_mode = line[1:-1]
                    mode_data = {"mode": current_mode, "conjugaisons": {}, "filepath": "", "prefix": ""}
                elif '=' in line and current_mode:
                    key, value = line.split('=')
                    key = key.strip()
                    value = value.strip()
                    if key == "filepath":
                        mode_data["filepath"] = value
                    elif key == "prefix":
                        mode_data["prefix"] = value
                    else:
                        mode_data["conjugaisons"][key] = value
            if current_mode:
                modes.append(mode_data)
    except FileNotFoundError:
        print("Erreur : Le fichier modes.txt n'a pas été trouvé.")
    return modes

# Classe Bot utilisant TwitchIO
class Bot(commands.Bot):
    def __init__(self, channel, oauth_token):
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel])
        self.channel = channel

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        self.bot_id = self.user_id  # Stocke l'ID du bot pour éviter les réponses à lui-même

    async def event_message(self, message):
        try:
            # Ignore le message si l'auteur est le bot lui-même (nom "texzzzzzz")
            if message.author and message.author.name.lower() == "texzzzzzz":
                return

            detected_author = message.author.name if message.author else "Unknown"
            print(f"> Message détecté de {detected_author}: {message.content}")
            if detected_author == "Unknown":
                return

            # Chance de réponse (ajustez la probabilité pour les tests)
            if random.random() < 0.1:
                print("J'attaque!")
                parsed_message = traiter_phrase(message.content)
                print(f"> Message décortiqué : {parsed_message}")

                # Charger les modes et en sélectionner un au hasard
                modes = load_modes_from_file()
                if modes:
                    chosen_mode_data = random.choice(modes)
                    chosen_mode = chosen_mode_data["mode"]
                    chosen_prefix = chosen_mode_data["prefix"]
                    print(f"Mode choisi : {chosen_mode}")
                    print(f"Préfixe choisi : {chosen_prefix}")

                    # Générer les réponses en utilisant le mode choisi
                    if parsed_message["groupes_nominaux"] or parsed_message["verbes"]:
                        groupes_nominaux = parsed_message["groupes_nominaux"]
                        verbes = parsed_message["verbes"]
                        responses = generer_reponses(groupes_nominaux, verbes, detected_author, chosen_mode)
                        
                        # Choisir une réponse aléatoire et ajouter le préfixe du mode
                        if responses:
                            chosen_response = random.choice(responses)
                            prefixed_response = f"{chosen_prefix} {chosen_response}"
                            print(f"> Réponse finale : {prefixed_response}")  # Log
                            await message.channel.send(prefixed_response)
                        else:
                            print("> Aucune réponse générée, éléments manquants ou réponse invalide.")
                    else:
                        print("> Aucun élément significatif détecté, pas de réponse.")
                else:
                    print("> Aucun mode disponible pour générer des réponses.")

        except Exception as e:
            print(f"Une erreur est survenue dans event_message : {e}")
            import traceback
            traceback.print_exc()

    async def send_message(self, channel_name, response):
        # Envoie la réponse dans le chat
        channel = self.get_channel(channel_name)
        if channel:
            await channel.send(response)
        else:
            print(f"Channel {channel_name} not found.")

def main():
    # Charger les informations de configuration
    config = load_config()
    client_id = config['client_id']
    redirect_uri = config['redirect_uri']
    scope = config['scope']

    oauth_token = config.get('oauth_token', None)

    if oauth_token and is_token_valid(oauth_token):
        print("Token OAuth valide.")
    else:
        print("Token OAuth invalide ou inexistant. Génération d'un nouveau token.")
        state = generate_state()
        auth_url = create_authorization_url(client_id, redirect_uri, scope, state)
        webbrowser.open(auth_url)
        print("Une fois l'autorisation accordée, copiez l'URL complète de redirection et collez-la ici.")
        oauth_token = extract_token_from_url()

        if oauth_token:
            print("Nouveau token OAuth récupéré.")
            save_oauth_token(oauth_token)
        else:
            print("Impossible de récupérer le token OAuth.")
            return

    channel = 'texzzzzzz'
    bot = Bot(channel, oauth_token)
    bot.run()

if __name__ == '__main__':
    main()
