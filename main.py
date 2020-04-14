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
global provaDe
global numeroItensProva
global emoji
global winner
global menuItensProva
global itensRetirados
global isEvento
isEvento = False


#lists
global palavroes
palavroes = ['caralho','puta', 'pqp', 'cu', 'buceta', 'pau']
global gameOrder
global gameOrderFixed
global brothersInGame

brothersInGame = list()
gameOrder = list()
gameOrderFixed = list()
itensRetirados = list()

fluxo = ['resumo','prova_lider','prova_anjo','salva','monstro','indicacao_lider','votacao_casa', 'paredao','eliminação']

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
        self.isMonstro = False

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

    def viraMonstro(self):
        self.isMonstro = True

    def acabaMonstro(self):
        self.isMonstro = False


#Handlers

@bot.message_handler(commands=['join'])
def send_join(message):
    global brothersInGame
    if adOnAir:
        if not any(x.id == message.chat.id for x in brothersInGame):   #erro
            brothersInGame.append(brother(message.chat.first_name, message.chat.id))
            bot.send_message(message.chat.id, message.chat.first_name + " entrou na brincadeira!")
        else:
            bot.send_message(message.chat.id, "Tu já tá, fera!")
    else:
        bot.send_message(message.chat.id, "Quem sabe ano que vem...")


@bot.message_handler(commands=['show_brothers'])
def send_show_joined(message):
    bot.send_message(message.chat.id, "Brothers na casa:")
    list_brothers(message)
    # for person in brothersInGame:
    #     bot.send_message(message.chat.id, "Nome: " + person.name + " ID: " + str(person.id))


@bot.message_handler(commands=['showAdTime'])
def send_show_ad_time(message):
    if adOnAir:
        bot.send_message(message.chat.id, "Faltam " + str(adTimeLeft) + " segundos. Da pra entrar ainda!")
    else:
        bot.send_message(message.chat.id, "Cabou o tempo!")

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id, """Bot para se sentir na casa mais vigiada do Brasil.""")
    bot.send_message(message.chat.id, "by: Mateus Villas Boas")

@bot.message_handler(commands=['prova_lider'])
def send_about(message):
    global isProva
    global provaDe
    global numeroItensProva
    global emoji
    if gameOn:
        isProva = True
        provaDe = "líder"
        bot.send_message(message.chat.id, "Vamos começar a prova de liderança de hoje!")
        numeroItensProva = random.randrange(5, 10)
        provaTexto = random.choice(allProvaSorte).replace("GANHADOR", provaDe).replace("NUMERO",str(numeroItensProva))
        emoji = provaTexto[-1]
        bot.send_message(message.chat.id, provaTexto)
        sorteioOrdem(message)
        provaStart(message)
    else:
        bot.send_message(message.chat.id, "Ainda ta na novela...")


@bot.message_handler(commands=['force_start'])
def send_start(message):
    global adOnAir
    adOnAir = False


@bot.message_handler(commands=['start'])
def send_start(message):
    global gameOn
    global gameStarted
    if not gameStarted:
        gameStarted = True
        bot.send_message(message.chat.id, "Vai entrar no ar a casa mais vigiada do Brasil! \nLogo após os comerciais de " + str(adTime) + " segundos!\nApertem /join para entrar!")
        callAd()
        while adOnAir:
            pass
        gameOn = True
        bot.send_message(message.chat.id, "Estamos de volta e o jogo começou!")
        list_brothers(message)
        entra_fluxo(message)
    else:
        if not gameOn:
            bot.send_message(message.chat.id, "O jogo já vai começar, espere o comercial!")
        else:
            bot.send_message(message.chat.id, "Já estamos no ar!")

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



@bot.message_handler(func=lambda message: gameOn, content_types=['text'])
def palavrao_handler(message):
    if (any(x in message.text for x in palavroes)):
        bot.reply_to(message, "Estamos ao vivo, não fale palavrão! Menos 300 estalecas!")


