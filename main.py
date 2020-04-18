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
adTime = 30
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
global isFinal
global minBrothers
minBrothers = 5
global isError
isError = False

#lists
global palavroes
palavroes = ['caralho','puta', 'pqp', 'cu', 'buceta', 'pau']
# global gameOrder
# global gameOrderFixed
global brothersInGame
global brothersEliminados
global allHosts
allHosts = ['bial','thiago','boninho']

brothersEliminados = list()
brothersInGame = list()
# gameOrder = list()
# gameOrderFixed = list()
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

thiagoFotos = list()
for foto in glob.glob(THIS_FOLDER + '/img/thiago*.jpg'):
    im = open(foto, 'rb')
    thiagoFotos.append(im)

bialFotos = list()
for foto in glob.glob(THIS_FOLDER +  '/img/bial*.jpg'):
    im = open(foto, 'rb')
    bialFotos.append(im)

boninhoFotos = list()
for foto in glob.glob(THIS_FOLDER +  '/img/boninho*.jpg'): #
    im = open(foto, 'rb')
    boninhoFotos.append(im)

premioFotos = list()
for foto in glob.glob(THIS_FOLDER +  '/img/premio*.jpg'): #
    im = open(foto, 'rb')
    premioFotos.append(im)

class brother():
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.nickname = random.choice(allNicknames)
        self.fullname = str(self.name) + ', ' + str(self.nickname)
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

    def zeraTudo(self):
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



#Handlers

@bot.message_handler(commands=['join'])
def send_join(message):
    global brothersInGame
    if adOnAir:
        if not any(x.id == message.from_user.id for x in brothersInGame):   #erro
            brothersInGame.append(brother(message.from_user.first_name, message.from_user.id))
            bot.send_message(message.chat.id, str(message.from_user.first_name) + ", seja bem-vindo ao BBT!")
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
def send_force_start(message):
    global adOnAir
    adOnAir = False

@bot.message_handler(commands=['start'])
def send_start(message):
    global gameOn
    global gameStarted
    global host
    global isFinal
    global brothersInGame
    if not gameStarted:
        gameStarted = True
        bot.send_message(message.chat.id, "Vai entrar no ar o chat mais vigiado do Brasil! \nLogo após os comerciais de " + str(adTime) + " segundos!\nApertem /join para entrar!")
        call_ad()
        while adOnAir:
            pass
        if len(brothersInGame) >= minBrothers:
            isFinal = False
            gameOn = True
            host = random.choice(allHosts)
            bot.send_message(message.chat.id, "Começando mais uma temporada de Big Brother Telegram, o chat mais vigiado do Brasil!\nSou " + host.title() + ", o seu apresentador essa noite!")
            list_brothers(message)
            entra_fluxo(message)
        gameStarted = False
        brothersInGame = list()
        bot.send_message(message.chat.id, "O número mínimo de " + str(minBrothers) + " brothers não foi alcançado. Quem sabe na próxima ¯\_(ツ)_/¯")
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



# @bot.message_handler(func=lambda message: gameOn, content_types=['text'])
# def palavrao_handler(message):
#     if (any(x in message.text for x in palavroes)):
#         bot.reply_to(message, "Estamos ao vivo, não fale palavrão! Menos 300 estalecas!")


