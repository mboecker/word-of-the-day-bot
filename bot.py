# This example requires the 'message_content' intent.

import discord
import os
from io import BytesIO
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

def read_mp3_file(filename):
    r = Request(filename, headers={'User-Agent': 'Mozilla/5.0'})
    data = urlopen(r).read()
    return BytesIO(data)

def read_website():
    url = "https://www.dictionary.com/word-of-the-day"
    r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(r).read()
    soup = BeautifulSoup(html, features="html.parser")
    return soup

def get_string(soup, class_):
    elements = soup.find_all(class_=class_)
    if not elements:
        return None
    return elements[0].string

def get_link(soup):
    elements = soup.find_all(class_="wotd-entry-headword")
    if not elements:
        return None
    return elements[0]["href"]

def get_word(soup):
    return get_string(soup, 'wotd-entry-headword')

def get_word_type(soup):
    return get_string(soup, 'wotd-entry-pos')

def get_prono(soup):
    elements = soup.find_all(class_='wotd-entry-phonetics')
    if not elements:
        return None
    res = ""
    for s in elements[0].strings:
        res += s
    return res

def get_desc(soup):
    return get_string(soup, 'wotd-entry-definition')

def get_link(soup):
    elements = soup.find_all(class_="wotd-entry-headword")
    if not elements:
        return None
    return elements[0]["href"]

def get_mp3(soup):
    elements = soup.find_all(class_="common-btn-headword-audio")
    if not elements:
        return None
    link = elements[0]["data-audioorigin"] + "/" + elements[0]["data-audiosrc"]
    return link

async def handle_wotd(channel):
    soup = read_website()
    word = get_word(soup)
    word_type = get_word_type(soup)
    word_prono = get_prono(soup).replace("[","").replace("]","")
    desc = get_desc(soup)
    link = get_link(soup)
    mp3 = get_mp3(soup)
    if word is None or word_type is None or word_prono is None or desc is None or link is None or mp3 is None:
        await channel.send("Sorry :( They changed their website and I cant read todays word")
    else:
        
        msg = f"""> **{word}** (_{word_type}_)
> [ {word_prono} ]
> {desc}
https://www.dictionary.com{link}"""
        f = discord.File(read_mp3_file(mp3), filename=word + ".mp3")
        await channel.send(msg, file = f, suppress_embeds = True)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    channels = [
        client.get_channel(726379185496653847), # general in Vast
        client.get_channel(997926904864718908)  # word smith in Tori's server
    ]
    
    for channel in channels:
        await handle_wotd(channel)
    await client.close()

token = os.getenv("DISCORD_TOKEN")
client.run(token)
