import colorama
import requests
import urllib
import telebot
from datetime import datetime
import os


apiKey = "YOUR TOKEN GOES HERE"
bot = telebot.TeleBot(apiKey)


logo = """
 ███╗   ███╗ ██████╗████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗██████╗  ██████╗ ████████╗
 ████╗ ████║██╔════╝╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔═══██╗╚══██╔══╝
 ██╔████╔██║██║        ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║██████╔╝██║   ██║   ██║   
 ██║╚██╔╝██║██║        ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║██╔══██╗██║   ██║   ██║   
 ██║ ╚═╝ ██║╚██████╗   ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║██████╔╝╚██████╔╝   ██║   
 ╚═╝     ╚═╝ ╚═════╝   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝  ╚═════╝    ╚═╝   

"""


def extract_arg(arg): #Thanks stack overflow :3
    return arg.split()[1:]


def getUserInfo(name, msg):
    r = requests.get(f"https://api.ashcon.app/mojang/v2/user/{name}", headers={"User-Agent": "MCTelegramBot"})
    if(r.status_code == 200):
        userData = []
        userData.append("UUID: "+r.json()['uuid'])
        userData.append("Creation Date: "+r.json()['created_at'])
        userData.append("Name History: ")
        for historyData in r.json()['username_history']:
            name = historyData['username']
            try:
                changedAt = historyData['changed_at'].split(".")[0].replace('T', ' ')
                userData.append(f"  {name} @ {changedAt}")
            except:
                userData.append(f"  {name} - Original Name")
        bot.send_message(msg.chat.id, '\n'.join(userData))

    elif(r.status_code == 404):
        bot.send_message(msg.chat.id, f"No such user as {name}")
    else:
        bot.send_message(msg.chat.id, f"Ashcon returned an unknown error {r.status_code}")


def getSkin(name, msg):
    #There's probably a better way to do this
    f = open('tmp.jpg','wb') #I was about to make this use a command to gen name+randnum but that could create an RCE (insert '; payload' into the name) and that's very spoopy
    f.write(urllib.request.urlopen("https://mc-heads.net/body/"+name).read(), headers={"User-Agent": "MCTelegramBot"})
    f.close()

    bot.send_chat_action(msg.chat.id, 'upload_photo')
    img = open('tmp.jpg', 'rb') 
    bot.send_photo(msg.chat.id, img)
    img.close()
    os.remove('tmp.jpg')


def getThreeChars(msg):
    r = requests.get("http://api.coolkidmacho.com/three", headers={"User-Agent": "MCTelegramBot"})
    if(r.status_code != 200):
        bot.send_message(msg.chat.id, f"The API did not respond, status code: {r.status_code}")
    else:
        i = 0
        names = []
        for name in r.json():
            if(i >= 5):
                break
            time = str(datetime.fromtimestamp(name['droptime']))
            names.append(f"{name['name']} Drops at {time}")
            i+=1
        bot.send_message(msg.chat.id, '\n'.join(names))


def getDroptime(name, msg):
    print(f"Looking Up: {name}")
    r = requests.get(f"http://api.star.shopping/droptime/{name}", headers={"User-Agent": "Sniper"}) #Sniper user-agent used to prevent CF triggering
    print("Status Code: "+str(r.status_code))
    print("Body: "+r.text)

    if r.status_code >= 400:
        bot.send_message(msg.chat.id, f"This name isn't dropping, status code: {r.status_code}")
    else:
        dropTime = str(datetime.fromtimestamp(r.json()["unix"]))
        bot.send_message(msg.chat.id, f"The name {name} will drop at {dropTime}")


@bot.message_handler(commands=['names'])
def names(msg):
    getThreeChars(msg)


@bot.message_handler(commands=['help', '?'])
def names(msg):
    bot.send_message(msg.chat.id, f"Commands:\n/names - Show dropping 3 chars\n/skin [USERNAME] - Show the skin of a user\n/lookup [USERNAME] - Show information about a user (Ashcon)\n/droptime [USERNAME] - Find when a name is dropping\n/author - Show who created the program")


@bot.message_handler(commands=['skin'])
def dropTime(msg):
    try:
        name = extract_arg(msg.text)[0]
        getSkin(name, msg)
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, f"Usage: /skin name")


@bot.message_handler(commands=['lookup'])
def lookupUser(msg):
    try:
        name = extract_arg(msg.text)[0]
        getUserInfo(name, msg)
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, f"Usage: /lookup name")


@bot.message_handler(commands=['droptime'])
def dropTime(msg):
    try:
        name = extract_arg(msg.text)[0]
        getDroptime(name, msg)
    except Exception as e:
        print(e)
        bot.send_message(msg.chat.id, f"Usage: /droptime name")


@bot.message_handler(commands=['author'])
def test(msg):
    bot.send_message(msg.chat.id, "Created by Kami147")


def main():
    colorama.init()
    print(logo.replace("█", "\033[36m█").replace("║", "\033[90m║").replace("╚", "\033[90m╚").replace("╗", "\033[90m╗").replace("╔", "\033[90m╔"))
    print("\033[90m[\033[92m+\033[90m] \033[36mMCTelegramBot \033[39mhas started\033[90m!\033[39m")
    bot.polling()


if __name__ == "__main__":
    main()