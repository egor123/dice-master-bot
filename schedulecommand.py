import discord
from discord.ext import commands
from utils import ConfirmationModal, DateModal, is_campaign_category, get_category_roles


def add_schedule_command(bot):
    empty_option = discord.SelectOption(label="Empty",
                                        description="Press \"📅Add date\"")
    # TODO Timizones!!!!!!!!!!

    class ScheduleView(discord.ui.View):
        def __init__(self, *args, **kwargs) -> None:
            self.name = kwargs.pop('name')
            self.thread = kwargs.pop('thread')
            self.role = kwargs.pop('role')
            self.required_votes = kwargs.pop('required_votes')
            self.options = []
            super().__init__(*args, **kwargs)

        async def add_date(self, interaction, date):
            await self.thread.send(f"{self.role.mention} new date \"{date}\" by {interaction.user.mention}")
            self.options.append({'date': date, 'votes': []})
            await self.apply_changes(interaction)

        async def remove_date(self, interaction, date):
            for o in self.options:
                if o['date'] == date:
                    await self.thread.send(f"{self.role.mention} date removed \"{date}\" by {interaction.user.mention}")
                    self.options.remove(o)
                    await self.apply_changes(interaction)
                    return
            await interaction.response.defer()

        async def vote(self, interaction, votes):
            for o in self.options:
                user = interaction.user.name
                date = o['date']
                if date in votes:
                    if user in o['votes']:
                        o['votes'].remove(user)
                        await self.thread.send(f"{interaction.user.mention} \"{date}\" 👎")
                    else:
                        o['votes'].append(user)
                        await self.thread.send(f"{interaction.user.mention} \"{date}\" 👍")
                        if (len(o['votes']) >= self.required_votes):
                            await self.apply_final_date(interaction, o['date'])
                            return
            await self.apply_changes(interaction)

        async def apply_changes(self, interaction):
            select = self.get_item('select')
            if len(self.options) > 0:
                self.options = list(sorted(self.options,
                                           key=lambda o: len(o['votes']),
                                           reverse=True))
                select.options = list(map(lambda o: discord.SelectOption(
                    label=o['date'],
                    description=f"[{len(o['votes'])}/{self.required_votes}] {', '.join(o['votes'])}"
                ), self.options))
            else:
                select.options = [empty_option]
            select.max_values = max(1, len(select.options))
            await interaction.response.edit_message(view=self)

        async def apply_final_date(self, interaction, date):
            self.get_item("remove_button").disabled = True
            self.get_item("add_button").disabled = True
            self.get_item('select').disabled = True
            self.message.embeds[0].add_field(name="Time", value=date)
            await self.thread.send(f"{self.role.mention} ✨✨✨\"{date}\"✨✨✨")
            await interaction.response.edit_message(view=self, embeds=self.message.embeds)

        async def delete(self, interaction):
            await interaction.response.edit_message(content=f"{interaction.user.mention} canceled event \"{self.name}\"", view=None, embed=None)
            await self.thread.delete()

        @discord.ui.button(custom_id="cancel_button", label="Cancel event", style=discord.ButtonStyle.danger, emoji="💩")
        async def cancel_callback(self, button, interaction):
            await interaction.response.send_modal(ConfirmationModal(title="⚠️Are you sure?⚠️",
                                                                    confirmation="DELETE",
                                                                    resolve=self.delete))

        @discord.ui.button(custom_id="remove_button", label="Remove date", style=discord.ButtonStyle.secondary, emoji="❌")
        async def remove_date_callback(self, button, interaction):
            await interaction.response.send_modal(DateModal(title="Remove date", resolve=self.remove_date))

        @discord.ui.button(custom_id="add_button", label="Add date", style=discord.ButtonStyle.primary, emoji="📅")
        async def add_date_callback(self, button, interaction):
            await interaction.response.send_modal(DateModal(title="Add date", resolve=self.add_date))

        @discord.ui.select(custom_id="select", min_values=0, placeholder="Choose Date!!!", options=[empty_option])
        async def select_callback(self, select, interaction):
            await self.vote(interaction, select.values)

    @bot.slash_command(description="Start scheduling new event")
    @commands.check(is_campaign_category)
    @discord.option("event", description="Enter event's name")
    @discord.option("required_votes", description="Amount of votes required to schedule event", min_value=0, default=0)
    @discord.option("description", description="Description of the event", min_length=10, required=False)
    async def schedule(ctx: discord.ApplicationContext, event: str, required_votes: int, description: str):
        (pc_role,) = get_category_roles(ctx, roles=["PC"])
        if required_votes == 0:
            required_votes = len(pc_role.members)
        embed = discord.Embed(
            title=f"***{event}***",
            type='rich',
            description=f"`🎲🎲🎲{'new event'.center(42)}🎲🎲🎲`",
            color=discord.Colour.blurple()
        )
        await ctx.respond(f"{pc_role.mention}", embed=embed)
        message = ctx.channel.last_message  # FIXME????
        thread = await message.create_thread(name=event)
        await thread.send(pc_role.mention)
        view = ScheduleView(name=event,
                            required_votes=required_votes,
                            thread=thread,
                            role=pc_role,
                            timeout=2419200.0)
        view.message = message
        await message.edit(view=view)
