import requests
import json
from datetime import datetime, timezone
import discord
from discord.ext import tasks

feedURL = '' #the share feed url of the feed you want to scrape from

splitURL = feedURL.split('/')
feedURI = 'at://' + splitURL[4] + '/app.bsky.feed.generator/' + splitURL[6]

requestURL = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getFeed'
limit = 50

discordChannelID = #channel ID to post in
discordBotToken = #bot token from discord developer

global lastUpdateTime
lastUpdateTime = datetime.now(timezone.utc).timestamp()

interval = 15 #how many minutes to wait between checks

def getBlueskyPosts():
    constructedURL = requestURL + '?feed=' + feedURI + '&limit=' + str(limit)
    response = requests.get(constructedURL).json()
    return response

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@tasks.loop(minutes = interval)
async def checkPosts():
    global lastUpdateTime
    await client.wait_until_ready()
    channel = client.get_channel(discordChannelID)
    response = getBlueskyPosts()
    for post in response['feed']:
        postTime = datetime.strptime(post['post']['record']['createdAt'],  '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()
        if postTime > (lastUpdateTime):
            postURL = 'https://bsky.app/profile/'+ post['post']['author']['handle'] + '/post/' + post['post']['uri'].split('/')[4]
            await channel.send(postURL)
    lastUpdateTime = datetime.now().timestamp()- 20

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    checkPosts.start()

client.run(discordBotToken)
