import discord
from datetime import datetime
from discord.ui import InputText, Modal


class ConfirmationModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        self.confirmation = kwargs.pop('confirmation')
        self.resolve = kwargs.pop('resolve')
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label=f"Enter \"{self.confirmation}\""))

    async def callback(self, interaction):
        if (self.children[0].value == self.confirmation):
            if self.resolve is not None:
                await self.resolve(interaction)
        else:
            await interaction.response.defer()


class DateModal(Modal):
    # TODO TIMEZONES??????!!!!!!!!!!!!!!!!!
    def __init__(self, *args, **kwargs) -> None:
        self.resolve = kwargs.pop('resolve')
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Date \"%d.%m.%Y\"",
                      value=datetime.now().strftime("%d.%m.%Y")))
        self.add_item(InputText(label="Time \"%H.%M\"",
                      value=datetime.now().strftime("%H.%M")))

    async def callback(self, interaction):
        try:
            date = f"{self.children[0].value} {self.children[1].value}"
            stamp = datetime.strptime(date, "%d.%m.%Y %H.%M")
            date = f"({stamp.strftime('%a')}) {date}"
            await self.resolve(interaction, date)
        except:
            await interaction.response.defer()


class TextInputModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        self.resolve = kwargs.pop('resolve')
        fields = kwargs.pop('fields')
        super().__init__(*args, **kwargs)
        for field in fields:
            self.add_item(InputText(label=field, required=False))

    async def callback(self, interaction):
        if self.resolve is not None:
            values = []
            for child in self.children:
                values.append(child.value)
            await self.resolve(interaction, *values)
        else:
            await interaction.response.defer()
