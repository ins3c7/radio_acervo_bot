#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# RADIOBOT IRC Bot
# Coded by ins3c7 and Zirou
#
# Coded for Priv8 Server
#
# Thanks xin0x, hc0d3r, HyOgA, idz, chk_, vL, VitaoDoidao, psycco, PoMeRaNo and all the #NOSAFE family.
#
# Let's Rock! ;D
#
#

import json, os, socket, time, base64, sys, threading, random, urllib2, requests
from urllib2 import urlopen
from time import strftime as hr
from datetime import date


reload(sys)
sys.setdefaultencoding('Cp1252')

os.system('clear')

class RadioBot:

	def __init__(self, server, port, nick, name, email, channel, ajoin, admin, prefix, verbose, owner, radioAlive):

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.s.connect((server, port))
		except:
			print 'ERRO: Não foi possível conectar ao HOST: {} e PORTA: {}'.format(str(server),str(port))
			time.sleep(5)
			exit(1)

		time.sleep(0.5)

		self.s.recv(4096)

		self.nick = nick
		self.name = name
		self.email = email
		self.channel = channel
		self.ajoin = ajoin
		self.admin = admin
		self.server = server
		self.prefix = prefix
		self.verbose = verbose

		self.radioAlive = radioAlive
		self.owner = owner

		self.week = str(date(int(hr('%Y')), int(hr('%m')), int(hr('%d'))).isocalendar()[1])

		self.data = ''
		self.command = None
		self.close = False

		self.log_dir = os.path.abspath('log')

		if not os.path.exists(self.log_dir):
			os.mkdir(self.log_dir)

		print '\nInicializando...\n'

	def SendCommand(self, cmd):
		comm = cmd + '\r\n'
		self.s.send(comm)

	def SendMsg(self, canal, msg):
		msg = msg + '\r\n'
		self.s.send('PRIVMSG ' + canal + ' ' + msg + '\r\n')

	def SendPingResponse(self):
		if self.data.find('PING') != -1:
			self.SendCommand('PONG ' + self.data.split()[1])

	def Logging(self, canal, nick, message):
		if canal == self.nick:
			canal = nick
		canal = canal.upper()
		f = open('log/'+ canal +'.log', 'a')
		f.write(message +'\n')
		f.close()

	def _cmp(self, x, y):
		return cmp(x[-1], y[-1])

