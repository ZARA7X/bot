import datetime as dt
import random

from async_rediscache import RedisCache
from discord import Message
from discord.ext.commands import Cog

from bot.bot import Bot
from bot.constants import Channels, Roles
from bot.log import get_logger

OT_CHANNEL_IDS = (Channels.off_topic_0, Channels.off_topic_1, Channels.off_topic_2)
NEW_HELPER_ROLE_ID = Roles.new_helpers

log = get_logger(__name__)


class NewHelperUtils(Cog):
    """Manages functionality for new helpers in April 2023."""

    # RedisCache[discord.Channel.id, UtcPosixTimestamp]
    cooldown_cache = RedisCache()

    COOLDOWN_DURATION = dt.timedelta(minutes=10)
    MESSAGES = [
        f"<@&{NEW_HELPER_ROLE_ID}> can someone please answer this??",
        f"Someone answer this <@&{NEW_HELPER_ROLE_ID}> if you want to keep your role",
        f"Where are my <@&{NEW_HELPER_ROLE_ID}> at?",
        f"<@&{NEW_HELPER_ROLE_ID}>, answer this!",
        f"What's the point of having all these new <@&{NEW_HELPER_ROLE_ID}> if questions are going unanswered?",
    ]

    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def _is_question(message: str) -> bool:
        """Return True if `message` appears to be a question, else False!"""
        return (
            ('?' in message)
            and any(map(
                message.lower().startswith,
                (
                    'is', 'are', 'am',
                    'was', 'were',
                    'will',
                    'can', 'does', 'do', 'did'
                    'who', 'what', 'when', 'where', 'why'
                )
            ))
        )

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """
        This is an event listener.

        Ping helpers in off-topic channels whenever someone asks a question, at most
        as often `COOLDOWN_DURATION`.
        """
        if message.author.bot or message.channel.id not in OT_CHANNEL_IDS:
            return

        last_activation_time = dt.datetime.fromtimestamp(
            await self.cooldown_cache.get(message.channel.id, 0)
        )

        if dt.datetime.now() - last_activation_time < self.COOLDOWN_DURATION:
            return

        if self._is_question(message.content):
            await message.reply(random.choice(self.MESSAGES))
            await self.cooldown_cache.set(message.channel.id, dt.datetime.now().timestamp())


async def setup(bot: Bot) -> None:
    """Load the OffTopicNames cog."""
    await bot.add_cog(NewHelperUtils(bot))
