import requests
import json
import time
import discord
from discord.ext import tasks
import threading
import queue
import os
from datetime import datetime

feedURL = '' ##the feed url from "share feed"
discordChannelID =  #the discord channel ID to post to
discordBotToken = '' #your discord bot token

limit = 50 #how many records to get at a time
interval = 1 #how many minutes to wait between checks

def exitThread():
    input()
    os._exit(0)

def make_request(request):
    response = None
    while response == None:
        try:
            response = requests.get(request, timeout = 10)
        except:
            logToConsole("Request timed out, retrying in 30 seconds")
            time.sleep(30)
    return(response.json())


def logToConsole(message):
    print(str(time.asctime()) + ' ' + str(message))

class Post():
    def __init__(self, post):
        self.postURI = post['post']['uri']
        self.postAuthor = post['post']['author']['handle']
        self.postID = str(self.postURI.split('/')[4]).lower()
        self.postURL = 'https://bsyy.app/profile/'+ self.postAuthor + '/post/' + self.postID
        self.isValid = self.postAuthor != 'handle.invalid'
        self.postCID = post['post']['cid']
        self.timestamp = datetime.strptime(post['post']['record']['createdAt'][:19],  '%Y-%m-%dT%H:%M:%S').timestamp()
        self.is_old = self.check_age()
        self.labels = post['post']['labels']
        self.is_porn = False
        self.is_sexual = False
        self.get_labels()

    def check_age(self):
        current_time = datetime.now().timestamp()
        one_week_ago = current_time - 604800
        return(self.timestamp < one_week_ago)

    def get_labels(self):
        for entry in self.labels:
            if entry['val'] == 'porn':
                self.is_porn = True
            if entry['val'] == 'sexual':
                self.is_sexual = True

class Feed():
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
        response = make_request(self.requestURL)

        if "feed" in response:

            if len( response['feed']) > 0:
                for entry in response['feed']:
                    post = Post(entry)
                    if post.isValid and post.postCID not in self.postIDs:
                        newPosts.append(post)
                        self.postIDs.append(post.postCID)

        while len(self.postIDs) > self.postHistoryLimit:
            self.postIDs.pop(0)
        return newPosts
    def populateHistory(self):
        response = make_request(self.requestURL)
        postList = response['feed']
        for postData in postList:
            post = Post(postData)
            self.postIDs.append(post.postCID)

def blueskyChecker(postQueue):
    posts = []
    feed = Feed()
    while True:
        logToConsole('Retrieving messages')
        posts = feed.getPosts()
        for post in posts:
            postQueue.put(post.postURL)
        logToConsole(str(postQueue.qsize()) + ' posts queued')
        time.sleep(interval*60)

postQueue = queue.Queue()
blueskyThread = threading.Thread(target=blueskyChecker, args=(postQueue,))
blueskyThread.daemon = True
blueskyThread.start()


exitThread = threading.Thread(target = exitThread)
exitThread.daemon = True
exitThread.start()
print("Press ENTER to exit at any time")

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
