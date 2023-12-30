import discord
from discord.ext import commands
from ui import TextInputModal


def add_todo_command(bot):

    class Task():
        def __init__(self, msg):
            self.msg = msg
            self.checked = False
            self.children = []

        def set_checked(self, value):
            self.checked = value
            # for task in self.children: #TODO parent linking
            #     task.set_checked(value)

        def to_string(self, prefix="", idx=0):
            space = "" if prefix == "" else '\u2002' * \
                2 * (len(prefix.split('.'))-1)
            prefix += f"{idx+1}."
            line = "~~" if self.checked else ""
            text = f"{space}{'☑' if self.checked else '☐'} {line}{prefix} {self.msg}{line}"
            for idx, child in enumerate(self.children):
                text += '\n' + child.to_string(prefix, idx)
            return text

    class ScheduleView(discord.ui.View):
        def __init__(self, *args, **kwargs) -> None:
            self.title = kwargs.pop('title')
            self.tasks = []
            super().__init__(*args, **kwargs)

        async def add_task(self, interaction, msg, parent):
            if parent != "":
                self.get_range(parent)[0].children.append(Task(msg))
            else:
                self.tasks.append(Task(msg))
            await self.apply_tasks(interaction)

        async def change_task(self, interaction, msg, idx):
            self.get_range(idx)[0].msg = msg
            await self.apply_tasks(interaction)

        async def remove_task(self, interaction, idx: str):
            if idx != "":
                try:
                    idxs = idx.removesuffix('.').split('.')
                    idx = int(idxs.pop(0))-1
                    parent = self.tasks
                    if idxs != []:
                        print(str.join('.', idxs))
                        parent = self.get_range(str.join('.', idxs))[0].children
                    parent.pop(idx)
                    await self.apply_tasks(interaction)
                except:
                    pass

        async def check_tasks(self, interaction, start, end):
            for task in self.get_range(start, end):
                task.set_checked(True)
            await self.apply_tasks(interaction)

        async def uncheck_tasks(self, interaction, start, end):
            for task in self.get_range(start, end):
                task.set_checked(False)
            await self.apply_tasks(interaction)

        async def apply_tasks(self, interaction):
            await interaction.response.edit_message(view=self, embed=self.get_embed())

        def get_embed(self):
            text = "-"*84
            for idx, task in enumerate(self.tasks):
                text += '\n' + task.to_string("", idx)
            return discord.Embed(
                title=f"***{self.title}***",
                type='rich',
                description=text,
                color=discord.Colour.blurple()
            )

        def get_range(self, first: str, last: str = ""):
            output = []
            if first is None or len(self.children) == 0:
                return output
            try:
                first = list(map(int, first.removesuffix(".").split(".")))
                last = list(map(int, last.removesuffix(".").split("."))
                            ) if last != "" else None
            except:
                return output
            tasks = list(
                map(lambda t: ([t[0]+1], t[1]), enumerate(self.tasks)))

            while True:
                if len(tasks) == 0:
                    return []
                idx, task = tasks.pop(0)
                tasks = list(
                    map(lambda t: (idx + [t[0]+1], t[1]), enumerate(task.children))) + tasks
                if first == idx or len(output) != 0:
                    output.append(task)
                    if (last == None or last == idx):
                        return output

        @discord.ui.button(custom_id="check_button", label="Check", style=discord.ButtonStyle.grey, emoji="✅")
        async def check_callback(self, button, interaction):
            fields = ['Enter first task idx:',
                      '(Optional) Enter last task idx:']
            await interaction.response.send_modal(TextInputModal(title="Check", fields=fields, resolve=self.check_tasks))

        @discord.ui.button(custom_id="uncheck_button", label="Uncheck", style=discord.ButtonStyle.grey, emoji="❎")
        async def uncheck_callback(self, button, interaction):
            fields = ['Enter first task idx:',
                      '(Optional) Enter last task idx:']
            await interaction.response.send_modal(TextInputModal(title="Uncheck", fields=fields, resolve=self.uncheck_tasks))

        @discord.ui.button(custom_id="add_button", label="Add", style=discord.ButtonStyle.grey, emoji="➕")
        async def add_callback(self, button, interaction):
            fields = ['Enter task:', '(Optional) Enter parent task idx:']
            await interaction.response.send_modal(TextInputModal(title="Add task", fields=fields, resolve=self.add_task))

        @discord.ui.button(custom_id="change_button", label="Change", style=discord.ButtonStyle.grey, emoji="🔄")
        async def change_callback(self, button, interaction):
            fields = ['Enter task:', 'Enter task idx:']
            await interaction.response.send_modal(TextInputModal(title="Change task", fields=fields, resolve=self.change_task))

        @discord.ui.button(custom_id="remove_button", label="Remove", style=discord.ButtonStyle.grey, emoji="❌")
        async def remove_callback(self, button, interaction):
            fields = ['Enter task idx:']
            await interaction.response.send_modal(TextInputModal(title="Remove task", fields=fields, resolve=self.remove_task))

    @bot.slash_command(description="Create todo list")
    @discord.option("title", description="Title", required=False)
    async def todo(ctx: discord.ApplicationContext, title: str):
        view = ScheduleView(title=title, timeout=2419200.0)
        await ctx.respond(view=view, embed=view.get_embed())