# escolheu o botão certo
@bot.callback_query_handler(lambda query: ('winner' in query.data) and isProva)
def process_callback_win(query):
    global isProva
    global isEvento
    global itensRetirados
    global brothersInGame

    if brothersInGame[0].isLider:
        brothersInGame.append(brothersInGame.pop(0))
    if(query.from_user.id == brothersInGame[0].id):
        brotherGanhador = next(brother for brother in brothersInGame if brother.id == brothersInGame[0].id)
        bot.edit_message_text("Acertou! Acabou a prova! O " + provaDe + " é: 🏆🏆🏆 " + brotherGanhador.fullname + " 🏆🏆🏆", query.message.chat.id, query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        if provaDe == 'líder':
            brotherGanhador.viraLider()
        elif provaDe == 'anjo':
            brotherGanhador.viraAnjo()
        else:
            bot.send_message(query.message.chat.id, "Algo deu errado! Essa prova não é de líder nem de anjo?")
        brothersInGame.append(brothersInGame.pop(0))
        isProva = False
        isEvento = False
        itensRetirados = list()
    else:
        bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

# escolhei o botão errado
@bot.callback_query_handler(lambda query: ('loser' in query.data) and isProva)
def process_callback_lose(query):
    global brothersInGame

    if(query.from_user.id == brothersInGame[0].id):
      brothersInGame.append(brothersInGame.pop(0))
      if brothersInGame[0].isLider:
          brothersInGame.append(brothersInGame.pop(0))
      menukeyboard = retira_item(query.message.chat.id, query.message.message_id, query.data)
      bot.edit_message_text("Errou! Agora é a vez de " + brothersInGame[0].name, query.message.chat.id, query.message.message_id, reply_markup=menukeyboard)
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('salva' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento

    brotherAnjo = next(brother for brother in brothersInGame if brother.isAnjo == True)
    if(query.from_user.id == brotherAnjo.id) and (not brotherAnjo.salvou):
        brotherSalvo = next(brother for brother in brothersInGame if str(brother.id) == query.data.replace('salva',''))
        brotherSalvo.viraSalvo()
        brotherAnjo.jaSalvou()
        bot.edit_message_text( brotherAnjo.name + " salvou " + brotherSalvo.name + "!", query.message.chat.id, query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('monstro' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento

    brotherAnjo = next(brother for brother in brothersInGame if brother.isAnjo == True)
    if(query.from_user.id == brotherAnjo.id) and (not brotherAnjo.monstrou):
        brotherMontro = next(brother for brother in brothersInGame if str(brother.id) == query.data.replace('monstro',''))
        brotherMontro.viraMonstro()
        brotherMontro.jaVotou()
        brotherAnjo.jaMonstrou()
        bot.edit_message_text( brotherAnjo.name + " deu o montro para " + brotherMontro.name + "!", query.message.chat.id, query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('indicado' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento
    global quantEmparedados

    brotherLider = next(brother for brother in brothersInGame if brother.isLider == True)
    if(query.from_user.id == brotherLider.id) and (not brotherLider.indicou):
        brotherIndicado = next(brother for brother in brothersInGame if str(brother.id) == query.data.replace('indicado',''))
        brotherIndicado.viraEmparedado()
        quantEmparedados += 1
        brotherLider.jaIndicou()
        bot.edit_message_text( brotherLider.name + " fez sua escolha. " + brotherIndicado.name + ", você está no paredão!", query.message.chat.id, query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('voto' in query.data) and isEvento)
def process_callback_lose(query):
    if any(x.id == query.from_user.id for x in brothersInGame):
        brotherVotou = next(brother for brother in brothersInGame if brother.id == query.from_user.id)
        if (not brotherVotou.votou) and (not brotherVotou.isMonstro):
            brotherVotou.jaVotou()
            brotherVotado = next(brother for brother in brothersInGame if str(brother.id) == query.data.replace('voto',''))
            brotherVotado.recebeVoto()

@bot.callback_query_handler(lambda query: ('desempate' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento
    global quantEmparedados

    brotherLider = next(brother for brother in brothersInGame if brother.isLider == True)
    if(query.from_user.id == brotherLider.id) and quantEmparedados < 3:
        brotherIndicado = next(brother for brother in brothersInGame if str(brother.id) == query.data.replace('desempate',''))
        brotherIndicado.viraEmparedado()
        quantEmparedados += 1
        bot.edit_message_text( brotherLider.name + " fez sua escolha. " + brotherIndicado.name + ", você está no paredão!", query.message.chat.id, query.message.message_id, reply_markup=types.InlineKeyboardMarkup())
        isEvento = False
    else:
      bot.send_message(query.message.chat.id, "Não é tua vez! Menos 500 estalecas!")

@bot.callback_query_handler(lambda query: ('final' in query.data) and isEvento)
def process_callback_lose(query):
    global isEvento
    if any(x.id == query.from_user.id for x in brothersEliminados):
        brotherVotou = next(brother for brother in brothersEliminados if brother.id == query.from_user.id)
        if (not brotherVotou.votou):
            brotherVotou.jaVotou()
            brotherVotado = next(brother for brother in brothersInGame if str(brother.id) == query.data.replace('voto',''))
            brotherVotado.recebeVoto()


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
    allbrothers = ''
    for brother in brothersInGame:
        allbrothers = allbrothers + brother.fullname + '\n'

    bot.send_message(message.chat.id, allbrothers)

def sorteio_ordem(message):
    global brothersInGame

    random.shuffle(brothersInGame)
    bot.send_message(message.chat.id, "Ordem de jogo: ")
    time.sleep(1)

    allOrdem = ''
    for brother in brothersInGame:
        if (not brother.isMonstro) and (not brother.isLider):
            allOrdem = allOrdem + brother.name + ' | '

    if brothersInGame[0].isLider:
        brothersInGame.append(brothersInGame.pop(0))
    bot.send_message(message.chat.id, allOrdem)


def prova_sorte(message):
    global emoji
    global winner
    global numeroItensProva

    numeroItensProva = random.randrange(len(brothersInGame), 3*len(brothersInGame), len(brothersInGame))
    provaTexto = random.choice(allProvaSorte).replace("GANHADOR", provaDe).replace("NUMERO",str(numeroItensProva))
    emoji = provaTexto[-1]
    bot.send_message(message.chat.id, provaTexto)
    time.sleep(1)
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
    while len(brothersInGame) > 3:
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

    final(message)

#fluxo

def resumo_semana(message):
    global isEvento
    if host == 'thiago':
        bot.send_photo(message.chat.id, random.choice(thiagoFotos))
    elif host == 'boninho':
        bot.send_photo(message.chat.id, random.choice(boninhoFotos))
    elif host == 'bial':
        bot.send_photo(message.chat.id, random.choice(bialFotos))
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
    time.sleep(1)
    global isProva
    global provaDe
    if gameOn:
        isProva = True
        provaDe = provaDeQue
        bot.send_message(message.chat.id, "Vamos começar a prova do " + provaDe + " de hoje!")
        time.sleep(1)
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
    brotherAnjo = next(brother for brother in brothersInGame if brother.isAnjo == True)
    bot.send_message(message.chat.id, "Anjo " + brotherAnjo.name + ", quem você deseja imunizar nessa rodada? ")

    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        if not brother.isAnjo:
            menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'salva' + str(brother.id)))
    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)


def anjo_monstro(message):
    brotherAnjo = next(brother for brother in brothersInGame if brother.isAnjo == True)
    bot.send_message(message.chat.id, "Anjo " + brotherAnjo.name + ", quem você bota de monstro essa rodada?\nLembrando que o montro não participa da votação da casa!")

    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        if not brother.isAnjo:
            menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'monstro' + str(brother.id)))
    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)


def indicacao_lider(message):
    brotherLider = next(brother for brother in brothersInGame if brother.isLider == True)
    bot.send_message(message.chat.id, "Líder " + brotherLider.name + ", está na sua vez. Quem você coloca no paredão?")
    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        if (not brother.isSalvo) and (not brother.isLider):
            menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'indicado' + str(brother.id)))
    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)