####################

	def ouvintes(self, banner, canal):
		try:
			hora = hr('%H');dia = hr('%d');mes = hr('%m')
			ouvintes = open('ouvintes/'+dia+mes+'.txt', 'r').readlines()
			nesta_hora = []
			neste_dia = []

			for data in ouvintes:
				data = data.rstrip()
				try:
					neste_dia.append(int(data.split(':')[1]))
				except Exception, e:
					print str(e)
				if data.find(hora+':') != -1:
					try:
						nesta_hora.append(int(data.split(':')[1]))
					except Exception, e:
						print str(e)
			try:
				media_dia = (sum((neste_dia)))/(len(neste_dia))
			except:
				media_dia = 'Ainda não disponível'
			try:
				media_hora = (sum((nesta_hora)))/(len(nesta_hora))
			except:
				media_hora = 'Ainda não disponível'

			self.SendMsg(canal, banner +'0MÉDIA DE OUVINTES0 [ 10HOJE:8 {} 0/10 ÚLTIMA HORA:8 {} 0] '.format(str(media_dia), str(media_hora)))
			
			ouvintes.close()

		except Exception, e:
			ouvintes.close()
			print str(e)


	def mais_tocadas(self, banner, canal):
		try:
			f = open(self.week+'_tocadas.txt','r').readlines()
			dic = {}
			for mus in f:
				mus = mus.rstrip()
				if mus.find('ACERVO') == -1 and mus.find('VINHETA') == -1:
					if mus not in dic:
						dic[mus] = 1
					else:
						dic[mus] += 1
			ord = sorted(dic.items(), self._cmp)[::-1]

			self.SendMsg(canal, banner +'0AS 8TOP 50 DA SEMANA:')
			self.SendMsg(canal, banner +'1.8 {} 0/ {} {}. '.format(ord[0][0], ord[0][1], 'vezes' if int(ord[0][1]) > 1 else 'vez'))
			self.SendMsg(canal, banner +'2.8 {} 0/ {} {}. '.format(ord[1][0], ord[1][1], 'vezes' if int(ord[1][1]) > 1 else 'vez'))
			self.SendMsg(canal, banner +'3.8 {} 0/ {} {}. '.format(ord[2][0], ord[2][1], 'vezes' if int(ord[2][1]) > 1 else 'vez'))
			self.SendMsg(canal, banner +'4.8 {} 0/ {} {}. '.format(ord[3][0], ord[3][1], 'vezes' if int(ord[3][1]) > 1 else 'vez'))
			self.SendMsg(canal, banner +'5.8 {} 0/ {} {}. '.format(ord[4][0], ord[4][1], 'vezes' if int(ord[4][1]) > 1 else 'vez'))
		except Exception, e:
			print str(e)

	def gravar(self, musica):
		f = open(self.week+'_tocadas.txt', 'a')
		f.write(musica+'\n')
		f.close()

	def Radio(self, banner, canal):
		merchan = ['[ 10PARA TOP 5 DA SEMANA: 0Digite 8@top5 0] ', '[10 MUDE SEU APELIDO 4NO CANTO ESQUERDO10 DO CHAT! 0] ', '[ 10 SEJAM VEM VINDOS À RADIO ACERVO! 0] ', ' ', ' ', ' ']
		url = 'http://migre.me/tWKFV'
		old = json.loads(urlopen(url).read())['currentTrack']
		data = urlopen('http://streaming13.brlogic.com:8174/status.xsl').read()
		listeners = data.split('Ouvintes:</td><td class="streamdata">')[1].split('</td>')[0]
		self.SendMsg(canal, banner +'Tocando agora:8 {}0 Ouvintes:8 {}0 {}'.format(old, listeners, random.choice(merchan)))
		
		played = []

		while not self.close:
			new = json.loads(urlopen(url).read())['currentTrack']

			if new != old:
				if new not in played:
					hora = hr('%H');dia = hr('%d');mes = hr('%m')
					ouvintes = open('ouvintes/'+dia+mes+'.txt', 'a')
					ouvintes.write(str(hora)+':'+str(listeners)+'\n')
					ouvintes.close()
					played.append(new)
					self.gravar(new)
					data = urlopen('http://streaming13.brlogic.com:8174/status.xsl').read()
					listeners = data.split('Ouvintes:</td><td class="streamdata">')[1].split('</td>')[0]
					old == new
					if new.find('ACERVO') == -1 and new.find('VINHETA') == -1:
						self.SendMsg(canal, banner +'Tocando agora:8 {}0 Ouvintes:8 {}0 {}'.format(new, listeners, random.choice(merchan)))
					
					if len(played) > 10:
						played = []

			time.sleep(5)

