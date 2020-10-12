import discord
import logging
import asyncio, json, time, traceback
import sys, os
from os import system
from colored import fg, bg, attr
import re
import requests
import urllib.request
import shutil
import hashlib

EmojiCache = []
Duplicates = 0
EmojisDownloaded = 0
i = 0
N = 0
isBusy = False

os.system('cls' if os.name == 'nt' else 'clear')

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    running_mode = 'Frozen/executable'
else:
    try:
        app_full_path = os.path.realpath(__file__)
        application_path = os.path.dirname(app_full_path)
        running_mode = "Non-interactive (e.g. 'python myapp.py')"
    except NameError:
        application_path = os.getcwd()
        running_mode = 'Interactive'

if os == 'Windows':
    jfile = application_path + '\\settings.json'
else:
    jfile = application_path + '/settings.json'

if os.path.exists(jfile):
    jdata = json.load(open(jfile))
else:
    jdata = open(jfile, 'w')
    jtmp = '{\n\"token\":\"Token_Here\",\n\"command_prefix\":\".\",\n\"keep_dir\":\"false\",\n\"no_dupes\":\"true\"\n}'
    jdata.write(jtmp)
    jdata.close()
    jdata = json.load(open(jfile))

os.environ["rg"] = str(jdata['token'])
token = str(jdata['token'])

os.environ["rg"] = str(jdata['keep_dir'])
keep_dir = bool(jdata['keep_dir'])

os.environ["rg"] = str(jdata['no_dupes'])
no_dupes = bool(jdata['no_dupes'])

os.environ["rg"] = str(jdata['command_prefix'])
command_prefix = str(jdata['command_prefix'])

color = fg('#13A10E')
color2= fg('#ACACAB')
color3 = fg('#FFFFFF')
color_t = fg('#7D0068')
color_p = fg('#FFCC00')
color_err = fg('#FF0000')

res = attr('reset')

print(color
+          "╔╦╗┬┌─┐┌─┐┌─┐┬─┐┌┬┐  ╔═╗┌┬┐┌─┐ ┬┬  ╔╗ ┌─┐┌─┐┬┌─┬ ┬┌─┐\n"
+ color2 + " ║║│└─┐│  │ │├┬┘ ││  ║╣ ││││ │ ││  ╠╩╗├─┤│  ├┴┐│ │├─┘\n"
+ color3 + "═╩╝┴└─┘└─┘└─┘┴└──┴┘  ╚═╝┴ ┴└─┘└┘┴  ╚═╝┴ ┴└─┘┴ ┴└─┘┴  \n"
+ res)
version_num = 'v1.0.5'
print(f'\33]0;DEB ' + version_num + ' - Developed by: Notorious\a', end='', flush=True)
r = requests.get('https://raw.githubusercontent.com/noto-rious/DEB/main/version.txt').text
if r != version_num:
    print(color_err + 'Looks like you may not be running the most current version. Check https://noto.cf/deb for an update!' + res)
    print()
if token == "Token_Here":
        print (color_err + "You haven't properly configured the \'settings.json\' file. Please put your Discord token in settings.json using the correct JSON syntax and then run the program again." + res)
        time.sleep(30)
        sys.exit()

client = discord.Client()
ready = False

def progress(count, total, status=''):
    bar_len = 8
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar =  '='  * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write("\033[K")
    sys.stdout.write('\r[%s %s%s] %s\r' % (color + bar + res, color_p + str(percents), '%' + res, status))
    
    sys.stdout.flush()

def calc_Chan():
    chans = 0
    for guild in client.guilds:
        chans += len(guild.channels)
    return f'{chans:,}'

def format_ename(name):
    name = ':' + name + ':'
    name = name.ljust(20, ' ')
    name = (name[:17] + '...') if len(name) > 20 else name
    return name

def format_dupes():
    dupe_string =  f'{Duplicates:,}'
    dupe_string = dupe_string.ljust(9, ' ')
    dupe_string = (dupe_string[:6] + '...') if len(dupe_string) > 9 else dupe_string
    return dupe_string

def format_p():
    percent = int(100 * i / N)
    percent = str(percent) + '%'.ljust(3, ' ')
    percent = (percent[:3]) if len(percent) > 3 else percent
    return percent
 
