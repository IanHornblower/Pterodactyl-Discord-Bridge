import discord
from discord.ext import commands, tasks
from discord import app_commands
from keys import *
from api import *
from server import Server
from settings import *
from formatting import *

# Intents (required for newer Discord bots)
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

global servers
servers = []

async def updateServers():
    global servers
    servers = get_servers()

async def updateStatus():
    global servers
    message = ""

    for server in servers[::-1]:
        message += f"{server.name}: {get_circle(server.current_state)}\n"

    activity = discord.Activity(type=discord.ActivityType.playing, name=message)
    await bot.change_presence(activity=activity)

# Register slash commands
@bot.event
async def on_ready():
    await bot.tree.sync()
    
    await periodic()

    periodic.start()

    print(f"Bot is online as {bot.user}")

@tasks.loop(seconds=API_PULL_INTERVAL)
async def periodic():
    await updateServers()

    await updateStatus()

@bot.tree.command(name="status", description="Get the status of all servers")
async def status(interaction: discord.Interaction):
    await periodic()

    embed = discord.Embed(title="Server Statuses", color=discord.Color.from_rgb(200, 56, 3)) # Hex Code "#C83803"

    for server in servers:
        if server.is_online():
            embed.add_field(
                name=f"{server.name}: {get_circle(server.current_state)}",
                value=f"Uptime: {format_uptime(server.uptime)} | RAM: {round(server.memory_usage, 2)} GiB",
                inline=False
            )
        else:
            embed.add_field(
                name=f"{server.name}: {get_circle(server.current_state)}",
                value=f"Status: {server.current_state} | Size on Disk: {round(server.size_on_disk, 2)} GiB",
                inline=False
            )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="start", description="Start a specific server")
async def start(interaction: discord.Interaction):
    global servers
    await periodic()

    # list of offline servers
    offline_servers = []

    for server in servers:
        if server.is_offline():
            offline_servers.append(server)

    if len(offline_servers) < 1:
        await interaction.response.send_message("All servers online")
        return

    options = [
        discord.SelectOption(label=server.name, value=str(server.server_id))
        for server in offline_servers
    ]

    # Create the select menu
    select = discord.ui.Select(
        placeholder="Choose a server...",
        min_values=1,
        max_values=1,
        options=options
    )

    # Create a view with the select menu
    view = discord.ui.View()
    view.add_item(select)

    # Send the message with the dropdown
    await interaction.response.send_message("Please select a server:", view=view)

    # Handle the dropdown selection
    async def on_select(interaction: discord.Interaction):
        # Find the selected server from the offline list
        selected_server = next((server for server in offline_servers if server.server_id == select.values[0]), None)

        if selected_server:
            result = start_server(select.values[0])  # Assuming `start_server` is a function to start the server
            message = ""

            match result:
                case 204:
                    message = f"Stopping: {selected_server.name}"
                case 401:
                    message = f"Unauthorized"
                case 404:
                    message = f"Not Found"
                case 403:
                    message = f"Forbidden"
                case _:
                    message = f"Unknown error"

            await interaction.response.edit_message(content=message, view=None)  # Removes the dropdown by setting view=None
        else:
            await interaction.response.edit_message(content="Server not found or invalid selection.", view=None)

    # Add the select menu callback
    select.callback = on_select

@bot.tree.command(name="stop", description="stop a specific server")
async def stop(interaction: discord.Interaction):
    global servers
    await periodic()

    # list of online servers
    online_servers = []

    for server in servers:
        if server.is_online():
            online_servers.append(server)

    if len(online_servers) < 1:
        await interaction.response.send_message("All servers offline")
        return

    options = [
        discord.SelectOption(label=server.name, value=str(server.server_id))
        for server in online_servers
    ]

    # Create the select menu
    select = discord.ui.Select(
        placeholder="Choose a server...",
        min_values=1,
        max_values=1,
        options=options
    )

    # Create a view with the select menu
    view = discord.ui.View()
    view.add_item(select)

    # Send the message with the dropdown
    await interaction.response.send_message("Please select a server:", view=view)

    # Handle the dropdown selection
    async def on_select(interaction: discord.Interaction):
        # Find the selected server from the offline list
        selected_server = next((server for server in online_servers if server.server_id == select.values[0]), None)

        if selected_server:
            result = stop_server(select.values[0])  # Assuming `start_server` is a function to start the server
            message = ""

            match result:
                case 204:
                    message = f"Stopping: {selected_server.name}"
                case 401:
                    message = f"Unauthorized"
                case 404:
                    message = f"Not Found"
                case 403:
                    message = f"Forbidden"
                case _:
                    message = f"Unknown error"

            await interaction.response.edit_message(content=message, view=None)  # Removes the dropdown by setting view=None
        else:
            # If server isn't found, edit message and remove the dropdown
            await interaction.response.edit_message(content="Server not found or invalid selection.", view=None)

    # Add the select menu callback
    select.callback = on_select

@bot.tree.command(name="force-update", description="force update loop")
async def force_periodic(interaction: discord.Interaction):
    #send_command(server_id, "stop")
    await periodic()

    await interaction.response.send_message("Updated")

bot.run(TOKEN)