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

class Post():
    def __init__(self, post):
        self.postURI = post['post']['uri']
        self.postAuthor = post['post']['author']['handle']
        self.postID = str(self.postURI.split('/')[4]).lower()
        self.postURL = 'https://bsyy.app/profile/'+ self.postAuthor + '/post/' + self.postID
        self.isValid = self.postAuthor != 'handle.invalid'
        self.postCID = post['post']['cid']

class Bluesky():
    def __init__(self):
        self.postIDs = []
        self.postHistoryLimit = 100
        splitFeedURL = feedURL.split('/')
        self.feedURI = 'at://' + splitFeedURL[4] + '/app.bsky.feed.generator/' + splitFeedURL[6]
        self.endpointURL = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getFeed'
        self.requestURL = self.endpointURL + '?feed=' + self.feedURI + '&limit=' + str(limit)
        self.populateHistory()

    def getPosts(self):
        newPosts = []
        response = requests.get(self.requestURL).json()
        postList = response['feed']
        for postData in postList:
            post = Post(postData)
            if post.isValid:
                if post.postCID not in self.postIDs:
                    self.postIDs.append(post.postCID)
                    newPosts.append(post)

        while len(self.postIDs) > self.postHistoryLimit:
            self.postIDs.pop(0)
        return newPosts

    def populateHistory(self):
        response = requests.get(self.requestURL).json()
        postList = response['feed']

        for postData in postList:
            post = Post(postData)
            self.postIDs.append(post.postCID)

def logToConsole(message):
    print(str(time.asctime()) + ' ' + message)


def blueskyChecker(postQueue):
    posts = []
    Bsky = Bluesky()
    while True:
        time.sleep(interval*60)
        logToConsole('Retrieving messages')
        posts = Bsky.getPosts()
        for post in posts:
            postQueue.put(post.postURL)
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
