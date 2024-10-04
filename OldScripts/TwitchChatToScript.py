from twitchio.ext import commands

class ChatBot(commands.Bot):

    def __init__(self, channel, oauth_token):
        # Initialisation du bot avec le token et le canal
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel])
        self.message_data = []

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Ne pas répondre à ses propres messages
        if message.author.name.lower() == self.nick.lower():
            return

        print(f"Message détecté de {message.author.name}: {message.content}")
        self.message_data.append((message.author.name, message.content))

    def get_chat_messages(self):
        return self.message_data
