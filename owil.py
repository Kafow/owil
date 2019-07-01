#!/usr/bin/env python3
import discord
from discord.ext import commands
import requests
from requests.auth import HTTPBasicAuth
import json
import re

client = commands.Bot(command_prefix='-')

f = open("key.txt", "r")
keys = f.read().split(';')
f.close()

##### tokens ####
TOKEN = keys[0]
BLIZZARDID = keys[1]
BLIZZARDSECRET = keys[2]
######       #####


headers = {
    'authorization': "Basic OTY1M2NkNzlmZjc2NDc4ZDk3YTU0ZmE3MGMxMTBjZWI6NUhNZXFKdDN4c1oxNDdlVlBhMkgyaXVkZXBoZlRCU3Y=",
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    'postman-token': "0465aa36-412d-bb62-7d6b-343566676f2c"
}

@client.event
async def on_ready():
    print('bot ready.')
    


@client.command()
async def verify(ctx):
    embed=discord.Embed(title="Please log in using this link and copy and send the code you have been given", url="https://eu.battle.net/oauth/authorize?access_type=online&client_id=9653cd79ff76478d97a54fa70c110ceb&redirect_uri=https://localhost&response_type=code&state=")
    await ctx.message.author.send(embed = embed)
    def check(m):
        return m.author == ctx.message.author and re.search("^EU", m.content)

    msg  = await client.wait_for("message", check= check)
    print (msg.content)
    #getting the access token with the authorization code obtained earliar using this link https://eu.battle.net/oauth/authorize?access_type=online&client_id=9653cd79ff76478d97a54fa70c110ceb&redirect_uri=https://localhost&response_type=code&state=

    payload = "code={}&grant_type=authorization_code&client_id%20=9653cd79ff76478d97a54fa70c110ceb&client_secret=5HMeqJt3xsZ147eVPa2H2iudephfTBSv&redirect_uri=https%3A%2F%2Flocalhost".format(
    msg.content)

    tokenrequest = requests.post('https://eu.battle.net/oauth/token',
                                 data=payload,
                                 headers=headers,
                                 auth=HTTPBasicAuth(BLIZZARDID, BLIZZARDSECRET))
   
    tokenrequest = json.loads(tokenrequest.text)
    print (tokenrequest)
    blizzardToken = tokenrequest["access_token"]
    # getting the battle net based on the access token
    battletagRequest = requests.get(
                                    "https://eu.battle.net/oauth/userinfo",
                                     params={'access_token': blizzardToken})
    battletagRequest = json.loads(battletagRequest.text)
    battletag = battletagRequest["battletag"]
    battletag = battletag.replace('#', '-')
    await ctx.message.channel.send(battletag)
    #getting the rank based on the battle net
    rankRequest = requests.get('https://ow-api.com/v1/stats/pc/eu/{}/profile'.format(battletag))
    rankRequest = json.loads(rankRequest.text)
    rating = rankRequest["rating"]
    #find the name of the rank
    rank =''
    if (rating==0 ):
        rank = 'Unranked'
    elif (0<rating<1500):
        rank = 'Bronze'
    elif (1500<=rating<2000):
        rank = 'Silver'
    elif (2000<= rating < 2500):
        rank = 'Gold'
    elif (2500<= rating <3000):
        rank = 'Platinum'
    elif (3000<= rating < 3500):
        rank = 'Diamond'
    elif (3500<= rating < 4000):
        rank = 'Master'
    elif (4000<= rating):
        rank = 'Grandmaster'
    
    role = discord.utils.get(ctx.guild.roles, name=rank)
    #adds role to message author 
    user = ctx.message.author
    await user.add_roles(role)


client.run(TOKEN)
