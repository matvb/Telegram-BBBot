import json
import requests
import time
import urllib
import telebot
import config
import random
import datetime
import os
import glob
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
global quantEmparedados
quantEmparedados = 0
global host

#lists
global palavroes
palavroes = ['caralho','puta', 'pqp', 'cu', 'buceta', 'pau']
global gameOrder
global gameOrderFixed
global brothersInGame
global allHosts
allHosts = ['bial','thiago','boninho']

brothersInGame = list()
gameOrder = list()
gameOrderFixed = list()
itensRetirados = list()


fluxo = ['resumo','prova_lider','prova_anjo','salva','monstro','indicacao_lider','votacao_casa', 'paredao','eliminação', 'reset_stats']
# tiposProvas = ['sorte','conhecimento']
allTiposProvas = ['sorte']

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

allResumo = list()
with open(os.path.join(THIS_FOLDER, 'resumo.txt'), encoding="utf8") as myfile:
    for line in myfile:
        allResumo.append(line.replace("\n",""))
myfile.close()

allEliminacao = list()
with open(os.path.join(THIS_FOLDER, 'eliminacao.txt'), encoding="utf8") as myfile:
    for line in myfile:
        allEliminacao.append(line.replace("\n",""))
myfile.close()

thiagofotos = list()
for foto in glob.glob('./img/thiago*.jpg'):
    im = open(foto, 'rb')
    thiagofotos.append(im)

bialfotos = list()
for foto in glob.glob('./img/bial*.jpg'): #
    im = open(foto, 'rb')
    bialfotos.append(im)

boninhofotos = list()
for foto in glob.glob('./img/boninho*.jpg'): #
    im = open(foto, 'rb')
    boninhofotos.append(im)

premioFotos = list()
for foto in glob.glob('./img/premio*.jpg'): #
    im = open(foto, 'rb')
    premioFotos.append(im)

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
        self.votos = 0
        self.votou = False
        self.salvou = False
        self.monstrou = False
        self.desempatou = False
        self.indicou = False

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

    def recebeVoto(self):
        self.votos += 1

    def zeraVoto(self):
        self.votos = 0

    def jaVotou(self):
        self.votou = True

    def zeraVotou(self):
        self.votou = False

    def jaSalvou(self):
        self.salvou = True

    def zeraSalvou(self):
        self.salvou = False

    def jaMonstrou(self):
        self.monstrou = True

    def zeraMonstrou(self):
        self.monstrou = False

    def jaDesempatou(self):
        self.desempatou = True

    def zeraDesempatou(self):
        self.desempatou = False

    def jaIndicou(self):
        self.indicou = True

    def zeraIndicou(self):
        self.indicou = False



#Handlers

@bot.message_handler(commands=['join'])
def send_join(message):
    global brothersInGame
    if adOnAir:
        if not any(x.id == message.chat.id for x in brothersInGame):   #erro
            brothersInGame.append(brother(message.chat.first_name, message.chat.id))
            bot.send_message(message.chat.id, message.chat.first_name + ", seja bem-vindo ao BBT!")
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


@bot.message_handler(commands=['show_ad_time'])
def send_show_ad_time(message):
    if adOnAir:
        bot.send_message(message.chat.id, "Faltam " + str(adTimeLeft) + " segundos. Da pra entrar ainda!")
    else:
        bot.send_message(message.chat.id, "Cabou o tempo!")

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id, """Bot para se sentir na casa mais vigiada do Brasil.""")
    bot.send_message(message.chat.id, "by: Mateus Villas Boas")


@bot.message_handler(commands=['force_start'])
def send_start(message):
    global adOnAir
    adOnAir = False