def votacao_casa(message):
    global brothersInGame
    global quantEmparedados
    global isEvento

    bot.send_message(message.chat.id, "Agora é com vocês casa, está na hora de votar. Quem vocês querem que vá para o paredão?")
    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        if (not brother.isSalvo) and (not brother.isLider) and (not brother.isEmparedado):
            menuKeyboard.add(types.InlineKeyboardButton(brother.fullname, callback_data= 'voto' + str(brother.id)))
    bot.send_message(message.chat.id, "Escolha um: ", reply_markup=menuKeyboard)

    while any(brother.votou == False for brother in brothersInGame):
        pass

    brothersInGame.sort(key=lambda x: x.votos, reverse=True)
    desempate1 = list()
    desempate2 = list()
    aux = 0
    bot.send_message(message.chat.id, "Votos: ")
    for brother in brothersInGame:
        if (not brother.isSalvo) and (not brother.isLider) and (not brother.isEmparedado):
            if aux == 0:
                desempate1.append(brother.id)
            else:
                if brother.votos == brothersInGame[0].votos:
                    desempate1.append(brother.id)
                else:
                    if len(desempate2) == 0:
                        desempate2.append(brother.id)
                    else:
                        segundoMaisVotado = next(brother for brother in brothersInGame if brother.id == desempate2[0])
                        if brother.votos == segundoMaisVotado.votos:
                            desempate2.append(brother.id)

            aux += 1
            bot.send_message(message.chat.id, brother.name + ": " + str(brother.votos))

    if (len(desempate1) == 1 and len(desempate2) == 1) or len(desempate1) == 2:
        brothersInGame[0].viraEmparedado()
        brothersInGame[1].viraEmparedado()
        quantEmparedados += 2
        isEvento = False

    elif len(desempate1) > 2:
        lider_desempata(message, desempate1)
    else:
        brothersInGame[0].viraEmparedado()
        quantEmparedados += 1
        lider_desempata(message, desempate2)


