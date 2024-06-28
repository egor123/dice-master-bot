# Discord TTRPG Server Management Bot

This is a Python bot designed to manage a Discord server for tabletop role-playing games (TTRPGs). It offers a variety of commands to facilitate server organization.

## Commands

The bot provides several commands that are restricted to specific user roles and categories:

### Configuration Commands (Only for 〔⚙〕config category)

#### @Admin, @Moderator, @TrueRoller

- **/create_new_category `<name>`**
  - Creates a new category with the specified name.

#### @Admin, @Moderator, @TrueRoller who is category DM

- **/rename_category `<category>` `<name>`**
  - Renames the specified category to the new name.

- **/delete_category `<name>`**
  - Deletes the specified category.

### Private Category Commands

#### @<category>-DM

- **/manage_roles `<user>` `<action>` `<role>`**
  - Manages roles within the category, adding or removing roles for specified users.
  - **Example:** `/manage_roles @Player1 add_role PC`

#### @<category>-PC, @<category>-DM

- **/schedule `<event>` `[required_votes]` `[description]`**
  - Schedules an event within the category, optionally requiring a specified number of votes.
  - **Example:** `/schedule "Game Night" 3 "Join us for a fun game night!"`

- **/leave**
  - Allows the player to leave the category.

### General Commands (For any category)

#### @everyone

- **/roll `<dice>`**
  - Rolls the specified dice.
  - **Example:** `/roll 1d20`

- **/todo `<title>`**
  - Adds a to-do item with the specified title, allows to add new points and mark them as completed
  - **Example:** `/todo "Finish objectives"`


## Installation

### Prerequisites

Make sure you have the following installed:

- [Python 3.8+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)

### Setting Up

1. Clone the repository:

    ```bash
    https://github.com/egor123/dice-master-bot.git
    cd dice-master-bot
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your Discord bot token and other configuration details. Create a `.env` file in the root directory and add your Discord token:

    ```env
    TOKEN=your_discord_bot_token
    ```

4. To run the bot locally:

    ```bash
    python main.py
    ```

### Hosting

Docker container could be hosted on any hostng you prefer, for example for this project was used [fly.io](https://fly.io/)