@bot.message_handler(commands=['start'])
def send_start(message):
    global gameOn
    global gameStarted
    global host
    if not gameStarted:
        gameStarted = True
        bot.send_message(message.chat.id, "Vai entrar no ar o chat mais vigiado do Brasil! \nLogo após os comerciais de " + str(adTime) + " segundos!\nApertem /join para entrar!")
        call_ad()
        while adOnAir:
            pass
        gameOn = True
        host = random.choice(allHosts)
        bot.send_message(message.chat.id, "Começando mais uma temporada de Big Brother Telegram, o chat mais vigiado do Brasil!\nSou " + host.title() + ", o seu apresentador essa noite!")
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
    global itensRetirados
    if(query.message.chat.id == gameOrder[0].id):
      for person in brothersInGame:
        if person.id == gameOrder[0].id:
            bot.edit_message_text("Acertou! Acabou a prova! O " + provaDe + " é: 🏆🏆🏆 " + person.name + " 🏆🏆🏆", query.message.chat.id, query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
            if provaDe == 'líder':
                person.viraLider()
            elif provaDe == 'anjo':
                person.viraAnjo()
            else:
                bot.send_message(query.message.chat.id, "Algo deu errado! Essa prova não é de líder nem de anjo?")
            break
      gameOrder.pop(0)
      isProva = False
      isEvento = False
      itensRetirados = list()
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

# escolhei o botão errado
@bot.callback_query_handler(lambda query: ('loser' in query.data) and isProva)
def process_callback_lose(query):
    global gameOrder
    if(query.message.chat.id == gameOrder[0].id):
      gameOrder.pop(0)
      menukeyboard = retira_item(query.message.chat.id, query.message.message_id, query.data)
      if(len(gameOrder) == 0):
          gameOrder = gameOrderFixed.copy()
          bot.edit_message_text("Errou! E volta para o primeiro: " + gameOrder[0].name, query.message.chat.id, query.message.message_id, reply_markup=menukeyboard)
      else:
          bot.edit_message_text("Errou! Agora é a vez de " + gameOrder[0].name, query.message.chat.id, query.message.message_id, reply_markup=menukeyboard)
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('salva' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento

    brotherAnjo = next(brother for brother in brothersInGame if brother.isAnjo == True)
    if(query.message.chat.id == brotherAnjo.id) and (not brotherAnjo.salvou):
        brotherSalvo = next(brother for brother in brothersInGame if brother.id == query.data.replace('salva',''))
        brotherSalvo.viraSalvo()
        brotherAnjo.jaSalvou()
        bot.edit_message_text( brotherAnjo.nome + "salvou " + brotherSalvo.nome, query.message.chat.id + "!", query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('monstro' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento

    brotherAnjo = next(brother for brother in brothersInGame if brother.isAnjo == True)
    if(query.message.chat.id == brotherAnjo.id) and (not brotherAnjo.monstrou):
        brotherMontro = next(brother for brother in brothersInGame if brother.id == query.data.replace('montro',''))
        brotherMontro.viraMonstro()
        brotherMontro.jaVotou()
        brotherAnjo.jaMonstrou()
        bot.edit_message_text( brotherAnjo.nome + " deu o montro para " + brotherMontro.nome, query.message.chat.id + "!", query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('indicado' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento
    global quantEmparedados

    brotherLider = next(brother for brother in brothersInGame if brother.isLider == True)
    if(query.message.chat.id == brotherLider.id) and (not brotherLider.indicou):
        brotherIndicado = next(brother for brother in brothersInGame if brother.id == query.data.replace('indicado',''))
        brotherIndicado.viraEmparedado()
        quantEmparedados += 1
        brotherLider.jaIndicou()
        bot.edit_message_text( brotherLider.nome + " fez sua escolha. " + brotherIndicado.nome, query.message.chat.id + ", você está no paredão!", query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('voto' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento
    if any(x.id == query.message.chat.id for x in brothersInGame):
        brotherVotou = next(brother for brother in brothersInGame if brother.id == query.message.chat.id)
        if (not brotherVotou.votou) and (not brotherVotou.isMonstro):
            brotherVotou.jaVotou()
            brotherVotado = next(brother for brother in brothersInGame if brother.id == query.data.replace('voto',''))
            brotherVotado.recebeVoto()

@bot.callback_query_handler(lambda query: ('desempate' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento
    global quantEmparedados

    brotherLider = next(brother for brother in brothersInGame if brother.isLider == True)
    if(query.message.chat.id == brotherLider.id) and quantEmparedados < 3:
        brotherIndicado = next(brother for brother in brothersInGame if brother.id == query.data.replace('desempate',''))
        brotherIndicado.viraEmparedado()
        quantEmparedados += 1
        bot.edit_message_text( brotherLider.nome + " fez sua escolha. " + brotherIndicado.nome, query.message.chat.id + ", você está no paredão!", query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")


def call_ad():
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
    bot.send_message(message.chat.id, "Brothers: ")
    for person in brothersInGame:
        bot.send_message(message.chat.id, person.name + ", " + person.nickname)

def sorteio_ordem(message):
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


def prova_sorte(message):
    global emoji
    global winner
    global numeroItensProva

    numeroItensProva = random.randrange(5, 10)
    provaTexto = random.choice(allProvaSorte).replace("GANHADOR", provaDe).replace("NUMERO",str(numeroItensProva))
    emoji = provaTexto[-1]
    bot.send_message(message.chat.id, provaTexto)
    sorteio_ordem(message)


    menuKeyboard = types.InlineKeyboardMarkup()
    winner = random.randrange(numeroItensProva)
    for x in range(numeroItensProva):
        if x == winner:
            menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='winner'+str(x)))
        else:
            menuKeyboard.add(types.InlineKeyboardButton(emoji, callback_data='loser'+str(x)))


    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)

def retira_item(cid, mid, item):
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
                isEvento = True
                resumo_semana(message)
            elif evento == 'prova_lider':
                isEvento = True
                prova(message, 'líder')
            elif  evento == 'prova_anjo':
                isEvento = True
                prova(message, 'anjo')
            elif evento == 'salva':
                isEvento = True
                anjo_salva(message)
            elif evento == 'monstro':
                isEvento = True
                anjo_monstro(message)
            elif evento == 'indicacao_lider':
                isEvento = True
                indicacao_lider(message)
            elif evento == 'votacao_casa':
                isEvento = True
                votacao_casa(message)
            elif evento == 'paredao':
                isEvento = True
                paredao(message)
            elif evento == 'eliminação':
                isEvento = True
                eliminacao(message)
            elif evento == 'reset_stats':
                isEvento = True
                reset_stats(message)
            else:
                bot.send_message(message.chat.id, "Erro! Fluxo inexistente!")

#fluxo

def resumo_semana(message):
    global isEvento
    if host == 'thiago':
        bot.send_photo(message.chat.id, random.choice(thiagofotos))
    elif host == 'boninho':
        bot.send_photo(message.chat.id, random.choice(boninhofotos))
    elif host == 'bial':
        bot.send_photo(message.chat.id, random.choice(bialfotos))
    bot.send_message(message.chat.id, "Resumo da semana: ")
    resumo = ""
    for brother in brothersInGame:
        brother2 = random.choice(brothersInGame)
        if len(brothersInGame) > 1:
            while (brother.id == brother2.id):
                brother2 = random.choice(brothersInGame)
        frase = random.choice(allResumo)
        frase = frase.replace('JOGADOR1',brother.name).replace('JOGADOR2',brother2.name)
        frase = frase.replace('JOG1',brother.name[:3]).replace('JOG2',brother2.name[-3:])
        bot.send_message(message.chat.id, frase)
        time.sleep(1)
    time.sleep(3)
    isEvento = False





def prova(message, provaDeQue):
    bot.send_message(message.chat.id, "Prova do " + provaDeQue + ": ")
    global isProva
    global provaDe
    if gameOn:
        isProva = True
        provaDe = provaDeQue
        bot.send_message(message.chat.id, "Vamos começar a prova do " + provaDe + " de hoje!")
        provaTipo = random.choice(allTiposProvas)
        if provaTipo == 'sorte':
            prova_sorte(message)
        elif provaTipo == 'conhecimento':
            bot.send_message(message.chat.id, "Prova de conhecimento não implementada.")
        else:
            bot.send_message(message.chat.id, "Outros tipos de prova não implementados.")
    else:
        bot.send_message(message.chat.id, "Ainda ta na novela...")


def anjo_salva(message):
    bot.send_message(message.chat.id, "Anjo, quem você deseja imunizar nessa rodada? ")

    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        if not brother.isAnjo:
            menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'salva' + brother.id))
    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)


def anjo_monstro(message):
    bot.send_message(message.chat.id, "Anjo, quem você bota de monstro essa rodada?\nLembrando que o montro não participa da votação da casa!")

    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        if not brother.isAnjo:
            menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'monstro' + brother.id))
    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)

def indicacao_lider(message):
    bot.send_message(message.chat.id, "Líder, está na sua vez. Quem você coloca no paredão?")
    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        if (not brother.isAnjo) and (not brother.isLider):
            menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'indicado' + brother.id))
    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)