def lider_desempata(message, listaDesempate):
    global isEvento

    bot.send_message(message.chat.id, "Temos um empates de " + str(len(listaDesempate)) + '. O líder irá decidir quem vai para o paredão.')

    menuKeyboard = types.InlineKeyboardMarkup()
    for id in listaDesempate:
        for brother in brothersInGame:
            if brother.id == id:
                menuKeyboard.add(types.InlineKeyboardButton(brother.name, callback_data= 'desempate' + str(brother.id)))

    brotherLider = next(brother for brother in brothersInGame if brother.isLider == True)
    bot.send_message(message.chat.id, "Líder " + brotherLider.name + ", escolha um", reply_markup=menuKeyboard)
    while quantEmparedados < 3:
        pass

    isEvento = False


def paredao(message):
    global isEvento
    bot.send_message(message.chat.id, "Os emparedados da semana são: ")
    for brother in brothersInGame:
        if brother.isEmparedado:
            bot.send_message(message.chat.id, brother.fullname)

    bot.send_message(message.chat.id, "Está aberta a votação do público!")

    time.sleep(3)
    isEvento = False


def eliminacao(message):
    global brothersInGame
    global isEvento
    global brothersEliminados

    if host == 'thiago':
        bot.send_photo(message.chat.id, random.choice(thiagoFotos))
    elif host == 'boninho':
        bot.send_photo(message.chat.id, random.choice(boninhoFotos))
    elif host == 'bial':
        bot.send_photo(message.chat.id, random.choice(bialFotos))

    bot.send_message(message.chat.id, "A votação está encerrada!")
    eliminado = random.choice(brothersInGame)
    while not eliminado.isEmparedado:
        eliminado = random.choice(brothersInGame)

    fraseEliminacao = random.choice(allEliminacao)
    fraseEliminacao = fraseEliminacao.replace('JOGADOR1', eliminado.name)

    bot.send_message(message.chat.id, fraseEliminacao)
    bot.send_message(message.chat.id, eliminado.fullname + ': ' + str(round(random.uniform(33.4,100), 2)) + '% dos votos')
    eliminado.zeraTudo()
    brothersEliminados.append(eliminado)
    brothersInGame.remove(eliminado)

    isEvento = False


def reset_stats(message):
    global brothersInGame
    global isEvento

    for brother in brothersInGame:
        brother.zeraTudo()

    isEvento = False


def final(message):
    global brothersInGame
    global gameStarted
    global gameOn

    bot.send_message(message.chat.id, "Estamos na final de mais um programa! ")
    bot.send_message(message.chat.id, "Eliminados, agora é vossa vez de participar! Votem em quem você acha que deveria ganhar")
    menuKeyboard = types.InlineKeyboardMarkup()
    for brother in brothersInGame:
        menuKeyboard.add(types.InlineKeyboardButton(brother.fullname, callback_data= 'final' + str(brother.id)))

    while any(brother.votou == False for brother in brothersEliminados):
        pass

    brothersInGame.sort(key=lambda x: x.votos, reverse=True)

    desempate = list()
    aux = 0
    for brother in brothersInGame:
        if (not brother.isSalvo) and (not brother.isLider) and (not brother.isEmparedado):
            if aux == 0:
                desempate.append(brother.id)
            else:
                if brother.votos == desempate[0].votos:
                    desempate.append(brother.id)
            aux += 1

    ganhador = random.choice(desempate)
    bot.send_message(message.chat.id, "O ganhador do Big Brother Telegram 2020 é:  ")
    time.sleep(3)
    bot.send_message(message.chat.id, "🏆🏆🏆 " + ganhador.fullname + " 🏆🏆🏆")
    brothersInGame = list()
    gameStarted = False
    gameOn = False


updates = bot.get_updates()

if updates:
    last_update_id = updates[-1].update_id
    bot.get_updates(offset=last_update_id+1)

# while True:
#     try:
#         bot.polling(interval=10, none_stop=False)
#     except:
#         isError = True

# try:
#     bot.polling(interval=10, none_stop=False)
# except:
#     isError = True

bot.infinity_polling(True)

@bot.message_handler(lambda error: isError)
def error(message):
    bot.send_message(message.chat.id, "Deu erro, time ")
    bot.send_sticker(message.chat.id, "CAADAQADDQADWAABkQe3VH-Hf1l1DAI")
    time.sleep(1)
