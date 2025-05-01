import discord
import os
from discord import app_commands
from replit import db

intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True
intents.members = True
intents.messages = True
intents.bans = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def setLogChannel(serverId, channelId):
  db["logChannel_" + str(serverId)] = channelId


def clearLogChannel(serverId):
  key = "logChannel_" + str(serverId)
  if key in db.keys():
    del db["logChannel_" + str(serverId)]


def getLogChannel(serverId):
  key = "logChannel_" + str(serverId)
  if key in db.keys():
    channelId = db[key]
    channel = client.get_channel(channelId)
    return channel
  else:
    return None


async def sendLog(serverId, message):
  channel = getLogChannel(serverId)
  if channel is not None:
    await channel.send(message)


def setActiveChannel(serverId, channelId):
  db["activeChannel_" + str(serverId)] = channelId


def clearActiveChannel(serverId):
  key = "activeChannel_" + str(serverId)
  if key in db.keys():
    del db[key]


def getActiveChannelId(serverId):
  key = "activeChannel_" + str(serverId)
  if key in db.keys():
    return db[key]
  else:
    return None


def getActiveChannel(serverId):
  channelId = db["activeChannel_" + str(serverId)]
  return client.get_channel(channelId)

async def handleMessageInActiveChannel(message):
  user = message.author
  canManageChannels = message.author.guild_permissions.manage_channels
  if not canManageChannels and not user.bot:
    await user.send(
      "You have been kicked from the Kappa Klub discord as your account has likely been compromised and is being used to post spam. Please secure your account before rejoining the server. " + os.getenv('inviteURL')
    )
    await user.ban(delete_message_days=1,reason="posted in trap channel")
    await user.unban()
    await sendLog(
      message.guild.id, user.mention + " kicked for message in " +
      getActiveChannel(message.guild.id).mention + ": " + message.content)

@tree.command(name="set_log_channel", description = "Set logging channel", guild=discord.Object(id=os.getenv('guildId')))
@app_commands.describe(channel="The channel to set")
@app_commands.default_permissions(manage_channels=True)
async def set_log_channel(interaction, channel: discord.TextChannel):
  serverId = channel.guild.id
  if channel is not None:
    setLogChannel(serverId, channel.id)
    await interaction.response.send_message("Log channel set to " + channel.mention, ephemeral=True)
  else:
    await interaction.response.send_message("No mentioned channel", ephemeral=True)

@tree.command(name="clear_log_channel", description = "Clear logging channel", guild=discord.Object(id=os.getenv('guildId')))
@app_commands.default_permissions(manage_channels=True)
async def clear_log_channel(interaction):
  serverId = interaction.guild.id
  channel = getLogChannel(serverId)
  if channel is not None:
    clearLogChannel(serverId)
    await interaction.response.send_message("No longer logging in " + channel.mention, ephemeral=True)
  else:
    interaction.response.send_message("No log channel set", ephemeral=True)

@tree.command(name="set_trap_channel", description = "Set trap channel", guild=discord.Object(id=os.getenv('guildId')))
@app_commands.describe(channel="The channel to set")
@app_commands.default_permissions(manage_channels=True)
async def set_trap_channel(interaction, channel: discord.TextChannel):
  serverId = channel.guild.id
  if channel is not None:
    setActiveChannel(serverId, channel.id)
    await interaction.response.send_message("Trap channel set to " + channel.mention, ephemeral=True)
  else:
    await interaction.response.send_message("No mentioned channel", ephemeral=True)

@tree.command(name="clear_trap_channel", description = "Clear trap channel", guild=discord.Object(id=os.getenv('guildId')))
@app_commands.default_permissions(manage_channels=True)
async def clear_trap_channel(interaction):
  serverId = interaction.guild.id
  channel = getActiveChannel(serverId)
  if channel is not None:
    clearActiveChannel(serverId)
    await interaction.response.send_message("No longer trapping in " + channel.mention, ephemeral=True)
    await sendLog(serverId, "No longer trapping in " + channel.mention)
  else:
    await interaction.response.send_message("No trap channel set", ephemeral=True)

@client.event
async def on_ready():
  await tree.sync(guild=discord.Object(id=os.getenv('guildId')))
  print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.channel.id == getActiveChannelId(message.guild.id):
    await handleMessageInActiveChannel(message)


client.run(os.getenv('TOKEN'))