def votacao_casa(message):
    global brothersInGame
    global quantEmparedados

    bot.send_message(message.chat.id, "Agora é com vocês casa, está na hora de votar. Quem vocês querem que vá para o paredão?")
    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        if (not brother.isAnjo) and (not brother.isLider):
            menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'voto' + brother.id))
    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)

    while any(x.votou == False.message.chat.id for x in brothersInGame):
        pass

    brothersInGame.sort(key=lambda x: x.votos, reverse=True)
    desempate1 = list()
    desempate2 = list()
    aux = 0
    bot.send_message(message.chat.id, "Votos: ")
    for brother in brothersInGame:
        if (not brother.isAnjo) and (not brother.isLider):
            if aux == 0:
                desempate1.append(brother.id)
            else:
                if brother.votos == desempate1[0].votos:
                    desempate1.append(brother.id)
                else:
                    if aux == 1:
                        desempate2.append(brother.id)
                    else:
                        if brother.votos == desempate2[0].votos:
                            desempate2.append(brother.id)

            aux += 1
            bot.send_message(message.chat.id, brother.name + ": " + brother.votos)

    if (len(desempate1) == 1 and len(desempate2) == 1) or len(desempate1) == 2:
        brothersInGame[0].viraEmparedado()
        brothersInGame[1].viraEmparedado()
        quantEmparedados += 2

    elif len(desempate1) > 2:
        lider_desempata(message, desempate1)
    else:
        brothersInGame[0].viraEmparedado()
        quantEmparedados += 1
        lider_desempata(message, desempate2)

