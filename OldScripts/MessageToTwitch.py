from twitchio.ext import commands

class Bot(commands.Bot):

    def __init__(self, channel, oauth_token):
        # Initialisation du bot avec le token et le canal
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def send_message(self, channel, message):
        # Envoie un message dans le canal spécifié
        ch = self.get_channel(channel)
        if ch:
            await ch.send(message)
        else:
            print(f"Le canal {channel} n'est pas trouvé.")

