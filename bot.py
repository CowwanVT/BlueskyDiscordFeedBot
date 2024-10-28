import requests
import json
import time
import discord
from discord.ext import tasks
import threading
import queue

feedURL = '' ##the feed url from "share feed"
discordChannelID =    #the discord channel ID to post to
discordBotToken = '' #your discord bot token

limit = 50 #how many records to get at a time
interval = 1 #how many minutes to wait between checks


def logToConsole(message):
    print(str(time.asctime()) + ' ' + message)

def getURL(post):
    author = post['post']['author']['handle']
    postID = post['post']['uri'].split('/')[4]
    postURL = 'https://bsyy.app/profile/'+ author + '/post/' + postID
    return postURL

def getBlueskyPosts():
    postURLs = []
    splitURL = feedURL.split('/')
    feedURI = 'at://' + splitURL[4] + '/app.bsky.feed.generator/' + splitURL[6]
    requestURL = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getFeed'
    constructedURL = requestURL + '?feed=' + feedURI + '&limit=' + str(limit)
    response = requests.get(constructedURL).json()
    for post in response['feed']:
        postURL = getURL(post)
        postURLs.append(postURL)
    return postURLs

def blueskyChecker(postQueue):
    oldPostURLs = []
    postURLs = []
    postURLs = getBlueskyPosts()
    while True:
        time.sleep(interval*60)
        logToConsole('Retrieving messages')
        oldPostURLs = postURLs
        postURLs = getBlueskyPosts()
        for URL in postURLs:
            if URL not in oldPostURLs:
                postQueue.put(URL)
        logToConsole(str(postQueue.qsize()) + ' posts queued')

postQueue = queue.Queue()
blueskyThread = threading.Thread(target=blueskyChecker, args=(postQueue,))
blueskyThread.daemon = True
blueskyThread.start()

client = discord.Client(intents=discord.Intents.default())

@tasks.loop(minutes = interval)
async def checkPosts():
    channel = client.get_channel(discordChannelID)
    logToConsole('Posting ' + str(postQueue.qsize()) + ' messages')
    while postQueue.qsize() > 0:
        await client.wait_until_ready()
        await channel.send(postQueue.get())

@client.event
async def on_ready():
    logToConsole('Logged in as {0.user}'.format(client))
    checkPosts.start()

client.run(discordBotToken)