def clean_fs_str(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"
    return "".join(safe_char(c) for c in s).rstrip("_")

def create_dir(dir):
        dir = os.path.dirname(dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            if keep_dir != True:
                shutil.rmtree(dir)
                os.makedirs(dir)

def save_emoji(url,path,guild,emoji):
    global i
    global N
    global EmojisDownloaded
    try:
        r = requests.get(url,emoji)
        #print(path)
        if r != None:
            imgSHA1 = hashlib.sha1(r.content).hexdigest()
            if no_dupes != False:
                if imgSHA1 in EmojiCache:
                    global Duplicates
                    Duplicates += 1
                else:
                    EmojiCache.append(imgSHA1)
                    if os.path.exists(path):
                        os.remove(path)
                    with open(path, 'wb') as handler:
                        handler.write(r.content)
                        EmojisDownloaded += 1
            else:
                if os.path.exists(path):
                        os.remove(path)
                with open(path, 'wb') as handler:
                    handler.write(r.content)
                    EmojisDownloaded += 1
    except requests.exceptions.Timeout:
        #timeout error
        save_emoji(url,path,guild,emoji)
    except requests.exceptions.RequestException as e:
        #catastrophic error. bail.
        #raise SystemExit(e)
        save_emoji(url,path,guild,emoji)

def calc_time(start):
    elapsed = time.time() - start
    seconds = elapsed % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60  
    return "%d:%02d:%02d" % (hour, minutes, seconds)
try:
    @client.event
    async def on_connect():
        global ready
        if ready == False:
            ready = True
            print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup -> Welcome, ' + color + str(client.user) + res + '.')
            print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup is now listening for ' + color + command_prefix + 'b' + res + ' or ' + color + command_prefix + 'ba' + res + ' in ' + color + calc_Chan() + res + ' channels in ' + color + f'{len(client.guilds):,}' + res + ' servers.')
            print()

    @client.event
    async def on_ready():
        global ready
        if ready == False:
            ready = True
            print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup -> Welcome, ' + color + str(client.user) + res + '.')
            print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup is now listening for ' + color + command_prefix +  'b' + res + ' or ' + color + command_prefix + 'ba' + res + ' in ' + color + calc_Chan() + res + ' channels in ' + color + f'{len(client.guilds):,}' + res + ' servers.')
            print()

    @client.event
    async def on_message(msg):
        global command_prefix
        global i
        global N
        global Duplicates
        global ready
        global EmojisDownloaded
        global isBusy

        if ready == False:
            ready = True
            print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup -> Welcome, ' + color + str(client.user) + res + '.')
            print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup is now listening for ' + color + command_prefix + 'b' + res + ' or ' + color + command_prefix + 'ba' + res + ' in ' + color + calc_Chan() + res + ' channels in ' + color + f'{len(client.guilds):,}' + res + ' servers.')
            print()

        #get current guild emojis
        if msg.content == command_prefix + 'b' and msg.author == client.user:
            start_time = time.time()
            await msg.edit(content='x')
            await msg.edit(content='xD')
            await msg.delete()
            if isBusy == True:
                 return
            if msg.guild == None:
                print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup -> ' + color_p + '{}%'.format(int(100 * i / N)) + res + ' -> Discord Emoji Backup -> I\'m pretty sure I can\'t get emojis from DM\'s')
                return
            print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup -> ' + color + command_prefix + 'b' + res + ' accepted in ' + color + str(msg.guild.name) + res + '. Please wait...' + res)
            if os.name == 'nt':
                emoji_path = application_path + '\\' + clean_fs_str(str(client.user)) + '\\' + clean_fs_str(str(msg.guild.name)) + '\\'
                create_dir(emoji_path)
            else:
                emoji_path = application_path + '/' + clean_fs_str(str(client.user)) + '/' + clean_fs_str(str(msg.guild.name)) + '/'
                create_dir(emoji_path)

            guild = client.get_guild(msg.guild.id)
            GEmojiList = guild.emojis

            isBusy = True
            i = 0
            tmp_guild = ''
            N = len(GEmojiList)
            for emoji in GEmojiList:
                emojiraw = str(emoji)

                if emoji.animated == True:
                    save_emoji('https://cdn.discordapp.com/emojis/' + str(emoji.id) + '.gif?v=1', emoji_path + emoji.name + '.gif',guild.name,emoji.name)
                else:
                    save_emoji('https://cdn.discordapp.com/emojis/' + str(emoji.id) + '.png?v=1', emoji_path + emoji.name + '.png',guild.name,emoji.name)
                i += 1
                tmp_guild = str(guild)
                tmp_guild = (tmp_guild[:14] + '...') if len(tmp_guild) > 17 else tmp_guild
                if no_dupes != False:
                    progress(i, N, res + 'Elapsed time: ' + color + calc_time(start_time) + res + ' -> Duplicates: ' + color + f'{Duplicates:,}' + res + ' -> Downloaded: ' + color + f'{EmojisDownloaded:,}' + res + ' from ' + color +  str(tmp_guild) + res)
                else:
                    progress(i, N, res + 'Elapsed time: ' + color + calc_time(start_time) + res + ' -> Downloaded: ' + color + f'{EmojisDownloaded:,}' + res + ' from ' + color +  str(tmp_guild) + res)
            time_took = time.time() - start_time
            if no_dupes != False:
                progress(i, N, res +  'Finished! Time Took: ' + color + calc_time(start_time) + res + ' -> Duplicates Ignored: ' + color + f'{Duplicates:,}' + res + ' -> Emojis Downloaded: ' + color + f'{EmojisDownloaded:,}' + res)
            else:
                progress(i, N, res +  'Finished! Time Took: ' + color + calc_time(start_time) + res + ' -> Emojis Downloaded: ' + color + f'{EmojisDownloaded:,}' + res)
            print()
            print()
            isBusy = False
            return
        #get all emojis    
        if msg.content == command_prefix + 'ba' and msg.author == client.user:
            start_time = time.time()
            await msg.edit(content='x')
            await msg.edit(content='xD')
            await msg.delete()
            if isBusy == True:
                 return
            if msg.guild == None:
                print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup -> ' + color +command_prefix +  'ba' + res + ' accepted in ' + color + str(client.get_channel(msg.channel.id)).replace('Direct Message', 'DM') + res + '. Please wait...' + res)
            else:
                print(res + color_t + time.strftime('%I:%M %p', time.localtime()).rstrip() + res +' -> Discord Emoji Backup -> ' + color +command_prefix +  'ba' + res + ' accepted in ' + color + str(msg.guild.name) + res + '. Please wait...' + res)
            for guild in client.guilds:
                if os.name == 'nt':
                    emoji_path = application_path + '\\' + clean_fs_str(str(client.user)) + '\\' + clean_fs_str(guild.name) + '\\'
                    create_dir(emoji_path)
                else:
                    emoji_path = application_path + '/' + clean_fs_str(str(client.user)) + '/' + clean_fs_str(guild.name) + '/'
                    create_dir(emoji_path)

            tmp_guild = ''
            EmojiList = client.emojis
            i = 0
            N = len(EmojiList)
            isBusy = True
            for emoji in EmojiList:
                guild = emoji.guild
                emojiraw = str(emoji)
                emoji_path = application_path + '\\' + clean_fs_str(str(client.user)) + '\\' + clean_fs_str(str(emoji.guild.name)) + '\\'

                if emoji.animated == True:
                    save_emoji('https://cdn.discordapp.com/emojis/' + str(emoji.id) + '.gif?v=1', emoji_path + emoji.name + '.gif',guild.name,emoji.name)
                else:
                    save_emoji('https://cdn.discordapp.com/emojis/' + str(emoji.id) + '.png?v=1', emoji_path + emoji.name + '.png',guild.name,emoji.name)
                i += 1
                tmp_guild = str(guild)
                tmp_guild = (tmp_guild[:14] + '...') if len(tmp_guild) > 17 else tmp_guild
                if no_dupes != False:
                    progress(i, N, res + 'Elapsed time: ' + color + calc_time(start_time) + res + ' -> Duplicates: ' + color + f'{Duplicates:,}' + res + ' -> Downloaded: ' + color + f'{EmojisDownloaded:,}' + res + ' from ' + color +  str(tmp_guild) + res)
                else:
                    progress(i, N, res + 'Elapsed time: ' + color + calc_time(start_time) + res + ' -> Downloaded: ' + color + f'{EmojisDownloaded:,}' + res + ' from ' + color +  str(tmp_guild) + res)
            time_took = time.time() - start_time
            if no_dupes != False:
                progress(i, N, res +  'Finished! Time Took: ' + color + calc_time(start_time) + res + ' -> Duplicates Ignored: ' + color + f'{Duplicates:,}' + res + ' -> Emojis Downloaded: ' + color + f'{EmojisDownloaded:,}' + res)
            else:
                progress(i, N, res +  'Finished! Time Took: ' + color + calc_time(start_time) + res + ' -> Emojis Downloaded: ' + color + f'{EmojisDownloaded:,}' + res)
            print()
            print()
            isBusy = False
            return

    client.run(token, bot=False)
except KeyboardInterrupt:
        raise
except:
    print('Are you sure you typed the correct user authorization token?')
    sys.tracebacklimit = 0
    time.sleep(30)
    sys.exit()
    #file = open('Error_Log.txt', 'w')
    #file.write(traceback.format_exc())
    #file.close()
    #exit(0)     