def lider_desempata(message, listaDesempate):

    bot.send_message(message.chat.id, "Temos um empates de " + len(listaDesempate) + '. O líder irá decidir quem vai para o paredão.')

    menuKeyboard = types.InlineKeyboardMarkup()
    for id in listaDesempate:
        for brother in brothersInGame:
            if brother.id == id:
                menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'desempate' + brother.id))

    bot.send_message(message.chat.id, "Líder,Escolha um: ", reply_markup=menuKeyboard)

def paredao(message):
    global isEvento
    bot.send_message(message.chat.id, "Os emparedados da semana são: ")
    for brother in brothersInGame:
        if brother.isEmparedado:
            bot.send_message(message.chat.id, brother.name + ', ' + brother.nickname)

    bot.send_message(message.chat.id, "Está aberta a votação do público!")

    time.sleep(3)
    isEvento = False


def eliminacao(message):
    global brothersInGame
    global isEvento
    if host == 'thiago':
        bot.send_photo(message.chat.id, random.choice(thiagofotos))
    elif host == 'boninho':
        bot.send_photo(message.chat.id, random.choice(boninhofotos))
    elif host == 'bial':
        bot.send_photo(message.chat.id, random.choice(bialfotos))

    bot.send_message(message.chat.id, "A votação está encerrada!")
    eliminado = random.choice(brothersInGame)
    while not eliminado.isEmparedado:
        eliminado = ramdom.choice(brothersInGame)

    fraseEliminacao = ramdom.choice(allEliminacao)
    fraseEliminacao = fraseEliminacao.replace('JOGADOR1', eliminado.nome)

    bot.send_message(message.chat.id, fraseEliminacao)
    bot.send_message(message.chat.id, eliminado.name + ', ' + eliminado.nickname + ': ' + round(random.uniform(33.4,100), 2) + '% dos votos')

    brothersInGame.remove(eliminado)

    isEvento = False

def reset_stats(message):
    global brothersInGame
    global isEvento

    for brother in brothersInGame:
        brother.acabaLider()
        brother.acabaAnjo()
        brother.acabaSalvo()
        brother.acabaMonstro()
        brother.acabaEmparedado()
        brother.zeraVoto()
        brother.zeraVotou()
        brother.zeraSalvou()
        brother.zeraIndicou()
        brother.zeraMonstrou()
        brother.zeraDesempatou()

    isEvento = False



bot.polling()
