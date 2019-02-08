#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
# #-*- coding: utf-8 -*-
import socket
import sys
import time
import hashlib
import random
import time
import re

from threading import Thread
from threading import RLock

import util

from util.common        import *
from util.Mylog         import *
from util.Outputdevice  import *
from util.MessageHolder import *
from util.TCPConnection  import *
from util.Protocol       import *
from core.Symbol         import *
#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------   
#---------------------------------------------------------------------------      
#
#---------------------------------------------------------------------------      
def client_close() :
   """
      Cette fonction est activee lorsque le signal SIGINT est intercepte.
      Elle est passive si le mode de jeu definie dans la classe Protocol 
      n'est ni 'permier' ni 'client'.
      
      Dans le cas contraire, l'une des fonctions premier_tracker_print ou 
      client_tracker_print est appelee.
   
   """
   print("\n*** Mode serveur= {}\n".format(Protocol.CURRENT_MODE))
   if Protocol.CURRENT_MODE is 'premier' :
      fileName = "log/premier_calltrack_sorted.txt"
      tracker_print(oDictionnaireOrdonne, fileName)

   elif Protocol.CURRENT_MODE is 'client' :
      fileName = "log/client_calltrack_sorted.txt"
      tracker_print(oDictionnaireOrdonne, fileName)

   elif Protocol.CURRENT_MODE is 'server' :
      pass
   else :
      pass
   sys.exit(0)
#---------------------------------------------------------------------------      
   
#---------------------------------------------------------------------------      

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------      
def test_Protocol_process(self,message) : 
   """
      Traite le message passe en argument.
   """
   oProtocol = Protocol()
   message   = oProtocol.messageProcess(message)
   return message
   
#---------------------------------------------------------------------------