# escolheu o botão certo
@bot.callback_query_handler(lambda query: ('winner' in query.data) and isProva)
def process_callback_win(query):
    global gameOrder
    global isProva
    global isEvento
    if(query.message.chat.id == gameOrder[0].id):
      for person in brothersInGame:
        if person.id == gameOrder[0].id:
            person.viraLider()
            bot.edit_message_text("Acertou! Acabou a prova! O líder é: 🏆🏆🏆 " + person.name + " 🏆🏆🏆", query.message.chat.id, query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
            break
      gameOrder.pop(0)
      isProva = False
      isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

# escolhei o botão errado
@bot.callback_query_handler(lambda query: ('loser' in query.data) and isProva)
def process_callback_lose(query):
    global gameOrder
    if(query.message.chat.id == gameOrder[0].id):
      gameOrder.pop(0)
      menukeyboard = retiraItem(query.message.chat.id, query.message.message_id, query.data)
      if(len(gameOrder) == 0):
          gameOrder = gameOrderFixed.copy()
          bot.edit_message_text("Errou! E volta para o primeiro: " + gameOrder[0].name, query.message.chat.id, query.message.message_id, reply_markup=menukeyboard)
      else:
          bot.edit_message_text("Errou! Agora é a vez de " + gameOrder[0].name, query.message.chat.id, query.message.message_id, reply_markup=menukeyboard)
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
    for person in brothersInGame:
        bot.send_message(message.chat.id, person.name + ", " + person.nickname)

def sorteioOrdem(message):
    allPeople = brothersInGame.copy()
    global gameOrder
    global gameOrderFixed
    for x in range(len(brothersInGame)):
        randomPlayer = random.choice(allPeople)
        if randomPlayer.isMonstro == False:
            gameOrder.append(randomPlayer)
        allPeople.remove(randomPlayer)
    gameOrderFixed = gameOrder.copy()
    bot.send_message(message.chat.id, "Ordem de jogo: ")
    for x in range(len(gameOrder)):
        bot.send_message(message.chat.id, gameOrder[x].name)


def provaStart(message):
    global emoji
    global winner
    global numeroItensProva
    menuKeyboard = types.InlineKeyboardMarkup()
    winner = random.randrange(numeroItensProva)
    for x in range(numeroItensProva):
        if x == winner:
            menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='winner'+str(x)))
        else:
            menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='loser'+str(x)))


    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)

def retiraItem(cid, mid, item):
    global itensRetirados
    itensRetirados.append(item)
    aux = item.replace('loser','')
    menuKeyboard = types.InlineKeyboardMarkup()
    for x in range(numeroItensProva):
        if x == winner:
            menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='winner'+str(x)))
        else:
            if x == int(aux) or ('loser'+str(x) in itensRetirados):
                menuKeyboard.add(types.InlineKeyboardButton('❌', callback_data='chosen'+str(x)))
            else:
                menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='loser'+str(x)))

    return menuKeyboard
    # bot.edit_message_text("Escolha um: ", cid, mid, reply_markup=menuKeyboard)

def entra_fluxo(message):
    global isEvento
    isEvento = False
    while len(brothersInGame) != 0:
        for evento in fluxo:
            time.sleep(1)
            while isEvento:
                pass
            # FALTA implementar switch-case da maneira certa
            if evento == 'resumo':
                resumo_semana(message)
            elif evento == 'prova_lider':
                isEvento = True
                prova_lider(message)
            elif  evento == 'prova_anjo':
                prova_anjo(message)
            elif evento == 'salva':
                anjo_salva(message)
            elif evento == 'monstro':
                anjo_monstro(message)
            elif evento == 'indicacao_lider':
                indicacao_lider(message)
            elif evento == 'votacao_casa':
                votacao_casa(message)
            elif evento == 'paredao':
                paredao(message)
            elif evento == 'eliminação':
                eliminacao(message)
            else:
                bot.send_message(message.chat.id, "Erro! Fluxo inexistente!")

#fluxo

def resumo_semana(message):
    bot.send_message(message.chat.id, "Resumo da semana: ")


def prova_lider(message):
    bot.send_message(message.chat.id, "Prova do Lider: ")
    global isProva
    global provaDe
    global numeroItensProva
    global emoji
    if gameOn:
        isProva = True
        provaDe = "líder"
        bot.send_message(message.chat.id, "Vamos começar a prova de liderança de hoje!")
        numeroItensProva = random.randrange(5, 10)
        provaTexto = random.choice(allProvaSorte).replace("GANHADOR", provaDe).replace("NUMERO",str(numeroItensProva))
        emoji = provaTexto[-1]
        bot.send_message(message.chat.id, provaTexto)
        sorteioOrdem(message)
        provaStart(message)
    else:
        bot.send_message(message.chat.id, "Ainda ta na novela...")



def prova_anjo(message):
    bot.send_message(message.chat.id, "Prova do anjo não foi implementada: ")

def anjo_salva(message):
    bot.send_message(message.chat.id, "Salvamento do anjo não foi implementado: ")

def anjo_monstro(message):
    bot.send_message(message.chat.id, "Montro não foi implementado: ")

def indicacao_lider(message):
    bot.send_message(message.chat.id, "Indicação do lider não foi implementada: ")

def votacao_casa(message):
    bot.send_message(message.chat.id, "Votação da casa não foi implementada: ")

def paredao(message):
    bot.send_message(message.chat.id, "Paredão não foi implementado: ")

def eliminacao(message):
    bot.send_message(message.chat.id, "Eliminação não foi implementada: ")




bot.polling()
