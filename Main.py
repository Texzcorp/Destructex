from flask import Flask, request, jsonify
from twitchio.ext import commands
from AnswerMaker import parse_message, generate_answer
import threading
import random

app = Flask(__name__)

# Classe Bot utilisant TwitchIO
class Bot(commands.Bot):
    def __init__(self, channel, token):
        super().__init__(token=token, prefix='!', initial_channels=[channel])
        self.channel = channel

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        try:
            if message.author and message.author.name.lower() == self.nick.lower():
                return

            detected_author = message.author.name if message.author else "Unknown"
            print(f"> Message détecté de {detected_author}: {message.content}")

            if random.random() < 0.6:
                print("J'attaque!")
                name, verb, mood, tense, person, original_verb_form, other_elements = parse_message(message.content)
                print("> Message décortiqué !")
                print(f"Name: {name}, Verb: {verb}, Mood: {mood}, Tense: {tense}, Person: {person}, Original Verb Form: {original_verb_form}, Other Elements: {other_elements}")

                if name or verb or other_elements:
                    response = generate_answer(name, verb, mood, tense, person, original_verb_form, message.author.name)
                    if response:
                        print(f"> Réponse générée : {response}")
                        await message.channel.send(response)
                    else:
                        print("> Aucune réponse générée.")
                else:
                    print("> Aucun élément significatif détecté.")
        except Exception as e:
            print(f"Erreur dans event_message : {e}")
            import traceback
            traceback.print_exc()

# Fonction pour démarrer le bot
def run_bot(channel, token):
    bot = Bot(channel, token)
    bot.run()

@app.route('/start-bot', methods=['POST'])
def start_bot():
    data = request.get_json()
    channel = data.get('channel')
    token = data.get('token')

    if not channel or not token:
        return jsonify({"message": "Channel ou token manquant."}), 400

    threading.Thread(target=run_bot, args=(channel, token)).start()
    return jsonify({"message": f"Bot démarré pour le channel {channel}."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)