#-----------------------------------------------------------------------------
class Protocol(Outputdevice, Thread, Mylog) :
   """ 
   Cette classe implemente le protocole de communication entre les objets 
   qui heritent de cette classe.
   
   Elle definie les champs du protocole de communication et interprete ces champs.

   Cette classe delivre ses services selon 3 modes : 
   -> le mode serveur
   -> le mode client, 
   -> le mode premier.
   
   * En mode serveur, l'instance ce cette classe attend et traite les commandes de controle envoyees par des
   clients sur le reseau.

   * En mode client, l'instance de cette classe envoie des commandes de controle au serveur et recoit les 
   reponses du serveur.

   * En mode premier, la communication entre le joueur et le jeu est celle de la premiere version du jeu 
   du labyrinthe. Cette version supporte de poser des murs et percer des portes.
      
   En mode client ou serveur, ces objets sont actifs dans un thread. Pour ce faire, cette classe herite 
   de la classe Thread.   
   """


   MODE           = {}
   MODE["client"] = "client"
   MODE["server"] = "server"
   MODE["premier"]= "premier"
   
   # Expression reguliere pour tester une commande de jeu.
   REGEXP_PLAYMOOVE  = r"^[nNeEsSoOuUdD][0-9]*$"
   # Expression reguliere pour tester une commande de controle.
   REGEXP_PLAYACTION = r"^[pPmMxX][nNeEsSoOuUdD]$"

   REGEXP_CTRLCMD    = r"^[cCkKnNhH?qQtT0wW][a-zA-Z0-9#@&_]*$"
   _zeroPosition  = [0,0,0]
   PLAY           = 'play'
   PLAY_DIRECTIONS= ('R','N','E','S','O','U','D')
   PLAY_ACTIONS   = ('M','P','X')
   
   CTRL               = 'ctrl'
   CTRL_ACTIONS_GET   = 'G'
   CTRL_ACTIONS_SET   = 'S'
   CTRL_ACTIONS_START = 'C'
   CTRL_ACTIONS_LEAVE = 'Q'
   CTRL_ACTIONS_TCHAT = 'T'
   CTRL_ACTIONS_HALT  = '0'
   CTRL_ACTIONS_PASSWD= 'E'
   CTRL_ACTIONS_WIN   = 'W'

   CRTL_ACTIONS   = (CTRL_ACTIONS_GET, CTRL_ACTIONS_SET, CTRL_ACTIONS_START, CTRL_ACTIONS_LEAVE, CTRL_ACTIONS_TCHAT, CTRL_ACTIONS_HALT, CTRL_ACTIONS_PASSWD, CTRL_ACTIONS_WIN)
   CTRL_PARTY     = 'party'
   CTRL_CARTE     = 'carte'
   
   CMDPARTY       = ('C','F','Q')
   CMDDATA        = ('CARTE',)
      
   CLIENT_MODE = 'client'
   SERVER_MODE = 'server'
   PREMIER_MODE = 'premier'
   CURRENT_MODE = None
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __init__(self, symbol=None, oReceiver=None, mode=None, debug=False,  serverAddress=None, isAuto=False) :
      """
      Initialise l'objet en enregistrant le receveur de messages passe en parametre.
      Le symbole passe en parametre identifie la source de communication, i.e l'objet qui 
      envoie le message.
      Parametres : 
         oReceiver le recepteur des messages
         symbol    : la source des messages.
         mode      : client, server, None (version premiere du robot)       
      """
      Outputdevice.__init__(self)
      Thread.__init__(self)
      Mylog.__init__(self, debug=debug)

      if oReceiver is None :
         #L'objet s'envoie des messages
         self._oReceiver   = self
      else :
         self._oReceiver   = oReceiver
         
      self._directions   = Protocol.PLAY_DIRECTIONS
      self._symbol       = symbol
      self._help         = 'H'      
      self._mode         = mode
      Protocol.CURRENT_MODE = mode
      self._isConnected  = False
      self._isActivated  = False
      self._server       = None
      #self._debug        = debug
      self._isServerHalt = False
      self._lastCommand  = None
      self._isAutoRecord = isAuto
      
      host = None
      port = None
      self.initAddress(serverAddress)
      
      # Attribut utilise en mode serveur
      self.oLabyrinthRequestHandler = None

      # En mode serveur ou client, l'objet sera actif dans un thread.
      if (Protocol.MODE["server"] == self._mode) or (Protocol.MODE["client"] == self._mode):
         Thread.__init__(self)
      else :
         # Version premiere du robot on mode client
         pass
         
      #Identifiant de session unique pour ce joueur sur le reseau
      id       = int(random.random()*1E16)
      byteId   = bytes(str(id),'utf-8')
      hashId   = hashlib.md5(byteId)
      self._id = hashId.hexdigest()
      
      # Choix du symbole
      
      self.mylog("\n*** Protocol.__init__() : symbol= {} / mode= {} / debug={} /ID= {} / Address={} ".\
      format(self._symbol, self._mode, debug, self._id, self._serverAddress))

   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def initAddress(self, serverAddress) :
      self.mylog("\n Server Address = {}".format(serverAddress))
      
      if serverAddress is None : 
         self._serverAddress = TCPConnection.SERVER
      else :
         if serverAddress[0] is None :
            host = TCPConnection.HOST 
         else :
            host = serverAddress[0]
            
         if serverAddress[1] is None :
            port = TCPConnection.PORT
         else :
            port = serverAddress[1]
         
         self._serverAddress = (host,port)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def handlerRegister(self,tcpHandlerMethods) :
      """
         Cette methode est utilisee en mode 'server' pour instancier un serveur 
         supportant le protocole TCP.
         Elle construit une classe dont la methode 'handle' prendra en charge 
         les requetes des clients faites au serveur TCP.
         
         Parametres
         ----------
           * tcpHandlerMethods : dictionnaire des methodes de la classe creee.
           Ce dictionnaire est definie dans le module qui creer une instance de 
           cette classe.
           
      """
      if Protocol.MODE["server"] == self._mode :
         self.oLabyrinthRequestHandler = type("LabyrinthRequestHandler",(BaseRequestHandler,),tcpHandlerMethods)
      
   #---------------------------------------------------------------------------
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)   
   def _messageReplyBuild(self, command) :
      status, formatedCommand = self._format(command)
      

      ctlcmd = (self._symbol,formatedCommand[0],formatedCommand[1])

      message              = dict()
      message['id']        = self._id
      message['ctlcmd']    = ctlcmd
      message['timestamp'] = time.time() 
      return message
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)   
   def _messageBuild(self, gameCmd) :
      """
         Construit un message de jeu qui sera transmis sur le reseau TCP.
         Cette construction consiste a encapsuler le parametre gameCmd (la payload) 
         dans un message compose comme suit : 
         
         * {'timetamp':value, 'id':value, 'payload':gameCmd}
         Retour : 
         ------
            * Le message construit
            
      """
      message              = dict()
      message['id']        = self._id
      message['timestamp'] = time.time() 
      message['payload']   = gameCmd
      return message
      
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)   
   @server_method_tracker(TRACKFLAG)   
   def buildHeader(self, status, notification, iddest) :
      """
         Contruit l'entete du message a retourner au client.
         Cet entete a pour format : 
         {'iddest': value, 'timestamp': value, 'status': value, 'notify':value,'timestamp':value}
      """
      replyMessage = dict()
      replyMessage['status']    = status
      replyMessage['notify']    = notification
      replyMessage['id']        = self._id
      replyMessage['iddest']    = iddest
      replyMessage['timestamp'] = time.time()
      
      return replyMessage
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)   
   def run(self) :
      """
         C'est la fonction principale du thread pour un objet instantie en mode serveur TCP.

         En mode serveur : le serveur est active et attend les requetes des clients.
         Lorsqu'une reqete arrive sur le serveur, elle est pris en charge par la fonction 
         self.oLabyrinthRequestHandler.

         En mode client  : rien ne se passe.
      """
      if Protocol.MODE["server"] == self._mode :
         if self._isActivated is False :
            self.mylog("\n\n*** Server : activation ...")
            self._server = socketserver.TCPServer(Protocol.SERVER, self.oLabyrinthRequestHandler)
            #self._server.allow_reuse_address = True
            self._isActivated = True
            self.mylog("*** Server : Activated!\n")

         # Les serveur se met en attente de messages des clients
         self._server.serve_forever()

         # Les serveur est desactive
         self.mylog("*** Server : Leaving...")
         
      elif Protocol.MODE["client"] == self._mode :
         pass
      else :
         # Version premiere du robot
         pass
   #---------------------------------------------------------------------------
   
      
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)   
   def _format(self, command, symbol= None) :
      """ 
      Formate la commande du joueur passee en parametre en 
      un dictionnaire interpretable par le jeu.
      
      La commande formatee, si elle est valide, constituera la payload du message.
      
      Deux types de commandes sont traitees :
      * Les commmandes de jeu, qui permettent de deplacer un robot et d'actionner des obstacles.
      * Les commandes de controle, qui ne participent pas au jeu.
        Les commandes de tchat, plus omplexes,  sont traitées quelque peu differament 
        des autres commandes de controle.

      Parametres : 
      -----------
      command : une chaine de caracteres entree par le joueur.
      
      Retour :
      ------
         Un dictonnaire formate comme suit : 
         * Format de la commande de jeu :
            {'play':None}   en cas d'erreur
            {'play':{'moove' :(symbol,value,direction)}} pour jouer un deplacement 'value'
            {'play':{'action':(symbol,value,direction)}} pour jouer une action 'value'

         * Format de la commande de controle :
            {'ctrl':None}   en cas d'erreur
            {'ctrl':(symbol_s,value,symbol_d)} ou 
               * symbol_s symbole source
               * value est 'g' ou 's', 
               * symbol_s symbole destination
            {'ctrl':(symbol_s,value,symbol_d, message)} ou 
               * symbol_s symbole source
               * value est 'g' ou 's', 
               * symbol_s symbole destination
               * message est un message a destibation du symbole symbol_s
         
      """
      status    = False
      
      jump      = 0
      direction = ''
      action    = ''
      fmtCmd={'play':None}
      
      length = len(command)

      # Commande vide
      if 0 >= length :
         return status, fmtCmd

      
      if re.match(Protocol.REGEXP_PLAYMOOVE, command):
         #------------------------------------------------
         # Formatage d'un deplacement
         #------------------------------------------------
         direction = command[0]

         #Calcul du saut
         if 1 == length:
            # Saut de 1 dans la direction
            jump = 1
         else :
            listJump = command.split(direction)
            strJump  = listJump[1]
            jump = int(strJump)
         fmtCmd = {'play':{'moove':(self._symbol,jump,direction.capitalize())}}
         status = True
      elif re.match(Protocol.REGEXP_PLAYACTION,command) :      
         #------------------------------------------------
         # Formatage d'une action
         #------------------------------------------------
         action    = command[0]
         direction = command[1]
         fmtCmd = {'play':{'action':(self._symbol,action.capitalize(),direction.capitalize())}}
         status = True
      elif re.match(Protocol.REGEXP_CTRLCMD,command) :
         #------------------------------------------------
         # Formatage d'une commande de controle 
         #------------------------------------------------
         if '?' == command[0] :
            # Commande de recuperation de la carte
            fmtCmd = {'ctrl':(self._symbol, Protocol.CTRL_ACTIONS_GET.capitalize(), self._symbol)}
            status = True

         elif Protocol.CTRL_ACTIONS_LEAVE == command[0].capitalize() :
            # Commande pour informer le serveur qu'un joueur quitte le jeu.
            fmtCmd = {'ctrl':(self._symbol, Protocol.CTRL_ACTIONS_LEAVE.capitalize(), self._symbol)}
            status = True

         elif Protocol.CTRL_ACTIONS_START == command[0].capitalize() :
            # Commande pour informer le serveur qu'un joueur quitte le jeu.
            fmtCmd = {'ctrl':(self._symbol, Protocol.CTRL_ACTIONS_START.capitalize(), self._symbol)}
            status = True
         elif Protocol.CTRL_ACTIONS_HALT == command[0].capitalize() :
            # Commande pour informer le serveur que le joueur quitte le jeu.
            if len(command) <= 1 :
               fmtCmd = {'ctrl':None}                  
               status = False
            else :
               fmtCmd = {'ctrl':(self._symbol, Protocol.CTRL_ACTIONS_HALT, command, Symbol._symbolLabyrinth)}
               status = True

         elif Protocol.CTRL_ACTIONS_WIN == command[0].capitalize() :
            # Commande pour informer le serveur que le joueur gagne; pour les tests unitaires seulement.
            if len(command) <= 1 :
               fmtCmd = {'ctrl':None}                  
               status = False
            else :
               fmtCmd = {'ctrl':(self._symbol, Protocol.CTRL_ACTIONS_WIN, command, Symbol._symbolLabyrinth)}
               status = True
         else :
            fmtCmd = {'ctrl':None}                  

      elif command.startswith(Protocol.CTRL_ACTIONS_TCHAT.lower()) or \
           command.startswith(Protocol.CTRL_ACTIONS_TCHAT.capitalize()) :
         #------------------------------------------------
         # Formatage d'une commande de tchat
         # La commande est splitee en un tuple (t<symbol>, " ", message)
         #------------------------------------------------
         self.mylog("*** INFO : _format(): command= {}".format(command))
         
         splittedCommand = command.split(" ")
         
         if len(splittedCommand) >= 3 :         
            tchatCommand = splittedCommand.pop(0)
            destSymbol   = splittedCommand.pop(0)
            
            # Le messafe est reconstitue 
            message = " ".join(splittedCommand)
            self.mylog("*** INFO : _format(): Command= {} Symbol= {} Message= {}".\
            format(tchatCommand, destSymbol, message))

            # Commande de tchat que le serveur redistribuera 
            fmtCmd = {'ctrl':(self._symbol, Protocol.CTRL_ACTIONS_TCHAT.capitalize(), destSymbol, message)}
            status = True
         else :
            status = False

      else :
         # Commande incorrecte
         self.setOutput("*** ERREUR : commande invalide : \"{}\"\n".format(command))

      return status, fmtCmd
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def send(self, command) :
      """ 
      Envoie a un recepteur une commande du joueur.
      Selon le mode de creation de cet objet, la commande de jeu sera 
      envoyee selon la version premiere ou selon la version reseau du jeu.

      Parametres
      ----------
         controlCmd : la commande de controle a envoyer formatee comme 
                      (symbol, saut, direction)

      Retour
      ------
         message : message retourne par le recepteur. 
                   En version reseau, si l'envoie a reussi, retourne None.
      """
      # Enregisttrement de la derniere commande, utilisee quand le  joueur quitte 
      # le jeu et faire changer l'etat du joueur.
      self._lastCommand = command.capitalize()
      self.mylog("*** send() : command before = {}".format(command))
      
      # La commande est formatee
      status, gameCmd = self._format(command)
      self.mylog("*** send() : Game command after  = {} / Status= {}".format(gameCmd, status))
      
      if status is False : 
         # Construction du message retourne
         return {'status':status,'notify':"Format de la commande= \""+command+"\" invalide!"}
      
      #
      # Encapsulation de la payload avec les parametres communs du message 
      # Le message contient une commande de jeu a destination du serveur.
      # {'play': {'action': (symbol, action, direction)}}
      # ou 
      # {'play': {'moove': (symbol, jump, direction)}}
      # ou 
      # 
      # {'ctrl': {'payload':{'state':value, 'notify':value, 'playstatus':value}}}
      #
      message = self._messageBuild(gameCmd)

      # Envoi du message : 
      if self._mode is 'premier' :
         # Envoi en version premiere du jeu.
         message = self._send_primaryVersion(message)
      else :
         # Envoi sur le reseau et recuperation du message retourne par le serveur
         message = self._send_networkVersion(message)
      
      # L'identite du message est verifie
      
      return message

   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def _send_primaryVersion(self, message) :
      """ 
      Envoie au recepteur enregistre dans cet objet un message.
      Parametres
      ----------
         message : le message a envoyer

      Retour
      ------
         message : la reponse du recepteur
      """

      message = self._oReceiver.receive(message)

      return message
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @client_method_tracker(TRACKFLAG)   
   def receive(self,message) : 
      """
         Recoit d'un emetteur un message.
         Le message est tranfere au recepteur pour traitement.
      """      
      message = self._oReceiver.messageProcess(message)
      return message
      
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @client_method_tracker(TRACKFLAG)   
   def messageProcess(self,message) : 
      """
         Traitement du message envoye par l'emetteur.
         Verifie la conformite du message passe en parametre.
         
         Retour
         ------
            Le message passe en parametre si ce dernier est conforme.
            Dans le cas contraire, un message construit pour la circonstance 
      """      
      replyMessage = dict()

      # Verification du message
      status, notification = self.messageCheck(message)

      # Construction du message de retour
      if status is False :
         replyMessage['status'] = False
         replyMessage['notify'] = notification
      else : 
         self.mylog("\n messageProcess() : message= {}".format(message))
         if 'ctrl' in message['payload'] :
            ctrlCmd = message['payload']['ctrl']
            status, notification = self.process(ctrlCmd)
         else :
            if 'moove' in message['payload']['play'] :
               gameCmd = message['payload']['play']['moove']
               status, notification = self.process(gameCmd)
               
            elif 'action' in message['payload']['play'] :
               gameCmd = message['payload']['play']['action']
               status, notification = self.processAction(gameCmd)
               
            else :
               notification = "\n*** ERROR : messageProcess() : Unknown command : {}".format(message)
               self.mylog(notification)
               replyMessage['status'] = False
               replyMessage['notify'] = notification
               return replyMessage

         self.mylog("\n messageProcess() : Returned message= {}".format((status,notification)))
         replyMessage['status'] = status
         replyMessage['notify'] = notification


      return replyMessage
      
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @client_method_tracker(TRACKFLAG)   
   def process(self,message) :
      status       = True
      notification ="Stub"
      return status, notification
   #---------------------------------------------------------------------------      
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @client_method_tracker(TRACKFLAG)   
   def processAction(self, message) :
      status       = True
      notification ="Stub"
      return status, notification
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @client_method_tracker(TRACKFLAG)   
   def messageCheck(self,message) :
      """
         Verifie la conformite du message passe en parametre.
         La verification procede comme suit: 
          * Les parametres commnuns a tous les messages sont verifies.
          * Ensuite, selon le type de message : 
            * La conformite du message a un message de jeu est verifiee
            * La conformite du message a un message de controle est verifiee

         Retourne le tuple : 
            * (True,  notification) si le message est conforme
            * (False, notification) si le message n'est pas conforme

         Format d'un message envoye au serveur: 
           {'timestamp' :value, 
            'id'        :value, 
            'status'    :value,
            'payload'   :{'moove':(symbol, jump, direction)}}

           {'timestamp' :value, 
            'id'        :value, 
            'status'    :value,
            'payload'   :{'action':(symbol, action, direction)}}

           {'timestamp' :value, 
            'id'        :value, 
            'status'    :value,
            'payload'   :{'ctrl':(symbol, action, symbol)}}

         Format d'un message recu par le serveur: 
           {'timestamp' :value, 
            'id'        :value, 
            'iddest'    :value, 
            'status'    :value,
            'notify'    :value,
            'payload'   :{'carte':data,'notify':notification,'playstatus':playStatus}}
      """
      
      status                 = True      
      notification = "Invalid message :"

      # Le message doit etre de type dictionnaire.
      if common_isValidType(message,'dict') is False :
         notification += " No dict type / "
         notification += " Message= {}".format(message)
         return False, notification
            
      #
      #  Verification des parametres communs a tous les messages
      #
      if 'timestamp' in message : 
         timestamp = message['timestamp']
      else :
         status = status and False
         notification += " No timestamp in message / "

      if 'id' in message : 
         id = message['id']
      else :
         status = status and False
         notification += " No id in message / "

      if 'iddest' in message : 
         # C'est un message retourne par le serveur; verification du destinataire
         if self._id !=  message['iddest'] :
            #Le message n'est pas adresse a ce destinataire
            notification += " Invalid destination / "
            notification += " Message= {}".format(message)
            status = False
         else :
            # Un message du serveur conforme au protocole transporte les champs 'notify' et 'status'
            if 'status' not in message : 
               status = status and False
               notification += " No status in message / "

            if 'notify' not in message : 
               #status = status and False
               notification += " No notification in message / "

            # Le message est conforme au protocole : verification de la valeur du status 
            if message['status'] is False :
               status = False
               if 'notify' in message :
                  notification = message['notify']
               else :
                  notification = 'ERREUR serveur inconnue'                  
            else :
               #
               # Verification de la payload      
               # Cette section devrait se trouver 
               if 'payload' in message :
                  statusChecked, checkedNotification = self._formatCheck(message['payload'])
                  status = status and statusChecked
                  notification += checkedNotification
               else :
                  status = status and False
                  notification += " No payload in message/ "
      else :
         if 'payload' in message :
            statusChecked, checkedNotification = self._formatCheck(message['payload'])
            status = status and statusChecked
            notification += checkedNotification
         else :
            status = status and False
            notification += " No payload in message/ "
         
      if status is True :
         notification = None
         
      self.mylog("\n*** INFO : messageCheck() : return= {}".format((status,notification)))
      return status, notification
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @client_method_tracker(TRACKFLAG)   
   def _formatCheck(self,gameCmd) :
      """
         Verifie la conformite de la commande passee en parametre.
         La commande passe en parametre peut etre une commande de jeu ou une commande 
         de controle.
         
         Exemple de commande de jeu conforme : 
           * playCmd= {'moove' : ('X', 1, 'N')} pour un deplacement sur la carte .
           * playCmd= {'action': ('X', M, 'S')} pour une action sur la carte.

         Exemple de commande de controle conforme : 
           * ctrlCmd= {'ctrl': ('X', M, 'S')} A definir

         Retour :
         --------
         * (True,  gameCmd)      si la commande est conforme.
         * (False, notification) dans le cas contraire.
      """      
      status       = True 
      notification = "Invalid format:"

      self.mylog("\n\n*** INFO : _formatCheck() : Commande de jeu= {}".format(gameCmd))
      
      if gameCmd is not None :
         if 'play' in gameCmd :
            # Verification du format d'une commande de jeu
            playCmd  = gameCmd['play'] 
            if 'moove' in playCmd :
               mooveCmd = playCmd['moove']
               
               symbol    = mooveCmd[0]
               
               # Le symbole doit etre une lettre
               if (common_isValidType(symbol,'str') is False) or (1 != len(symbol)) :
                  status = status and False
                  notification += " Invalid symbol= {}/ ".format(str(symbol))

               # La commande du joueur est reconstituee et testee
               jump      = mooveCmd[1]
               strJump   = str(jump)
               direction = mooveCmd[2]
               command   = direction+strJump
               if not re.match(Protocol.REGEXP_PLAYMOOVE,command) :
                  status = status and False
                  notification += " Invalid playing moove= {} / ".format(command)
            elif 'action' in playCmd :
               actionCmd = playCmd['action']
               action    = actionCmd[1]
               direction = actionCmd[2]
               command   = action+direction
               if not re.match(Protocol.REGEXP_PLAYACTION,command) :
                  status = status and False
                  notification += " Invalid playing action= {} / ".format(command)
            else :
               status = status and False
               notification += " Unknown play command= {} / "+format(playCmd)
         elif 'ctrl' in gameCmd : 
            ctrlAction      = gameCmd['ctrl']
            self.mylog("\n\n*** INFO : _formatCheck() : Commande de control= {}".format(ctrlAction))
            srcSymbolAction = ctrlAction[0]
            action          = ctrlAction[1]
            dstSymbolAction = ctrlAction[2]
            if (action in Protocol.CRTL_ACTIONS) or (action[0] in Protocol.CRTL_ACTIONS):
               status = status and True
            else : 
               status = status and False
               notification += " Invalid control action= {}".format(ctrlAction)
         # Test du message renvoye par le serveur
         elif ('notify' in gameCmd) and ('playstatus' in gameCmd) :
            #C'est un message renvoye par le serveur; la payload sera traitee par le client
            status = status and True
         else :
            status = status and False
            if 'notify' not in gameCmd :
               notification += " No notify /"      
            if 'playstatus' not in gameCmd :
               notification += " No playstatus /"      
      else :
         status = status and False
         notification += " Empty content for play command= {} / "+format(gameCmd)
         
      return status, notification
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)   
   def _send_networkVersion(self, message) :
      """ 
      Etablit une connection avec le serveur de jeu si cette derniere n'existe pas.
      Envoie au serveur une commande de contrôle.
      Le message est serialise puis envoye au serveur.
      La fonction attend la reponse du serveur et retourne les donnees renvoyees par le serveur.

      Parametres
      ----------
         message : le message a envoyer au serveur

      Retour
      ------
         message : le message retourne par le serveur.
      
      """
      messageLength = len(message)
      notification  = "0"
      if(0 < messageLength) :   
         self.mylog("\n\n*** Protocol._send_networkVersion() : message= {}".format(message))

         if self._isConnected is False :
            self._isConnected, notification = self._serverConnect()
            
         if self._isConnected is True :  
            # La commande de controle est creee.
            oMessageHolder = MessageHolder(None, message,"")
            
            # La commande de controle est serialisee avant d'etre transmise au serveur.
            serializedData = oMessageHolder.serialized()

            # La requete est transmise au serveur
            if 0 < len(serializedData) :
               self._clientConnection.sendall(serializedData)
               return None
            else :
               message = dict()
               notification = "*** ERROR : serialized data length to be sent = {}".format(len(serializedData))
               message['status'] = False
               message['notify'] = notification
         else : 
            message = dict()
            message['status'] = False
            message['notify'] = notification
            
      else :      
         message = dict()
         message['status'] = False
         message['notify'] = "Invalid message to transmit: len= {}".format(messageLength)

      self.mylog("\n\n*** Protocol._send_networkVersion() : Received from server : message= {}".format(message))
      return message
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)   
   def receive_networkVersion(self) :
      """
      Cette methode se met en attente de reception d'un message TCP.
      Le message ercu est verifie conforme au protocole.
      
      Retour : 
      * le message recu en cas de succes
      * un message d'erreur dans le cas contraire
      """
      # Attente de reception de la requete 
      try :
         receivedData = self._clientConnection.recv(TCPConnection.MAXDATALENGTH)
      except ConnectionResetError :
         #---------------------------------------------------------------------
         # Fermeture de la connection avec le serveur.
         #---------------------------------------------------------------------
         self.mylog("\n*** ERROR : Connection reset from server side  ")
         self._clientConnection.close()
         message = dict()
         notification = "*** ERREUR : La connection a ete fermee par le serveur"
         message['status'] = False
         message['notify'] = notification
         return message

      if 0 < len(receivedData) :
         #---------------------------------------------------------------------
         # Les donnees recues par le serveur sont deserialisees
         #---------------------------------------------------------------------
         oMessageHolder = MessageHolder(None, receivedData,"")
         oMessageHolder = oMessageHolder.deserialized(receivedData)

         if 0 < len(oMessageHolder._data) :
            #---------------------------------------------------------------------
            # Le message est recupere
            #---------------------------------------------------------------------
            message = oMessageHolder.data
            self.mylog("\n*** Received message= {} ".format(message))
            
            #---------------------------------------------------------------------
            # Verification du message recupere du serveur
            #---------------------------------------------------------------------
            status, notification = self.messageCheck(message)
            
            #---------------------------------------------------------------------
            # Construction du message de retour en cas de non conformite du message recu
            #---------------------------------------------------------------------
            if status is False :
               message = dict()
               message['status'] = False
               message['notify'] = notification

         else :
            message = dict()
            notification = "*** ERROR : Empty content received!"
            message['status'] = False
            message['notify'] = notification
      else : 
         message = dict()
         notification = "*** ERROR : Empty message received! Length= {}".format(len(receivedData))
         self.mylog(notification)
         message['status'] = False
         message['notify'] = ""

      return message   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @client_method_tracker(TRACKFLAG)   
   def _serverConnect(self) :
      """
       Creer une connexion avec le serveur.
       Si la connexion est deja etablie, la methode retourne True.
       Si la connexion echoue apres deux tentatives, la methode retourne False.
       Une pause de quelques secondes est faite entre deux tentatives.
      """ 
      
      count        = 0
      status       = False
      notification = "*** Connexion KO!"
      
      if self._isConnected is False :
         if Protocol.MODE["client"] == self._mode :
            while self._isConnected is False and count < 2: 
               try :
                  # Mode client : connexion avec le serveur du jeu.
                  self._clientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                  self.mylog("\n*** Connexion au server = {}".format(self._serverAddress))
                  self._clientConnection.connect(self._serverAddress)
                  self._isConnected = True
                  self._clientConnection.setblocking(1)
                  #self._clientConnection.settimeout(None)
                  
                  notification ="***Connexion OK!" 
                  self.mylog("\n{}".format(notification))
               except ConnectionRefusedError as strConnectionRefusedError:
                  notification ="***Connection en cours...!" 
                  self.mylog("\n{}".format(notification))
                  self._clientConnection.close()
                  time.sleep(2)
                  count += 1
      else : 
         notification = "***Connexion OK!"
         self.mylog("\n{}".format(notification))

      # Test si la connexion a reussie 
      if self._isConnected is False :
         status       = False
         notification = "Echec de connexion au serveur!"
      
      self.mylog("\n_clientConnection() :  {} status= {}".format(notification,self._isConnected))   
      return self._isConnected,notification
   #---------------------------------------------------------------------------      


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @client_method_tracker(TRACKFLAG)   
   def shutdown(self) :
      if (self._server is not None) and (self._isActivated is True) :
         self._server.shutdown()
   #---------------------------------------------------------------------------      
      

   #---------------------------------------------------------------------------
   #  Properties
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)   
   def _get_direction(self) :
      return self._direction
      
   @client_method_tracker(TRACKFLAG)   
   def _get_isActivated(self) :
      return self._isActivated


   @client_method_tracker(TRACKFLAG)   
   def _set_direction(self,direction) :
      self._direction = direction
   
   direction   = property(_get_direction, _set_direction)
   isActivated = property(_get_isActivated)
   #---------------------------------------------------------------------------
#-----------------------------------------------------------------------------