####################

	def Parse(self, banner, canal, user, cmd):
		tmp = cmd.split()
		numargs = len(tmp)
		fmt = []

		if (len(str(cmd).split()) == 0):
			return
			
		command = cmd
		command = command.split()

		# for i in range(numargs):
		# 	fmt.append(tmp[i] + ' ')

		# if user in self.admin:

		########## FUNCOES
		
		if len(command) == 1:
			if canal != self.nick:
				if command[0] == 'help' or command[0] == 'ajuda':
					self.SendMsg(canal, banner + 'Bot under construction...')

			if command[0] == 'rehash':
				if user == self.owner:
					time.sleep(1)
					self.SendCommand('QUIT ... ')
					self.s.close()
					self.close = True
					exit(1)
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')

			if command[0].lower() == 'top5':
				self.mais_tocadas(banner, canal)

			if command[0].lower() == 'ouvintes':
				self.ouvintes(banner, canal)

		else:

			if command[0] == 'join':
				if user in self.admin:
					if command[1][0] == '#':
						join_channel = command[1]
					else:
						join_channel = '#' + command[1]
					self.SendCommand('JOIN %s' % join_channel)
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')

			if command[0] == 'part':
				if user in self.admin:
					if command[1][0] == '#':
						part_channel = command[1]
					else:
						part_channel = '#' + command[1]
					self.SendCommand('PART %s Let\'s Rock!' % part_channel)
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')

	def run(self):

		self.SendCommand('NICK ' + self.nick)
		self.SendCommand('USER ' + self.nick + ' ' + self.name + 
			' ' + self.email + ' :' +
			base64.b16decode(''))

		joined = False
		self.radioAlive = False

		version_check = False

		while not self.close:

			self.data = self.s.recv(4096)
			
			if self.verbose:
				print self.data

			if str(self.data).find('VERSION') != -1:
				exit(1)

			self.SendPingResponse()
			
			time.sleep(0.5)
			
			if str(self.data).find(str(base64.b16decode(''))) != -1:
				print '\nServer [{}] - CONNECTED! Thank\'s to use RADIO BOT!\n'.format(self.server)
				self.SendMsg(str(base64.b16decode('')), str(base64.b16decode('')))
			if str(self.data).find(str(base64.b16decode(''))) != -1:
				self.s.send('{}'.format(base64.b16decode('')) + '\r\n')
			if str(self.data).find(str(base64.b16decode(''))) != -1:
				self.s.send('JOIN {}\r\n'.format(self.channel))
				joined = True
				for channel in ajoin:self.s.send('JOIN {}\r\n'.format(channel))

			if str(self.data).find('JOIN :') != -1:
					nickjoin = self.data.split('!')[0].lstrip(':')
					if nickjoin.find('Radio') == -1:
						self.s.send('MODE #RadioAcervo +v {}\r\n'.format(nickjoin))
					if nickjoin.find(base64.b16decode('')) != -1:
						self.s.send(base64.b16decode('')+'\r\n')

			if str(self.data).find('PRIVMSG') != -1: # Confere se o dado recebido foi uma mensagem private ou para algum canal
				
				msg_time  = time.strftime('%H:%M:%S')		# Define a hora da mensagem
				user_nick = self.data.split('!')[0][1:] 	# Filtra o nick
				try:
					user_host = self.data.split()[0].split('@')[1] # Tenta filtrar o host (Variável ainda não usada)
				except:
					pass
				
				pre_user_msg	= self.data[1:].split('PRIVMSG')[1].split()[1:]	# Trabalha a mensagem bruta
				user_msg 		= ' '.join(pre_user_msg).lstrip(':') 					# Filtra apenas a mensagem
				user_channel 	= str(self.data.split('PRIVMSG')[1].split()[0])	# Filtra o canal

				print '[%s] %s %s: %s' % (str(msg_time), str(user_channel), str(user_nick), str(user_msg)) # Imprime a mensagem na tela do bot

				text_log = '[{}] {}: {}'.format(str(msg_time), str(user_nick), str(user_msg)) # Filtra o a mensagem para a função Logging()

				
				self.Logging(str(user_channel), str(user_nick), str(text_log)) # Grava os logs

				# Banner oficial:

				try:
					if (str(user_msg)[0] == str(self.prefix)):
						self.Parse(banner, user_channel, user_nick, user_msg.lstrip(str(self.prefix)))
				except:
					continue
			
			banner = '14,1[7'+ '#RadioAcervo' +'14]0 '
			
			rbot = threading.Thread(target=self.Radio, args=(banner, '#RadioAcervo'))
			
			if not self.radioAlive and joined:
				try:
					self.radioAlive = True
					rbot.start()

				except Exception, e:
					print str(e)
					self.SendMsg('ins3c7', 'THREADINGS START: '+ str(e))
				except KeyboardInterrupt:
					print 'INTERROMPIDO PELO USUÁRIO'
					self.close = True



#			self.SendCommand('NICK ' + self.nick)

			
if __name__ == '__main__':

	servidor = 'irc.priv8.jp'
	porta = 6667
	nick = 'RadioAcervo'
	nome = 'Coded by #NoSafe/Team - http://NoSafe.Priv8.jp'
	email = 'radiobot@priv8.jp'
	canal_principal = '#RadioAcervo' # Canal de comando do bot
	ajoin = [canal_principal,]
	owner = 'ins3c7'
	admin = ['ins3c7'] # Nicks para acessos à funções especiais do bot
	prefix = '@'
	verbose = False
	radioAlive = False

bot = RadioBot(servidor, porta, nick, nome, email, canal_principal, ajoin, admin, prefix, verbose, owner, radioAlive)
bot.run()
