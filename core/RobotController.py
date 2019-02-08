#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-
import threading
from threading import Thread
from threading import Condition
from threading import RLock
from threading import Event 
from math      import *
import hashlib
from getpass import getpass

import util

from util.Inputdevice   import *
from util.Outputdevice  import *
from util.Mylog         import *
from util.TCPConnection import *
from util.OutputGUI import *

from core.LabyrinthState import *
from core.Labyrinth      import *


eventSignalPlaying = threading.Event()


class RobotController(Protocol,Outputdevice,Inputdevice) :
   """ 
   Cette classe implemente l'interface de communication entre le joueur et le robot. 
   Elle permet au joueur d'envoyer des commandes pour contrôler le robot 
   et de recevoir les notifications du jeu. 
   Les commandes sont formatees en commandes de control (control command) et envoyees au labyrinthe.
   Le labyrinthe interprete la commande et agit sur le robot.
   
   Une instance de cette classe evolue dans 3 etats:
      *  STATE_WAIT_KEY  : attente d'etre enregistree sur le serveur
      *  STATE_READY_KEY : l'instance est enregistree sur le serveur, en attente du demarrage du jeu
      *  STATE_PlAY_KEY  : en cours de jeu
      *  STATE_PlAYING_KEY  : en cours de jeu et le tour de jeu se presente au joueur.
      
   L'instance est active dans deux threads. Le premier se charge des echanges de messages avec le serveur 
   et restitue au joueur les informations sur l'etat du jeu.
   Le second se charge de recuperer les commandes du joueur et de les transmettre au serveur.
   
   En mode automatique, le premier thread se charge d'enregistrer le joueur aupres du seveur. Pendant cette 
   phase, le joueur ne peut entrer de commande.
   Une fois la phase de negociation passee, un signal est envoye au second thread pour permettre au joueur de
   jouer. Cette synchronisation des deux threads se fait par un objet de type Event. 
   """

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def __init__(self, oLabyrinth, symbol, mode=Protocol.CLIENT_MODE, debug=False, isGUI=False, pserverAddress=None,isAuto=False, isCardDisplayed = True) :

      if 'premier' is mode : 
         # Mode dit 'premier' : oLabyrinth recoit les messages en local
         oReceiver = oLabyrinth
      else :
         # Mode client ou serveur: le labyrinthe est un serveur qui recoit 
         # des messages par un reseau TCP
         oReceiver = None
      
      Protocol.__init__(self, symbol, oReceiver, mode=mode, debug=debug, serverAddress=pserverAddress, isAuto=isAuto)
      Outputdevice.__init__(self)
      Inputdevice.__init__(self)
      
      self._notification   = ""
      self._command        = ""
      self._signalplaying  = False
      self._message        = (False,"",None)
      self._state          = LabyrinthState.STATE_WAIT_KEY
      self._startPlay      = False
      self._isThreadActive = False
      self._oOutputGUI     = None
      self._isGUI          = isGUI
      self._isCardDisplayed = isCardDisplayed
      self._isUnittest     = False
      self._isNotificationDisplayed = True

   #---------------------------------------------------------------------------
      
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def _helpMe(self) :
      self.setOutput("\n")
      self.setOutput(" Deplacements sur la carte: ")
      self.setOutput("   1 pas a Gauche --------> O ")
      self.setOutput("   n pas a Gauche --------> On")
      self.setOutput("   1 pas a Droite --------> E ")
      self.setOutput("   n pas a Droite --------> En")
      self.setOutput("   1 pas vers le Haut ----> N ")
      self.setOutput("   n pas vers le Haut ----> Nn")
      self.setOutput("   1 pas vers le Bas -----> S ")
      self.setOutput("   n pas vers le Bas -----> Sn")
      self.setOutput("   Monter 1 marche -------> U ")
      self.setOutput("   Monter n marches ------> Un ")
      self.setOutput("   Descendre 1 marche ----> D  ")
      self.setOutput("   Descendre n marches ---> Dn ")
      self.setOutput("\n Actions sur la carte: ")
      self.setOutput("   Murer au nord----------> mn ou Mn/mN/MN")
      self.setOutput("   Murer au sud ----------> ms ou Ms/mS/MS")
      self.setOutput("   Murer a l'est----------> me ou Me/mE/ME")
      self.setOutput("   Murer a l'ouest -------> mo ou Mo/mO/MO")
      self.setOutput("   Porte au nord ---------> pn ou Pn/pN/PN")
      self.setOutput("   Porte au sud  ---------> ps ou Ps/pS/PS")
      self.setOutput("   Porte a l'est ---------> pe ou Pe/pE/PE")
      self.setOutput("   Porte a l'ouest -------> po ou Po/pO/PO")
      self.setOutput("   Sortie au sud ---------> xs ou Xs/xS/XS")
      self.setOutput("\n Controle du jeu: ")
      self.setOutput("   Demarrer le jeu  ------> c ou C ")
      self.setOutput("   Tchater avec un robot -> t <symbol du robot> <message>")
      self.setOutput("   Tchater avec un robot -> T <symbol du robot> <message>")
      self.setOutput("   Quitter le jeu  -------> Q ou q")
      self.setOutput("   Rafraichir la carte ---> ?")
      self.setOutput("   Arreter du serveur ----> 0 le mot de passe sere demande")
      self.setOutput("   Forcer la victoire ----> u ou U pour unittest; le mot de passe sere demande")
      self.setOutput("\n")
      self.setOutput("\n")
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def run(self) :
      """
         Cette methode se charge de : 
          1) recuperer la commande du joueur,
          2) envoyer cette commande au serveur
          3) recuperer le message retourne par le serveur
          4) traiter le message 

         La commande envoyee par le joueur est recuperee de facon synchrone.
         Une fois envoyee, le client se met en attente de reception du message du serveur.
         
         Le thread s'arrete si : 
         1) le joueur envoie une commande d'arret 
         2) un message de fin de partie est recu 
         3) le joueur gagne la partie.
         
      """
      command        = None
      self._isThreadActive = True
      if self._isGUI is True :
         self._oOutputGUI     = OutputGUI()
         self._oOutputGUI.start()
      
      while(self._isThreadActive) :
         self.mylog("\n run() : State = {}".format(self._state))
         if LabyrinthState.STATE_WAIT_VALUE  == LabyrinthState.STATE_MACHINE[self._state] :
            if self._isAutoRecord :
               #---------------------------------------------------------------
               # Demande automatique de participation au jeu.
               # Si une partie est en cours il faut attendre le fin du jeu.
               #---------------------------------------------------------------
               time.sleep(2)
               message = self.send(Protocol.CTRL_ACTIONS_START) 
               if message is None :
                  message = self.receive_networkVersion()
                  self.messageProcess(message) 
               else :
                  #---------------------------------------------------------------
                  # L'envoie du message a echoue; le message est traite par la suite.
                  #---------------------------------------------------------------
                  pass
            else :
               #---------------------------------------------------------------
               # Connection au serveur :
               #---------------------------------------------------------------
               self._serverConnect()
               if self._isConnected is True :
                  #---------------------------------------------------------------
                  # Le joueur est connecte. Le controle est donne au joueur.
                  # Ce dernier peut envoyer une commande au serveur.
                  #---------------------------------------------------------------
                  self.signalplaying = True
                  
                  #---------------------------------------------------------------
                  # Attente de reception d'un message du serveur.
                  # Une fois recu, le message est traite.
                  #---------------------------------------------------------------
                  message = self.receive_networkVersion()
                  self.messageProcess(message) 

               else :
                  #---------------------------------------------------------------
                  # La connexion avec le serveur ne peut s'etablir
                  #---------------------------------------------------------------
                  self._isThreadActive = False
                  #---------------------------------------------------------------
                  # Debloquage eventuel de la boucle de controle 
                  # Le thread va s'arreter.
                  #---------------------------------------------------------------
                  self.signalplaying = False
                  self._state = LabyrinthState.STATE_END_KEY

         elif LabyrinthState.STATE_READY_VALUE == LabyrinthState.STATE_MACHINE[self._state] : 
            #---------------------------------------------------------------
            # Le joueur est enregistre. 
            # Attente du signal de demarrage de la partie. 
            # Une fois recu, le message est traite.
            #---------------------------------------------------------------
            self.mylog("\n State = {} : Waiting for server signal start".format(self._state))
            self.signalplaying = True
            message = self.receive_networkVersion()
            self.messageProcess(message) 
                       
         elif LabyrinthState.STATE_PLAY_VALUE == LabyrinthState.STATE_MACHINE[self._state] : 
            self.mylog("\n State = {} : Start play status= {}".format(self._state, self._startPlay))
            if self._startPlay is False :
               #---------------------------------------------------------------
               # Debloquage de la boucle de controle; la main est donnee au joueur.
               #---------------------------------------------------------------
               self.mylog("\n State = {} : Signal starting..".format(self._state))
               self.signalplaying = True
            #---------------------------------------------------------------
            # Attente de reception d'un message du serveur.
            # Une fois recu, le message est traite.
            #---------------------------------------------------------------
            self.mylog("\n State = {} : Waiting for server notification".format(self._state))
            message = self.receive_networkVersion()
            self.messageProcess(message) 
            
         elif LabyrinthState.STATE_PLAYING_VALUE == LabyrinthState.STATE_MACHINE[self._state] : 
            if self._startPlay is False :
               #---------------------------------------------------------------
               # C'est le tour de jeu du joueur.
               #---------------------------------------------------------------
               self.mylog("\n State = {} : Signal starting..".format(self._state))
               self.signalplaying = True

            #---------------------------------------------------------------
            # Attente de reception d'un message du serveur.
            # Une fois recu, le message est traite.
            #---------------------------------------------------------------
            self.mylog("\n State = {} : Waiting for server notification".format(self._state))
            message = self.receive_networkVersion()
            self.messageProcess(message) 

            
         elif LabyrinthState.STATE_END_VALUE == LabyrinthState.STATE_MACHINE[self._state] : 
            #---------------------------------------------------------------
            # Fin de la partie pour ce joueur.
            # La connexion est cloturee
            #---------------------------------------------------------------
            self._clientConnection.close()
            self._isConnected = False

            #---------------------------------------------------------------
            # Le thread se suicide
            #---------------------------------------------------------------
            self._isThreadActive = False
            
         else :
            self.mylog("***RobotController : Unknow state = {}".format(self._state))

      if self._isGUI is True :
         self._oOutputGUI._setStatus(False)
         self._oOutputGUI.join()

      self.mylog("\n***RobotController : Thread is ENDING***\n".center(80))
   #---------------------------------------------------------------------------



   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def control(self) :
      """ 
      Dans une boucle infinie, recoit les commandes du joueur, formate les 
      commandes recues en deplacements envoie les deplacements au labyrinthe sous la forme de commandes de controle.
      Affiche les notifications envoyees par le labyrinthe du jeu.

          NB: la notification pourrait etre sonorisee a l'aide d'une API REST envoyee a un 
          serveur intelligent comme Bluemix.
      """
      
      isContinue = True
      self.mylog("*** control() : mode = {}".format(self._mode))
      if self._mode is 'premier' :
         # Le robot en mode 1ere version
         pass 
      else :
         while self._startPlay is False :
            #------------------------------------------------------------------
            # Le robot fonctionne en version client / serveur
            # Attente du signal renvoye par le thread
            #------------------------------------------------------------------
            self._startPlay = self.signalplaying
            self.setOutput("Connection avec le serveur etablie!".center(80))
            self.mylog("**** control() : Signal received = {} / Thread state= {}".format(self._startPlay, self._state))
            if LabyrinthState.STATE_END_VALUE == LabyrinthState.STATE_MACHINE[self._state] : 
               break
               
      while( True == isContinue ):
         if (self._isThreadActive is False) and (self._mode is 'client'):
            isContinue = False
         else :
            pass
            
         if LabyrinthState.STATE_WAIT_VALUE is LabyrinthState.STATE_MACHINE[self._state] and self._mode is 'client':
            #------------------------------------------------------------------
            #L'enregistrement dans le jeu n'est pas automatique.
            #------------------------------------------------------------------
            message =  "Entrez C pour commencer la partie : "
         else :
            #------------------------------------------------------------------
            # En mode premier ou en mode client avec enregistrement automatique.
            #------------------------------------------------------------------
            message =  "Entrez le deplacement ou l'action (Q pour quitter le jeu, H pour l'aide) : "               
         
         prompt = self._symbol+ " :-) "
         command =  self.getInput(message, prompt=prompt)
         if command.capitalize() == self._help :
            self._helpMe()
         elif command.capitalize() == Protocol.CTRL_ACTIONS_HALT or command.capitalize() == Protocol.CTRL_ACTIONS_WIN:
            if self._isUnittest is False :
               clearPasswd    = getpass("Mot de passe : ") 
            else :
               clearPasswd ="roboc"

            cipheredPasswd = hashlib.sha1(clearPasswd.encode()).hexdigest()
            command = command.capitalize()+"_"+cipheredPasswd
            message = self.send(command)
            if message is not None :
               notification = message['notify']
               status       = message['status']
               self.setOutput(notification)
            else :
               pass

         else : 
            if self._mode is 'premier' :
               #------------------------------------------------------------------
               # jeu en mode premier 
               #------------------------------------------------------------------

               if command.capitalize() == Protocol.CTRL_ACTIONS_LEAVE :
                  self.setOutput("Au plaisir de vous revoir jouer!")
                  isContinue = False
               else :
                  message = self.send(command)
                  
                  notification = message['notify']
                  status       = message['status']
                  self.setOutput(notification)
                  if status is True :
                     isContinue = False                     
            else :
               #------------------------------------------------------------------
               # jeu en mode client/serveur sur un reseau TCP
               #------------------------------------------------------------------
               self.send(command)

               if self._isThreadActive is False :
                  isContinue = False
      return 
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def messageProcess(self, message) :
      """
         Cette methode traite un message recu du serveur.
         Le flag d'activite du thread est positionne a False si la partie est terminee, a True sinon.
         La methode payloadProcess est appelee pour traiter le contenu du message et faire evoluer l'etat de 
         l'objet.
      """
      
      #------------------------------------------------------------------
      # Traitement du message recu: l'etat de l'objet evolue en fonction du contenu du message.
      #------------------------------------------------------------------
      if message is not None :
         #------------------------------------------------------------------
         # Verification du message recu par le serveur; s'il y a une erreur, il n'est pas traite.
         #------------------------------------------------------------------
         status = message['status']
         if status is False :

            self.setOutput(message['notify'])
                        
            self._clientConnection.close() 
            self._isConnected = False
            self._state = LabyrinthState.STATE_END_KEY
            self.mylog("\n*** INFO : messageProcess() : state = {}".format(self._state))
                       
         else :
            #------------------------------------------------------------------
            # Recuperation de la payload 
            #------------------------------------------------------------------
            payloadMessage = message['payload']
                    
            #------------------------------------------------------------------
            # Traitement du contenu du message envoye par le serveur
            #------------------------------------------------------------------
            self.payloadProcess(payloadMessage)
            if status is True :
               pass
            else :
               self.setOutput("*** Erreur detectee dans le contenu du message recu")

         self.mylog("***RobotController : messageProcess() : State = {} ".format(self._state))
   #---------------------------------------------------------------------------
   
   #---------------------------------------------------------------------------
   #  
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def payloadProcess(self, payloadMessage) :
      """
         Cette methode traite le contenu des messages (la payload) en provenance du serveur.
         Les formats supportes : 
         * {'playstatus': value, 'state': value, 'turn':value, 'notify': notification, 'carte': data}
         * {'playstatus': value, 'state': value, 'turn':value, 'notify': notification}

         Une notification contenue dans la payload est delivree au joueur.
         Les differents champs du dictionnaire, sont traites.
         
         Le contenu du message fait changer l'etat du l'objet.
         Les etat possibles sont : WAIT, READY, PLAY, PLAYING.
         * WAIT  : le robot du joueur est en cours d'enregistrement sur le serveur.
         * READY : le robot du joueur est enregistre, le quotas de joueurs n'a pas ete atteint.
         * PLAY  : le quotas de joueurs a ete atteint, la partie a demarree.
         * PLAYING : C'est au tour du joueur de jouer.
         * ENDED : La partie est finie pour le joueur.

      """
      playStatus   = False
      status       = False
      payloadNotification = None
      gamersLocation      = None
      #------------------------------------------------------------------
      # Verification du format de la payload : 
      #------------------------------------------------------------------
      self.mylog("\n*** INFO : payloadProcess() : Payload= {}".format(payloadMessage))
      if ('playstatus' in payloadMessage) and ('notify' in payloadMessage) :
         payloadNotification = payloadMessage['notify'] 
         
         #------------------------------------------------------------------
         # L'etat du jeu (gagne/fin,en cours) est recupere : 
         #------------------------------------------------------------------
         playStatus = payloadMessage['playstatus']

         if 'symbol' in payloadMessage : 
            self._symbol = payloadMessage['symbol']
                      
         if 'location' in payloadMessage : 
            gamersLocation = payloadMessage['location']
            
         if 'carte' in  payloadMessage :
            #------------------------------------------------------------------
            # Affichage de la carte 
            #------------------------------------------------------------------
            oCarte  = payloadMessage['carte']
            self.displayCarte(oCarte, gamersLocation)
            
         if 'state' in  payloadMessage :
            #------------------------------------------------------------------
            # L'objet change d'etat
            #------------------------------------------------------------------
            self._state = payloadMessage['state']

         if 'halt' in  payloadMessage :
            #------------------------------------------------------------------
            # L'objet change d'etat
            #------------------------------------------------------------------
            self._state = payloadMessage['state']

         if playStatus is True :
            #------------------------------------------------------------------
            # La partie est terminee.
            #------------------------------------------------------------------
            self._state = LabyrinthState.STATE_END_KEY                        

         if payloadMessage['turn'] is True :
            #------------------------------------------------------------------
            # C'est le tour de jeu du joueur.
            #------------------------------------------------------------------
            self._state = LabyrinthState.STATE_PLAYING_KEY
            if playStatus is False :
               #------------------------------------------------------------------
               # La partie est toujours en cours
               #------------------------------------------------------------------
               pass 
            else :
               #------------------------------------------------------------------
               # La partie est gagnee par un joueur.
               #------------------------------------------------------------------
               pass

         else :
            pass
         if self._isNotificationDisplayed :
            #------------------------------------------------------------------
            # Affichage des messages du serveur 
            #------------------------------------------------------------------
            self.setOutput(self._symbol+" :-) "+payloadNotification)
         status = True
      
      else : 
         self.mylog("\n*** ERREUR : RobotController.payloadProcess() : format du contenu= {}".format(payloadMessage))

         return status, playStatus
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def displayCarte(self, oCarte, gamersLocation) :
      """
      Cette methode permet d'afficher la carte avec les symboles des 
      robots du jeu.
      
      Si le jeu en client (option -c) a ete lance en mode d'enregistrement automatique 
      (option -a ) et avec l'option de choisir son symbole pour le robot (option -r <symbol>)
      alors les symboles sont affiches.
      
      Si le jeu en client (option -c) a ete lance en mode d'enregistrement manuel 
      (sans l'option -a, avec ou sans l'option -r <symbol>) alors les symboles des robots 
      seront affiches x ou X si ce dernier est celui du joueur.
      Pour ce faire, gamersLocation le dictionnaire des positions de 
      chaque symbole de robot est utilise.
      """
      if self._isCardDisplayed is False :
         return 
      else :
         pass

      if self._isAutoRecord is False :
         # --------------------------------------------------------------------
         # Dans le cas de l'enregistrement manuel (la commande C est entree par la console)
         # Les symboles des robots sont differencies en x et X
         # --------------------------------------------------------------------
         if gamersLocation is not None :
            # --------------------------------------------------------------------
            #Les robots des autres joueurs sont remplaces 
            # --------------------------------------------------------------------
            for position in gamersLocation.values() :
               symbol    = Symbol._symbolRobot.lower()
               if position is not None :
                  oObstacle = Obstacle(symbol,position)
                  oCarte._setObstacle(oObstacle)
               else :
                  pass
            
            # --------------------------------------------------------------------
            # Le robot du joueur est remplace
            # --------------------------------------------------------------------
            if self._id in gamersLocation.keys() :
               position  = gamersLocation[self._id]
               if position is not None :
                  symbol    = Symbol._symbolRobot.upper()
                  oObstacle = Obstacle(symbol,position)
                  oCarte._setObstacle(oObstacle)
               else :
                  pass
         else :
            pass
      else :
         # --------------------------------------------------------------------
         # Dans le cas de l'enregistrement automatique (sans entrer la commande C de la console)
         # les symboles sont affiches differencies
         # --------------------------------------------------------------------
         pass
      self.setOutput("\n")
      centerLine = 0
      for line, symbolsLane in enumerate(oCarte._loadedObstacle):
         if len(str(line)) < 2 :
            lineToDisplay = str(line) + "  " + symbolsLane
         else :
            lineToDisplay = str(line) + " " + symbolsLane
         if self._isGUI is True :
            self._oOutputGUI.setOutput(lineToDisplay)
         else :
            if oCarte._cardID == 2 :
               centerLine = 130
            else :
               pass
            self.setOutput(lineToDisplay.center(centerLine))
         if line == oCarte._lineMax :
            # --------------------------------------------------------------------
            # La valeur de la deniere enumeration ne correspond pas a une ligne
            # --------------------------------------------------------------------
            break

      # --------------------------------------------------------------------
      # Affichage de la ligne de graduation horizontale
      # --------------------------------------------------------------------
      columnMax = oCarte.columnMax
      index = 0
      horizontalGraduate  = list()
      while index < columnMax :
         if index%9 == 5 :
            character = str(index%9)
         else :
            character = "|"            
         horizontalGraduate.append(character)
         index +=1

      strHorizontalGraduate = "".join(horizontalGraduate)
      strHorizontalGraduate = "  " + " " +strHorizontalGraduate
      self.setOutput(strHorizontalGraduate.center(centerLine))
      self.setOutput("\n")
         
               
      self.setOutput("\n")
         
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   #  Properties
   #---------------------------------------------------------------------------

   #--------------------------------
   @client_method_tracker(TRACKFLAG)
   def _get_signalplaying(self) :
      signalplaying = ""
      self.mylog("***\n RobotController._get_eventSignalPlaying() : waiting...")
      eventSignalPlaying.wait()
      self.mylog("***\n RobotController._get_eventSignalPlaying() : Wake up!")
      signalplaying = self._signalplaying
      self._signalplaying = ""
      eventSignalPlaying.clear()
      return signalplaying

   @client_method_tracker(TRACKFLAG)
   def _set_signalplaying(self,signalplaying) :
      self._signalplaying = signalplaying
      eventSignalPlaying.set()
      return

   @client_method_tracker(TRACKFLAG)
   def _set_isUnittest(self,isUnittest) :
      """
         Utilisee dans les tests unitaire pour forcer certaines valeurs 
         entrees par le joueur, comme le mot de passse du serveur.
      """
      self._isUnittest = isUnittest
      return
      
   #--------------------------------


   #--------------------------------
   signalplaying = property(_get_signalplaying,_set_signalplaying)
   isUnittest    = property(_set_isUnittest)

   #--------------------------------

   #---------------------------------------------------------------------------
      
      
      
      
      
