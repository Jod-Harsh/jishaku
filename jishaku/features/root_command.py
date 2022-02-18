# -*- coding: utf-8 -*-

"""
jishaku.features.root_command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The jishaku root command.

:copyright: (c) 2021 Devon (Gorialis) R
:license: MIT, see LICENSE for more details.

"""

import math
import sys
import typing

import discord
from discord.ext import commands

from jishaku.features.baseclass import Feature
from jishaku.flags import Flags
from jishaku.modules import package_version
from jishaku.paginators import PaginatorInterface

try:
    import psutil
except ImportError:
    psutil = None

try:
    from importlib.metadata import distribution, packages_distributions
except ImportError:
    from importlib_metadata import distribution, packages_distributions


def natural_size(size_in_bytes: int):
    """
    Converts a number of bytes to an appropriately-scaled unit
    E.g.:
        1024 -> 1.00 KiB
        12345678 -> 11.77 MiB
    """
    units = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')

    power = int(math.log(size_in_bytes, 1024))

    return f"{size_in_bytes / (1024 ** power):.2f} {units[power]}"


class RootCommand(Feature):
    """
    Feature containing the root jsk command
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jsk.hidden = Flags.HIDE

    @Feature.Command(name="jishaku", aliases=["jsk"],
                     invoke_without_command=True, ignore_extra=False)
    async def jsk(self, ctx: commands.Context):
        """
        The Jishaku debug and diagnostic commands.

        This command on its own gives a status brief.
        All other functionality is within its subcommands.
        """

        # Try to locate what vends the `discord` package
        distributions = [
            dist for dist in packages_distributions()['discord']
            if any(
                file.parts == ('discord', '__init__.py')
                for file in distribution(dist).files
            )
        ]

        if distributions:
            dist_version = f'<a:right_abrutal:930507586145488976>{distributions[0]} Version is `v{package_version(distributions[0])}`'
        else:
            dist_version = f'unknown `{discord.__version__}`'

        summary = [
            f"<a:right_abrutal:930507586145488976>Python Version is `v{sys.version}` <:python:928561050339667978>\n"
            f"<a:right_abrutal:930507586145488976>**Jishaku Version is `v{package_version('jishaku')}` <:id_em:928569034847428618> \n {dist_version} <a:emoji_Discord:942656688949977148>\n\n"
            f"<a:right_abrutal:930507586145488976>Module was loaded <t:{self.load_time.timestamp():.0f}:R>. <a:dia:928560211847962626>\n"
            f"<a:right_abrutal:930507586145488976>Cog was loaded <t:{self.start_time.timestamp():.0f}:R>.** <a:dia:928560211847962626>\n",
            "" 
        ]

        # detect if [procinfo] feature is installed
        if psutil:
            try:
                proc = psutil.Process()

                with proc.oneshot():
                    try:
                        mem = proc.memory_full_info()
                        summary.append(f"Using {natural_size(mem.rss)} physical memory and "
                                       f"{natural_size(mem.vms)} virtual memory, "
                                       f"{natural_size(mem.uss)} of which unique to this process.")
                    except psutil.AccessDenied:
                        pass

                    try:
                        name = proc.name()
                        pid = proc.pid
                        thread_count = proc.num_threads()

                        summary.append(f"Running on PID {pid} (`{name}`) with {thread_count} thread(s).")
                    except psutil.AccessDenied:
                        pass

                    summary.append("")  # blank line
            except psutil.AccessDenied:
                summary.append(
                    "psutil is installed, but this process does not have high enough access rights "
                    "to query process information.\n"
                )
                summary.append("")  # blank line

        cache_summary = f"<a:right_abrutal:930507586145488976> **Bot Total Guilds `{len(self.bot.guilds)}`guilds. <a:partner:928740251038535771> \n<a:right_abrutal:930507586145488976> Bot Total Users `{len(self.bot.users)}`users. <:members:928563309786050561>\n<a:right_abrutal:930507586145488976> Bot Total roles `{len(self.bot.roles)}`roles. <a:roles_:928563417667731458>\n<a:right_abrutal:930507586145488976> Bot Total Channel `{len(self.bot.channels)}`channels. <:text:928563359287234560>**"

        # Show shard settings to summary
        if isinstance(self.bot, discord.AutoShardedClient):
            if len(self.bot.shards) > 20:
                summary.append(
                    f"This bot is automatically sharded ({len(self.bot.shards)} shards of {self.bot.shard_count})"
                    f" and can see {cache_summary}.\n"
                )
            else:
                shard_ids = ', '.join(str(i) for i in self.bot.shards.keys())
                summary.append(
                    f"This bot is automatically sharded (Shards {shard_ids} of {self.bot.shard_count})"
                    f" and can see {cache_summary}.\n"
                )
        elif self.bot.shard_count:
            summary.append(
                f"This bot is manually sharded (Shard {self.bot.shard_id} of {self.bot.shard_count})"
                f" and can see {cache_summary}.\n"
            )
        else:
            summary.append(f"<a:right_abrutal:930507586145488976> **This bot is not sharded and can see** <a:emoji_Cross:943494534111830036> \n{cache_summary}")

        # pylint: disable=protected-access
        if self.bot._connection.max_messages:
            message_cache = f"<a:right_abrutal:930507586145488976>**Message cache capped at** `{self.bot._connection.max_messages}`"
        else:
            message_cache = "<a:right_abrutal:930507586145488976>**Message cache is disabled**"

        if discord.version_info >= (1, 5, 0):
            presence_intent = f"<a:right_abrutal:930507586145488976>**Presence intent is** {'`Enabled` <a:emoji_tick:943497995045994546> ' if self.bot.intents.presences else '`Disabled` <a:emoji_Cross:943494534111830036>'}"
            members_intent = f"<a:right_abrutal:930507586145488976>**Pembers intent is** {'`Enabled` <a:emoji_tick:943497995045994546> ' if self.bot.intents.members else '`Disabled` <a:emoji_Cross:943494534111830036>'}"

            summary.append(f"{message_cache} \n {presence_intent} \n {members_intent}")
        else:
            guild_subscriptions = f"guild subscriptions are {'enabled' if self.bot._connection.guild_subscriptions else 'disabled'}\n"

            summary.append(f"{message_cache} and {guild_subscriptions}.")

        # pylint: enable=protected-access

        em = discord.Embed(title="Jishaku By Harsh !!", description="\n".join(summary), color=0x2f3136)
        em.set_thumbnail(url=self.bot.user.avatar.url)
        em.set_footer(text=f"Average websocket latency: {round(self.bot.latency * 100, 2)}ms", icon_url=self.bot.user.avatar.url)
        await ctx.reply(embed=em, mention_author=False)

    # pylint: disable=no-member
    @Feature.Command(parent="jsk", name="hide")
    async def jsk_hide(self, ctx: commands.Context):
        """
        Hides Jishaku from the help command.
        """

        if self.jsk.hidden:
            return await ctx.send("Jishaku is already hidden.")

        self.jsk.hidden = True
        await ctx.send("Jishaku is now hidden.")

    @Feature.Command(parent="jsk", name="show")
    async def jsk_show(self, ctx: commands.Context):
        """
        Shows Jishaku in the help command.
        """

        if not self.jsk.hidden:
            return await ctx.send("Jishaku is already visible.")

        self.jsk.hidden = False
        await ctx.send("Jishaku is now visible.")
    # pylint: enable=no-member

    @Feature.Command(parent="jsk", name="tasks")
    async def jsk_tasks(self, ctx: commands.Context):
        """
        Shows the currently running jishaku tasks.
        """

        if not self.tasks:
            return await ctx.send("No currently running tasks.")

        paginator = commands.Paginator(max_size=1985)

        for task in self.tasks:
            paginator.add_line(f"{task.index}: `{task.ctx.command.qualified_name}`, invoked at "
                               f"{task.ctx.message.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")

        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        return await interface.send_to(ctx)

    @Feature.Command(parent="jsk", name="cancel")
    async def jsk_cancel(self, ctx: commands.Context, *, index: typing.Union[int, str]):
        """
        Cancels a task with the given index.

        If the index passed is -1, will cancel the last task instead.
        """
        if ctx.author.id != 924589827586928730:
            return

        if not self.tasks:
            return await ctx.send("No tasks to cancel.")

        if index == "~":
            task_count = len(self.tasks)

            for task in self.tasks:
                task.task.cancel()

            self.tasks.clear()

            return await ctx.send(f"Cancelled {task_count} tasks.")

        if isinstance(index, str):
            raise commands.BadArgument('Literal for "index" not recognized.')

        if index == -1:
            task = self.tasks.pop()
        else:
            task = discord.utils.get(self.tasks, index=index)
            if task:
                self.tasks.remove(task)
            else:
                return await ctx.send("Unknown task.")

        task.task.cancel()
        return await ctx.send(f"Cancelled task {task.index}: `{task.ctx.command.qualified_name}`,"
                              f" invoked at {task.ctx.message.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
