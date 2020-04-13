import json
import requests
import time
import urllib
import telebot
import config
import random
import datetime
import os
from telebot import types


bot = telebot.TeleBot("1260151892:AAG8if7VcDgpm63FaaJSFlVku-grhabeo-o")

#global variables
global prodaDe
global adTime
adTime = 2
global adOnAir
adOnAir = False
global adTimeLeft
global questioning
questioning = False
global voting
voting = False
global currentQuestion
currentQuestion = " "
global justVoted
justVoted = False
global gameOn
gameOn = False
global gameStarted
gameStarted = False
sizeOfHand = 5 #quantidade de cartas que se pode ter na mão
global markup
#lists
global choosenPhrase
global palavroes
palavroes = ['caralho','puta', 'pqp', 'cu', 'buceta', 'pau']

# Answers given to a question
givenAnswers = list()
myAnswers = list()
gameQuestions = list()
joinedPeople = list()

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

allNicknames = list()
with open(os.path.join(THIS_FOLDER, 'nicknames.txt'), encoding="utf8") as myfile:
    for line in myfile:
        allNicknames.append(line.replace("\n",""))
myfile.close()

allProvaSorte = list()
with open(os.path.join(THIS_FOLDER, 'prova-sorte.txt'), encoding="utf8") as myfile:
    for line in myfile:
        allProvaSorte.append(line.replace("\n",""))
myfile.close()


class joinedPerson():
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.nickname = random.choice(allNicknames)


#Handlers

@bot.message_handler(commands=['join'])
def send_join(message):
    if adOnAir:
        if (message.chat.first_name, message.chat.id) not in joinedPeople:   #erro
            joinedPeople.append(joinedPerson(message.chat.first_name, message.chat.id))
            bot.send_message(message.chat.id, message.chat.first_name + " entrou na brincadeira!")
        else:
            bot.send_message(message.chat.id, "Tu já tá, fera!")
    else:
        bot.send_message(message.chat.id, "Quem sabe ano que vem...")


@bot.message_handler(commands=['showJoined'])
def send_show_joined(message):
    bot.send_message(message.chat.id, "Brothers na casa:")
    list_brothers(message)
    # for person in joinedPeople:
    #     bot.send_message(message.chat.id, "Nome: " + person.name + " ID: " + str(person.id))


@bot.message_handler(commands=['showAdTime'])
def send_show_ad_time(message):
    if adOnAir:
        bot.send_message(message.chat.id, "Faltam " + str(adTimeLeft) + " segundos. Da pra entrar ainda!")
    else:
        bot.send_message(message.chat.id, "Cabou o tempo!")

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id, """Bot para jogar "Cards Against Humanity" mas com um nome menos agressivo.""")
    bot.send_message(message.chat.id, "by: Mateus Villas Boas")

@bot.message_handler(commands=['provaLider'])
def send_about(message):
    global provaDe
    if gameOn:
        provaDe = "líder"
        bot.send_message(message.chat.id, "Vamos começar a prova de liderança de hoje!")
        numero = random.randrange(10, 20)
        provaTexto = random.choice(allProvaSorte).replace("GANHADOR", provaDe).replace("NUMERO",str(numero))
        emoji = provaTexto[-1]
        bot.send_message(message.chat.id, provaTexto)
        provaStart(message, provaDe, numero, emoji)
    else:
        bot.send_message(message.chat.id, "Ainda ta na novela...")

@bot.message_handler(commands=['start'])
def send_start(message):
    global gameOn
    global gameStarted
    if not gameStarted:
        gameStarted = True
        bot.send_message(message.chat.id, "Vai entrar no ar a casa mais vigiada do Brasil! \nLogo após os comerciais de " + str(adTime) + " segundos!\nApertem /join para entrar!")
        callAd()
    else:
        if adOnAir:
            bot.send_message(message.chat.id, "Espere o comercial acabar. Ainda pode ter gente entrando da casa de vidro.")
        else:
            gameOn = True
            bot.send_message(message.chat.id, "Estamos de volta e o jogo começou!")
            list_brothers(message)


@bot.message_handler(commands=['stop'])
def send_stop(message):
    global gameOn
    global markup
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,"Xau" , reply_markup=markup)
    if gameOn:
        markup = types.ReplyKeyboardRemove()
        gameOn = False
        bot.send_sticker(message.chat.id, "CAADAQADDQADWAABkQe3VH-Hf1l1DAI")
    else:
        bot.send_message(message.chat.id, "Já nem tinha começado, otário!")

@bot.message_handler(commands=['banco_perguntas'])
def send_banco_perguntas(message):
    if len(gameQuestions) != len(allQuestions):
        bot.send_message(message.chat.id, "Inicializando Banco de Perguntas!")
        inicialize_gameQuestions()
        inicialize_my_answers()
    else:
        bot.send_message(message.chat.id, "Banco de Perguntas já está cheio!")


@bot.message_handler(func=lambda message: gameOn, commands=['pergunta'])
def send_question(message):
    global questioning
    global currentQuestion
    global markup
    questioning = True
    if len(gameQuestions) == 0:
        bot.send_message(message.chat.id, "<b>Embaralhando cartas de perguntas.</b>", parse_mode= 'HTML')
        inicialize_gameQuestions()
    if len(myAnswers) == 0:
        inicialize_my_answers()
    currentQuestion = gameQuestions[random.randint(0, len(gameQuestions)-1)]
    gameQuestions.remove(currentQuestion)
    bot.send_message(message.chat.id, "<b>Pergunta:</b>", parse_mode= 'HTML')
    bot.send_message(message.chat.id, currentQuestion, parse_mode= 'HTML')

    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    update_keyboard()
    bot.send_message(message.chat.id, "Cartas de perguntas restantes: " + str(len(gameQuestions)))
    bot.send_message(message.chat.id, "<b>Escolha sua resposta:</b>", reply_markup=markup, parse_mode= 'HTML')

@bot.message_handler(func=lambda message: gameOn, content_types=['text'])
def palavrao_handler(message):
    if (any(x in message.text for x in palavroes)):
        bot.reply_to(message, "Estamos ao vivo, não fale palavrão! Menos 300 estalecas!")

def update_keyboard():
    for answer in myAnswers:
        markup.add(types.KeyboardButton(answer))

#inicializa e enche a lista de perguntas
def inicialize_gameQuestions():
    for question in allQuestions:
        if question not in gameQuestions:
            gameQuestions.append(question)

def inicialize_my_answers():
    for i in range(0, sizeOfHand):
        add_one_answer()

def add_one_answer():
    answer = allAnswers[random.randint(0, len(allAnswers)-1)]
    myAnswers.append(answer)

def callAd():
    global adOnAir
    global adTimeLeft
    adOnAir = True
    start = datetime.datetime.now()
    while adOnAir:
        now = datetime.datetime.now()
        adTimeLeft = round(adTime - (now - start).total_seconds())
        if adTimeLeft < 0:
            adOnAir = False

def list_brothers(message):
    for person in joinedPeople:
        bot.send_message(message.chat.id, person.name + ", " + person.nickname)

def provaStart(message, provaDe, numero, emoji):
    menuKeyboard = types.InlineKeyboardMarkup()
    for x in range(numero):
      menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='button'))


    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)





bot.polling()
