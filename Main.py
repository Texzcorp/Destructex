import webbrowser
import urllib.parse
import random
import string
import time
from twitchio.ext import commands
from AnswerMaker import parse_message, generate_answer

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

# Fonction pour extraire le token de l'URL de redirection (simulation d'extraction depuis une page web)
def extract_token_from_url():
    # Ici on simule la récupération du token depuis le fragment de l'URL après authentification
    redirect_url = input("Copie-colle ici l'URL de redirection complète après l'autorisation : ")
    fragment = urllib.parse.urlparse(redirect_url).fragment
    params = dict(x.split('=') for x in fragment.split('&'))
    access_token = params.get('access_token', None)
    return access_token

# Classe Bot utilisant TwitchIO
class Bot(commands.Bot):
    def __init__(self, channel, oauth_token):
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel])
        self.channel = channel

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        try:
            # Ne pas répondre aux messages du bot lui-même
            if message.author and message.author.name.lower() == self.nick.lower():
                return

            detected_author = message.author.name if message.author else "Unknown"
            print(f"> Message détecté de {detected_author}: {message.content}")

            # 100% de chance de répondre pour les tests (remplacez par 0.6 pour une réponse aléatoire)
            if random.random() < 0.6:
                print("J'attaque!")
                name, verb, mood, tense, person, original_verb_form, other_elements = parse_message(message.content)
                print("> Message décortiqué !")
                print(f"Name: {name}, Verb: {verb}, Mood: {mood}, Tense: {tense}, Person: {person}, Original Verb Form: {original_verb_form}, Other Elements: {other_elements}")  # Log

                # Si un nom, verbe ou autre élément significatif est détecté, générer une réponse
                if name or verb or other_elements:
                    response = generate_answer(name, verb, mood, tense, person, original_verb_form, message.author.name)
                    if response:
                        print(f"> Réponse générée : {response}")  # Log
                        await message.channel.send(response)
                    else:
                        print("> Aucune réponse générée, éléments manquants ou réponse invalide.")
                else:
                    print("> Aucun élément significatif détecté, pas de réponse.")

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
    
    # Générer un état unique
    state = generate_state()

    # Créer l'URL d'autorisation
    auth_url = create_authorization_url(client_id, redirect_uri, scope, state)
    
    # Ouvrir l'URL dans un navigateur
    webbrowser.open(auth_url)
    
    print("Une fois l'autorisation accordée, copiez l'URL complète de redirection et collez-la ici.")

    # Extraire le token de l'URL de redirection fournie par l'utilisateur
    oauth_token = extract_token_from_url()

    if oauth_token:
        print(f"Access Token récupéré")
        
        # Spécifier le channel ici
        channel = 'loinduciel'
        
        # Lancer le bot
        bot = Bot(channel, oauth_token)
        bot.run()
    else:
        print("Impossible de récupérer le token. Vérifiez l'URL fournie.")

if __name__ == '__main__':
    main()
