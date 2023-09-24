import discord
from datetime import datetime

class ConfirmationModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        self.confirmation = kwargs.pop('confirmation')
        self.resolve = kwargs.pop('resolve')
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(
            label=f"Enter \"{self.confirmation}\""))

    async def callback(self, interaction):
        if (self.children[0].value == self.confirmation):
            if self.resolve is not None:
                await self.resolve(interaction)
        else:
            await interaction.response.defer()


class DateModal(discord.ui.Modal):
    # TODO TIMEZONES??????!!!!!!!!!!!!!!!!!
    def __init__(self, *args, **kwargs) -> None:
        self.resolve = kwargs.pop('resolve')
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Date \"%d.%m.%Y\"",
                      value=datetime.now().strftime("%d.%m.%Y")))
        self.add_item(discord.ui.InputText(label="Time \"%H.%M\"",
                      value=datetime.now().strftime("%H.%M")))

    async def callback(self, interaction):
        try:
            date = f"{self.children[0].value} {self.children[1].value}"
            stamp = datetime.strptime(date, "%d.%m.%Y %H.%M")
            date = f"({stamp.strftime('%a')}) {date}"
            await self.resolve(interaction, date)
        except:
            await interaction.response.defer()