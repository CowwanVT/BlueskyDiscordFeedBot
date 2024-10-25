# BlueskyDiscordFeedBot

A thing to post things from a bluesky feed into discord

writing a python script was easier than figuring out docker

you need to setup a bot in the discord developers thingy, add your bot token to the script, as well as the channel id and who you want to get posts from

rough install instructions

-Download bot.py
-Place it wherever you like in your file system

-Open bot.py in Notepad or some other text editor

-Add the feed share url between the quotes after feedURL

-Add the discord channel id you want to post to after discordChannelID (right click the channel -> copy channel id)

-Go to https://discord.com/developers/applications

-Click New Application 

-Give it a cute name, accept the terms, and click create

-Go to the Bot tab on the left

-Click Reset Token to get a new token

-Copy it into bot.py after discordBotToken=

-Go to the Oauth2 tab on the left and scroll down to OAuth2 URL Generator

-Select the "bot" scope

-under "Bot Permissions" select "Send Messages"

-Copy the generated URL, go to it, and add the bot to your server

-Go to Python.org > Downloads

-Get the installer for your OS

-Run the installer

-On the first screen select "Add python.exe to PATH"

-Click Install Now

-Let installer run

-open CMD

-Navigate to folder with bot.py

-run the command 'pip install requests audioop-lts discord'

-run python bot.py


