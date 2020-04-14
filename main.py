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
global adTime
adTime = 2
global adOnAir
adOnAir = False
global adTimeLeft
global gameOn
gameOn = False
global gameStarted
gameStarted = False
global isProva
isProva = False


#lists
global palavroes
palavroes = ['caralho','puta', 'pqp', 'cu', 'buceta', 'pau']
global gameOrder
global gameOrderFixed

BrothersInGame = list()
gameOrder = list()
gameOrderFixed = list()

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


class brother():
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.nickname = random.choice(allNicknames)
        self.isLider = False
        self.isAnjo = False
        self.isSalvo = False
        self.isEmparedado = False

    def viraLider(self):
        self.isLider = True

    def acabaLider(self):
        self.isLider = False

    def viraAnjo(self):
        self.isAnjo = True

    def acabaAnjo(self):
        self.isAnjo = False

    def viraSalvo(self):
        self.isSalvo = True

    def acabaSalvo(self):
        self.isSalvo = False

    def viraEmparedado(self):
        self.isEmparedado = True

    def acabaEmparedado(self):
        self.isEmparedado = False


#Handlers

@bot.message_handler(commands=['join'])
def send_join(message):
    if adOnAir:
        if not any(x.id == message.chat.id for x in BrothersInGame):   #erro
            BrothersInGame.append(brother(message.chat.first_name, message.chat.id))
            bot.send_message(message.chat.id, message.chat.first_name + " entrou na brincadeira!")
        else:
            bot.send_message(message.chat.id, "Tu já tá, fera!")
    else:
        bot.send_message(message.chat.id, "Quem sabe ano que vem...")


@bot.message_handler(commands=['showBrothers'])
def send_show_joined(message):
    bot.send_message(message.chat.id, "Brothers na casa:")
    list_brothers(message)
    # for person in BrothersInGame:
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

@bot.message_handler(commands=['prova_lider'])
def send_about(message):
    global isProva
    if gameOn:
        isProva = True
        provaDe = "líder"
        bot.send_message(message.chat.id, "Vamos começar a prova de liderança de hoje!")
        numero = random.randrange(1, 5)
        provaTexto = random.choice(allProvaSorte).replace("GANHADOR", provaDe).replace("NUMERO",str(numero))
        emoji = provaTexto[-1]
        bot.send_message(message.chat.id, provaTexto)
        sorteioOrdem(message)
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


# escolheu o botão certo
@bot.callback_query_handler(lambda query: ('winner' in query.data) and isProva)
def process_callback_win(query):
    global gameOrder
    global isProva
    if(query.message.chat.id == gameOrder[0].id):
      bot.send_message(query.message.chat.id, "Acertou!")
      for brother in BrothersInGame:
        if brother.id == gameOrder[0].id:
            brother.viraLider()
            break
      gameOrder.pop(0)
      isProva = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

# escolhei o botão errado
@bot.callback_query_handler(lambda query: ('loser' in query.data) and isProva)
def process_callback_lose(query):
    global gameOrder
    if(query.message.chat.id == gameOrder[0].id):
      bot.send_message(query.message.chat.id, "Errou!")
      gameOrder.pop(0)
      if(len(gameOrder) == 0):
          gameOrder = gameOrderFixed.copy()
          bot.send_message(query.message.chat.id, "E volta para o primeiro: " + gameOrder[0].name)
      else:
          bot.send_message(query.message.chat.id, "Sua vez " + gameOrder[0].name)
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")



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
    for person in BrothersInGame:
        bot.send_message(message.chat.id, person.name + ", " + person.nickname)

def sorteioOrdem(message):
    allPeople = BrothersInGame
    global gameOrder
    global gameOrderFixed
    for x in range(len(BrothersInGame)):
        randomPlayer = random.choice(BrothersInGame)
        gameOrder.append(randomPlayer)
        allPeople.remove(randomPlayer)
    gameOrderFixed = gameOrder.copy()
    bot.send_message(message.chat.id, "Ordem de jogo: ")
    for x in range(len(gameOrder)):
        bot.send_message(message.chat.id, gameOrder[x].name)


def provaStart(message, provaDe, numero, emoji):
    menuKeyboard = types.InlineKeyboardMarkup()
    winner = random.randrange(numero)
    for x in range(numero):
        if x == winner:
            menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='winner'+str(x)))
        else:
            menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='loser'+str(x)))


    escolhas = bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)





bot.polling()
