#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-

from util.common         import *
from util.Protocol       import *
from util.MessageHolder  import *
from core.LabyrinthState import *
from core.Labyrinth      import *
from core.Symbol         import *

class LabyrinthServer() :
   """
   Cette classe etend les services de la classe Labyrinth dont elle herite.
   L'heritage est implementee dans une aggregation.

   Cette classe implemente toute la logique du jeu du labyrinthe en reseaux joue a plusieurs joueurs.
   Les joueurs sont enregistres de facon ordonnee au fure et a mesure de leur connexion au serveur de jeu.
   Cet ordonancement permet de calculer le tour de jeu de chacun des joueurs.
   
   Cette classe gere la machine a etat finie du jeu qui evolue en fonction des requetes 
   recues par les joueurs. De ce fait, le jeu ne demarre que lorsque le quotas de joueurs 
   fixe au lancement du serveur est atteint.
      
   Les requetes des joueurs, recues sur le serveur, sont transmises par la classe 
   LabyrinthTCPServer.
   
   Les requetes sont verifiees et traitees selon le protocole implemente dans la classe Protocol.
   Le traitement des requetes des joueurs amene a traiter les types de commandes suivantes :
   * Les commandes de jeu, qui permettent des deplacements ou des actions des robots sur le jeu
   * Les commandes de controle du jeu, qui sont echangees entre le serveur et le joueur mais qui ne 
     prennent pas part au jeu.
   * La commande d'arret du serveur.
      
   Les commandes transmises a la classe Labyrinth, dont cette classe herite (presque, vous le savez).
   Les commandes de controle sont traitees dans cette classe.
  
   """

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   def __init__(self, mode, gamers, debug) :
      self.oLabyrinth    = Labyrinth(mode, gamers=gamers, debug=debug)
      self._gamersCount  = 0
      self._state        = LabyrinthState.STATE_WAIT_KEY
      self._gamersLocation = dict()
      self._gamersState  = dict()
      self._gamersSymbol = dict()
      self._gamersQueue  = DictionnaireOrdonne() # Dictionnaire ordonne, issue du TP3
      self._gamersMax    = gamers
      self._gamerTurn    = None
      self._isServerHalted = False
      
      # Le symbole du labyrinthe est enregistre dans la liste des symboles reserves
      Symbol.SYMBOL_LIST.append(Symbol._symbolLabyrinth)
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------  
   """
   Encapsulation de la methode Labyrinth.messageCheck
   Ce, pour simuler l'heritage de la classe Labyrinth.
   """    
   def messageCheck(self,message) :
      return self.oLabyrinth.messageCheck(message)
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   """
   Encapsulation de la methode Labyrinth.buildHeader
   Ce, pour simuler l'heritage de la classe Labyrinth.
   """    
   def buildHeader(self, status, notification, iddest) :
      return self.oLabyrinth.buildHeader(status, notification, iddest)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   """
   Encapsulation de la methode Labyrinth.mylog
   Ce, pour simuler l'heritage de la classe Labyrinth.
   """    
   def mylog(self,logmessage) :
      self.oLabyrinth.mylog(logmessage)
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   """
   Encapsulation de la methode Labyrinth.menu
   Ce, pour simuler l'heritage de la classe Labyrinth.
   """    
   def menu(self) :
      return self.oLabyrinth.menu()
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   """
   Encapsulation de la methode Labyrinth.processAction
   Ce, pour simuler l'heritage de la classe Labyrinth.
   """   
   @server_method_tracker(TRACKFLAG)
   def processAction(self, cmdAction) :
      return self.oLabyrinth.processAction(cmdAction)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   """
   Encapsulation de la methode Labyrinth.process
   Ce, pour simuler l'heritage de la classe Labyrinth.
   """    
   @server_method_tracker(TRACKFLAG)
   def processMoove(self, cmdMoove) :
      return self.oLabyrinth.process(cmdMoove)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def setRandomRobotPosition(self, symbol) :
      """
      Encapsulation de la methode Labyrinth.setRandomRobotPosition
      Ce, pour simuler l'heritage de la classe Labyrinth.
      """
      return self.oLabyrinth.setRandomRobotPosition(symbol)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   def mylog(self, message) :
      """
      Encapsulation de la methode Labyrinth.mylog
      Ce, pour simuler l'heritage de la classe Labyrinth.
      """
      return self.oLabyrinth.mylog(message)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #  Properties
   #---------------------------------------------------------------------------
   def _get_carteID(self) :
      return self.oLabyrinth._carteID

   def _get_oCarte(self) :
      return self.oLabyrinth._oCarte

   def _get_oRobot(self) :
      return self.oLabyrinth._oRobot

   def _set_oRobot(self, oRobot) :
      self.oLabyrinth._oRobot = oRobot

      
   carteID = property(_get_carteID)
   oCarte  = property(_get_oCarte)
   oRobot  = property(_get_oRobot, _set_oRobot)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def processWinner(self, gamerIdentifier, notify=None) :
      """
      Cette methode traite le cas du joueur dont l'identifiant passe en parametre a 
      gagne la partie.
      Une notification personnalisee est envoyee au gagnant.
      Une notification generale est envoyee aux autres joueurs.
      Toutes les ressources allouees aux joueurs sont liberees.
      """
      status = False
      #---------------------------------------------------------------------------#
      # Le joueur doit etre enregistre
      #---------------------------------------------------------------------------#      
      if gamerIdentifier not in self._gamersQueue.values()  :
         playStatus = False
         payloadNotification = "Pour gagner, vous devez etre enregistre dans le jeu!"
         self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)

      else :
         #---------------------------------------------------------------------------#
         # playStatus est mis a True: le jeu est gagne ou termine.
         #---------------------------------------------------------------------------#      
         playStatus = True

         #---------------------------------------------------------------------------#
         # Les joueurs passent dans l'etat WAIT
         #---------------------------------------------------------------------------#
         for gamerId in self._gamersQueue.values() :
            self._gamersState[gamerId] = LabyrinthState.STATE_END_KEY
         
         #---------------------------------------------------------------------------#
         # Le joueur a gagne; la partie prend fin. Le serveur retourne  l'etat WAIT
         #---------------------------------------------------------------------------#
         if notify is None :
            payloadNotification = "La partie est terminee. Bravo! Vous l'avez gagnee!"
         else :
            payloadNotification = notify
            
         self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)

         #---------------------------------------------------------------------------#
         # Diffusion a tous les autres joueurs de l'etat de la partie
         #---------------------------------------------------------------------------#
         winerRobot = self._gamersSymbol[gamerIdentifier]
         payloadNotification = " Fin de la partie! Le robot '{}' l'a remportee!".\
         format(winerRobot)   
         self.sendMessageOtherGamer(payloadNotification, gamerIdentifier)

         #---------------------------------------------------------------------------#
         # Les ressources allouees aux joueurs sont liberees
         #---------------------------------------------------------------------------#
         status = self._drop_allgamers()

         #---------------------------------------------------------------------------#
         # Le masque de la carte est mis a jour.
         #---------------------------------------------------------------------------#
         self.oCarte._symbolMask[0] = Symbol._symbolEmpty

         if status is False :
            self.mylog("\n ERREUR : _drop_allgamers returned= {}".format(status))
         else :
            pass                           
      return status
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------    
   @server_method_tracker(TRACKFLAG)
   def processPayload(self, message):
      """
      Cette methode traite une requete envoyee par un joueur.
      Le traitement suit les etapes suivantes :
      
         *  Cette methode verifie la conformite de la requete au protocole.
         *  Si la requete est conforme, elle est traitee par la classe Labyrinth.
         *  Sinon, un message de retour signalant l'erreur est retourne.
      
         *  Une fois le message traite par la classe Labyrinth, un message de 
            reponse est construit et retourne au joueur. Selon le traitement, 
            une notification peut etre envoyee a tous les autres joueurs. 
      
      """

      gamerRobotSymbol = ""
      gamerIdentifier  = None
      replyMessage     = dict()
      playStatus       = False
      
      self.mylog("processPayload() : received request = {}".format(message))
      
      # L'identifiant du joueur est releve
      gamerIdentifier = message['id']
      
      # Traitement du message recu par le joueur.
      status = True
      
      # Si la requete est valide, son contenu (la payload) est recuperee.
      payloadMessage = message['payload']
      self.mylog("LabyrinthServer.processPayload() : Server state= {} / payloadMessage= {}".\
      format(self._state, payloadMessage))
      
      if LabyrinthState.STATE_WAIT_VALUE == LabyrinthState.STATE_MACHINE[self._state] :
         if 'play' in payloadMessage :
            # Message non traitable
            payloadNotification = "La partie n'est pas encore commencee!"
            playStatus = False
            self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)

         elif 'ctrl' in payloadMessage :
            # Traitement d'une commande de controle par le serveur dans l'etat WAIT
            payloadCmd   = payloadMessage['ctrl']
            gamerRobotSymbol = payloadCmd[0]
            
            self.mylog("processPayload() : payloadCmd = {}".format(payloadCmd))

            # Traitement de la commande de controle du joueur et 
            # construction de la reponse qui sera retournee au joueur dans cette fonction
            self.processPayloadCtrl(payloadCmd, gamerIdentifier, gamerRobotSymbol)
                  
         else : 
            # La payload de ce message est inconnue 
            payloadNotification = "Le traitement de cette commande n'est pas disponible"
            playStatus = False
            self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)
                  
      elif LabyrinthState.STATE_PLAY_VALUE == LabyrinthState.STATE_MACHINE[self._state] :
         if 'play' in payloadMessage :   
            # Traitement d'une commande de jeu dans l'etat PLAY

            # Recuperation du tour du joueur 
            self.mylog("\n*** LabyrinthServer.processPayload() : Before scheduling : _gamersQueue= {}".\
            format(self._gamersQueue))

            playPosition = self.gameScheduler(gamerIdentifier)

            self.mylog("\n*** LabyrinthServer.processPayload() : After scheduling : _gamersQueue= {}".\
            format(self._gamersQueue))
      
            if(0 < playPosition) :
         
               #---------------------------------------------------------------------------#
               # Le tour de ce joueur ne s'est pas presente.
               # Construction du message de retour notifiant sa position de tour de jeu 
               #---------------------------------------------------------------------------#
               payloadNotification = "Patientez SVP; {} joueur(s) avant votre tour.".format(playPosition)
               self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)

               #---------------------------------------------------------------------------#
               # Le joueur dont c'est le tour est invite a jouer.
               #---------------------------------------------------------------------------#       
               payloadNotification = "C'est votre tour! Des joueurs s'impatientent!"
               self.sendMessageScheduledGamer(payloadNotification)
        
            else :
               #---------------------------------------------------------------------------#
               # Le joueur est bien celui dont c'est le tour de jouer.
               #---------------------------------------------------------------------------#
               playMessage = payloadMessage['play']
               messageNotification = ""      
               
               if 'moove' in playMessage  or 'action' in playMessage :
               
                  # Traitement d'une commande de jeu   
                  if 'moove' in playMessage :
                     # La payload du message est extraite et la commande est jouee
                     payloadCmd   = playMessage['moove']
                     gamerRobotSymbol = payloadCmd[0]                  
                                    
                     # La carte va proceder avec le symbole du robot du joueur
                     self.oCarte.symbolRobot = gamerRobotSymbol

                     # Le labyrinthe utilise le robot du joueur; 
                     self.oRobot = Robot(Protocol._zeroPosition, gamerRobotSymbol)

                     # La commande de deplacement est jouee
                     playStatus, notification = self.processMoove(payloadCmd)
                     
                     #La nouvelle position du robot est mise a jour dans les ressources des joueurs.
                     position = self.oCarte.getRobotPosition() 
                     self._set_gamerLocation(gamerIdentifier, position)
                     
                     # Le tour du joueur est passe 
                     self._gamerTurn = None
                           
                     if playStatus is False :
                     
                        #---------------------------------------------------------------------------#
                        # Le joueur n'a pas gagne. Une reponse est renvoyee au joueur 
                        #---------------------------------------------------------------------------#
                        payloadNotification = notification
                        self.sendMessageGamer( payloadNotification, gamerIdentifier, playStatus) 
                                                
                        #---------------------------------------------------------------------------#
                        # Recherche du joueur a jouer et envoie d'un message pour l'inviter a jouer.
                        #---------------------------------------------------------------------------#
                        self.sendMessageScheduledGamer(payloadNotification)

                        #---------------------------------------------------------------------------#
                        # Diffusion du message a chacun des joueurs sur l'etat de leur tour de jeu
                        #---------------------------------------------------------------------------#
                        self.sendMessageGamerTurnStatus(gamerIdentifier)

                     else :
                        status = self.processWinner(gamerIdentifier, notify=notification)
                     
                  elif 'action' in playMessage:      
                     payloadCmd   = playMessage['action']
                     gamerRobotSymbol = payloadCmd[0]
                     messageNotification = ""

                     #---------------------------------------------------------------------------#
                     # La commande du joueur est jouee
                     #---------------------------------------------------------------------------#

                     # La carte va proceder avec le symbole du robot du joueur
                     self.oCarte.symbolRobot = gamerRobotSymbol

                     # La commande de jeu est jouee
                     status, notification = self.processAction(payloadCmd)
                     
                     #Le tour du joueur est passe 
                     self._gamerTurn = None

                     # Les actions ne conduisent pas a la victoire.
                     playStatus = False
                     
                     #---------------------------------------------------------------------------#
                     # Envoie d'une reponse au joueur qui vient de jouer
                     #---------------------------------------------------------------------------#
                     payloadNotification = notification
                     self.sendMessageGamer( payloadNotification, gamerIdentifier, playStatus) 
                     
                     #---------------------------------------------------------------------------#
                     # Diffusion du message a chacun des joueurs sur l'etat de leur tour de jeu
                     #---------------------------------------------------------------------------#
                     self.sendMessageGamerTurnStatus(gamerIdentifier)

                     #---------------------------------------------------------------------------#
                     # Recherche du joueur dont c'est le tour de jouer et envoie d'un message 
                     # pour l'inviter a jouer.
                     #---------------------------------------------------------------------------#
                     payloadNotification = "C'est votre tour!"
                     self.sendMessageScheduledGamer(payloadNotification)

                  
                  else :
                     self.mylog("\n*** ERROR : processPayload() : Unknown playing message : {}".format(playMessage))

         elif 'ctrl' in payloadMessage : 
            #---------------------------------------------------------------------------#
            # Traitement d'une commande de controle dans l'etat PLAY
            #---------------------------------------------------------------------------#

            payloadCmd   = payloadMessage['ctrl']
            gamerRobotSymbol = payloadCmd[0]
            
            self.mylog("\n*** processMessage() : Server state= {} / PayloadCmd = {}".format(self._state ,payloadCmd))

            # Construction du contenu du message qui est retourne au joueur dans cette fonction
            self.processPayloadCtrl(payloadCmd, gamerIdentifier, gamerRobotSymbol)
            return 
                  
         else :
            playStatus = False
            #---------------------------------------------------------------------------#
            # Le joueur est notifie que sa commande de jeu est indisponible
            #---------------------------------------------------------------------------#
            payloadNotification = "Cette commande de jeu est indisponible."
            self.sendMessageGamer( payloadNotification, gamerIdentifier, playStatus) 
            
            #---------------------------------------------------------------------------#
            # Le joueur est invite a rejouer 
            #---------------------------------------------------------------------------#
            payloadNotification = "Vous pouvez rejouer!"
            self.sendMessageGamer( payloadNotification, gamerIdentifier, playStatus) 
            
            #---------------------------------------------------------------------------#
            # Diffusion a tous les autres joueurs de l'etat de leur tour de jeu
            #---------------------------------------------------------------------------#
            self.sendMessageGamerTurnStatus(gamerIdentifier)
      else :
         # This state should not be!
         self.mylog("\n*** ERROR : processMessage() : Unknown Server state= {} ".format(self._state))
             
         
      return replyMessage
   #---------------------------------------------------------------------------   


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def processPayloadCtrl(self, payloadCmd, gamerIdentifier, gamerRobotSymbol):
      """
         Cette methode traite le contenu d'une commande de controle envoyee par un joueur.
         Une commande de controle permet :
         * De renvoyer la carte du jeu avec tous les joueurs lorsque ceux-ci en font la demande.
         * D'enregistrer un joueur demandant de jouer; a cette occasion, son robot 
           est positionne sur la carte.
         * De de-enregistrer un joueur qui quitte la partie.
         * Ce tchater avec un autre joueur.
         
         Si le quotas de joueur est atteint, une notification de demarrage du jeu est envoyee 
         a tous les joueurs.
         
         Dans le cas contraire, une notification d'attente est envoyee a tous les joueurs.

         Le traitement d'une commande depend de l'etat du jeu. Cet etat evolue en fonction des 
         informations transportees dans les commandes.
      """
      # Sauf avis contraire, la partie n'est pas gagnee
      playStatus = False
      self.mylog("*** INFO : processPayloadCtrl() : Payload Command= {}".format(payloadCmd))
      if Protocol.CTRL_ACTIONS_WIN in payloadCmd : 
         #---------------------------------------------------------------------------#
         # Recuperation du mot de passe chiffre et verification de sa valeur
         #---------------------------------------------------------------------------#
         formatedPasswd = payloadCmd[2]
         splittedPasswd = payloadCmd[2].split("_")
         cipheredPasswd = splittedPasswd[1]
         self.mylog("*** INFO  : (passwd, received passwd)=({},{})".format(self._passwd, cipheredPasswd))
         if self._passwd == cipheredPasswd :
            #---------------------------------------------------------------------------#
            # Le joueur emetteur de ce message vient de gagner
            #---------------------------------------------------------------------------#
            self.processWinner(gamerIdentifier)

         else:
            #---------------------------------------------------------------------------#
            # Le mot de passe est invalide
            #---------------------------------------------------------------------------#
            self.sendMessageGamer("Mot de passe invalide!", gamerIdentifier, playStatus)
      
      elif Protocol.CTRL_ACTIONS_HALT in payloadCmd : 
         #---------------------------------------------------------------------------#
         # Recuperation du mot de passe chiffre et verification de sa valeur
         #---------------------------------------------------------------------------#
         formatedPasswd = payloadCmd[2]
         splittedPasswd = payloadCmd[2].split("_")
         cipheredPasswd = splittedPasswd[1]
         if self._passwd == cipheredPasswd :
            #---------------------------------------------------------------------------#
            # Diffusion a tous les joueurs de l'arret du serveur.
            #---------------------------------------------------------------------------#
            payloadNotification = "Arret du serveur"
            
            #---------------------------------------------------------------------------#
            # Tous les joueurs passent dans l'etat STATE_END_KEY
            #---------------------------------------------------------------------------#
            for gamerId in self._gamersState.keys() :
               self._gamersState[gamerId] = LabyrinthState.STATE_END_KEY

            #---------------------------------------------------------------------------#
            # Diffusion, a tous les joueurs, de l'information d'arret du serveur
            #---------------------------------------------------------------------------#
            self.sendMessageOtherGamer(payloadNotification, None)

            #---------------------------------------------------------------------------#
            # Les ressource de tous les joueurs sont liberees; cela provoquera 
            # La deconnexion de tous les serveurs dans la classe LabyrinthTCPServer
            #---------------------------------------------------------------------------#
            self._drop_allgamers()
            
            #---------------------------------------------------------------------------#
            # Le serveur est mis a l'arret
            #---------------------------------------------------------------------------#
            self._isServerHalted = True
         else :
            #---------------------------------------------------------------------------#
            # Le mot de passe est invalide
            #---------------------------------------------------------------------------#
            self.sendMessageGamer("Mot de passe invalide!", gamerIdentifier, playStatus)
         
      elif Protocol.CTRL_ACTIONS_GET is payloadCmd[1] : 
         #---------------------------------------------------------------------------#
         # Demande d'un joueur d'afficher la carte. La carte est recuperee.
         #---------------------------------------------------------------------------#
         payloadNotification = "Carte mise a jour!"
         self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)
            
      elif Protocol.CTRL_ACTIONS_TCHAT in payloadCmd :
         #---------------------------------------------------------------------------#
         # Traitement d'une commande de TCHAT : l'identifiant du recepteur du message 
         # est recherche a partir de son symbole transporte dans la commande de tchat.
         #---------------------------------------------------------------------------#
         self.mylog("\n*** INFO : TCHAT : payloadCmd = {}".format(payloadCmd))
         srcSymbol  = payloadCmd[0]
         destSymbol = payloadCmd[2]
         
         foundReceiver = False
         for gamerId in self._gamersSymbol.keys() :
            if destSymbol is self._gamersSymbol[gamerId] :
               # Le message est construit et envoye au destinataire 
               payloadNotification = "Message de : "+srcSymbol+"> "+payloadCmd[3]
               playStatus   = False               
               self.sendMessageGamer(payloadNotification, gamerId, playStatus)
               foundReceiver = True
               break
         #---------------------------------------------------------------------------#
         # Le recepteur du message n'a pas ete trouve; une reponse est renvoyee 
         # a l'emetteur
         #---------------------------------------------------------------------------#
         if False is foundReceiver :
            payloadNotification = "Le robot '"+destSymbol+"' est injoignabale!"
            playStatus = False
            self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)
         

      elif Protocol.CTRL_ACTIONS_LEAVE in payloadCmd :
         #-----------------------------------------------------------
         # Demande du joueur de quitter le jeu.
         #-----------------------------------------------------------
         
         if gamerIdentifier not in self._gamersQueue.values() :
            self._drop_gamer(gamerIdentifier)
         else :      
            #-----------------------------------------------------------
            # Le symbol du robot est releve 
            #-----------------------------------------------------------
            robotLeaving = self._gamersSymbol[gamerIdentifier]

            #-----------------------------------------------------------
            # Le joueur passe dans l'etat ENDED; il sera deconnecte et purge apres l'envoie de la reponse
            #-----------------------------------------------------------
            self._gamersState[gamerIdentifier] = LabyrinthState.STATE_END_KEY

            #-----------------------------------------------------------
            # Envoie de la reponse au joueur qui demande a quitter le jeu.
            #-----------------------------------------------------------
            payloadNotification = "Au plaisir de vous revoir!"
            playStatus = False
            self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)

            #-----------------------------------------------------------
            # Le joueur est purge du jeu. 
            #-----------------------------------------------------------
            self._drop_gamer(gamerIdentifier)
            
            #-----------------------------------------------------------
            # Envoi a tous les autres joueurs l'information
            #-----------------------------------------------------------
            payloadNotification = "INFO : le joueur '{}' vient de quitter le jeu!".format(robotLeaving)
            self.sendMessageOtherGamer(payloadNotification, gamerIdentifier)
            
            #-----------------------------------------------------------
            # Envoie de l'invite de jouer au joueur dont c'est le tour.
            # S'il n'y a plus de joueurs dans le jeu, aucun message n'est envoye.
            #-----------------------------------------------------------
            payloadNotification = "C'est votre tour!"
            self.sendMessageScheduledGamer(payloadNotification)
         

      elif Protocol.CTRL_ACTIONS_START in payloadCmd :      
         #-----------------------------------------------------------
         # Un joueur s'est connecte au serveur pour jouer une partie.
         # Il est enregistre et positionne sur la carte.
         #-----------------------------------------------------------
         self.mylog("\n*** INFO : Gamer ID : {} : Gamers = {} / Max= {}".\
         format(gamerIdentifier, self._gamersCount, self._gamersMax))           

         if self._gamersCount < self._gamersMax :
            #-----------------------------------------------------------
            # L'existence du symbol est verifiee: si le symbole du robot est dans la liste 
            # des symboles réserves, l'enregistrement ne se fait pas.
            #-----------------------------------------------------------
            if gamerRobotSymbol in Symbol.SYMBOL_LIST :
               #-----------------------------------------------------------
               # Recherche d'un symbol libre pour le robot du joueur 
               #-----------------------------------------------------------
               symbolFound = False
               for freeRobotSymbol in Symbol.SYMBOL_LIST_ALLOWED :
                  if freeRobotSymbol not in Symbol.SYMBOL_LIST :
                     gamerRobotSymbol = freeRobotSymbol
                     symbolFound = True
                     break
                  else :
                     pass
               if False == symbolFound :
                  payloadNotification  = "\nLe Symbole= '{}' est deja reserve.".format(gamerRobotSymbol)
                  payloadNotification += " Symboles reserves : {}".format(Symbol.SYMBOL_LIST)
                  
                  playStatus = False
                  self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus,\
                  symbolList=Symbol.SYMBOL_LIST)
                  return 
            else :
               pass 

            #-----------------------------------------------------------
            # Le serveur est en attente du quotas de joueurs
            # Le joueur est enregistre dans la liste des joueurs en 
            # attente de demarrage de la partie.
            #-----------------------------------------------------------
            status = self._set_gamer(gamerIdentifier, gamerRobotSymbol)
            self.mylog("\n*** INFO : processPayloadCtrl() : Recorded symbol= {}".format(gamerRobotSymbol))

            if status is True :
               #-----------------------------------------------------------
               # Le robot du joueur a ete enregistre. Il passe dans l'etat READY.
               # Dans cet etat, il sera a l'ecoute du signal du demarrage du jeu.
               #-----------------------------------------------------------
               gamerState = LabyrinthState.STATE_READY_KEY

               #-----------------------------------------------------------
               # Le robot du joueur est positionne sur la carte et sa position 
               # est associee a son identifiant. 
               #-----------------------------------------------------------
               position = self.setRandomRobotPosition(gamerRobotSymbol)
               if position is not None :
                  self._set_gamerLocation(gamerIdentifier, position)
               else :
                  #---------------------------------------------------------------
                  # Ce joueur ne peut etre enregistre dans le jeu; il en est notifie.
                  #---------------------------------------------------------------
                  payloadNotification = "Votre positionnement dans le jeu a echoue!"
                  self._set_gamersState(gamerIdentifier, LabyrinthState.STATE_END_KEY)
                  playStatus = False
                  self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)
                  return
                  
               #-----------------------------------------------------------
               # La liste contenant les symboles des obstacles du jeu est mise a jour.
               # Cela permet de choisir des symboles differents pour chaque robot.
               #-----------------------------------------------------------
               if gamerRobotSymbol not in Symbol.SYMBOL_LIST :
                  Symbol.SYMBOL_LIST.append(gamerRobotSymbol)

               #-----------------------------------------------------------
               # Le nombre de joueurs est incremente
               #-----------------------------------------------------------
               self._gamersCount  += 1
               
               #-----------------------------------------------------------
               # Message de notification au joueur qui vient de s'enregistrer
               #-----------------------------------------------------------
               if 1 == self._gamersCount :
                  payloadNotification = "Bienvenue! Vous etes le 1er joueur / "+\
                  str(self._gamersMax)+" attendu(s)."
               else :
                  payloadNotification = "Bienvenue! Vous etes le "+\
                  str(self._gamersCount)+"eme joueur / "+\
                  str(self._gamersMax)+" joueurs encore attendu(s)."
                  
            else :
               #-----------------------------------------------------------
               # L'enregistrement a echoue: le joueur etait deja present.
               #-----------------------------------------------------------
               gamersCount = self._gamersCount
               gamersMax   = self._gamersMax
               payloadNotification = "En attente du quotas de joueurs : {}/{}".format(gamersCount, gamersMax)
               gamerState = LabyrinthState.STATE_READY_KEY

            #-----------------------------------------------------------
            # L'etat du joueur est mis a jour
            #-----------------------------------------------------------
            self._set_gamersState(gamerIdentifier, gamerState)

            #-----------------------------------------------------------
            # Envoie de la reponse de sa demande d'enregistrement au joueur
            #-----------------------------------------------------------
            playStatus = False
            self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)
                        
            #-----------------------------------------------------------
            # Diffusion d'un message a tous les autres joueurs
            #-----------------------------------------------------------
            if self._gamersCount < self._gamersMax :
               messageNotification = ""      
               payloadNotification = "En attente du quotas de joueurs : {} enregistres / {} attendus".\
               format(self._gamersCount, self._gamersMax)
               self.sendMessageOtherGamer(payloadNotification, gamerIdentifier)
               
            else :
               #---------------------------------------------------------
               #  Le quotas a ete atteint ; la partie commence.
               #---------------------------------------------------------
               self._state = LabyrinthState.STATE_PLAY_KEY
               gamerState = self._state
               messageNotification = ""      
               payloadNotification = "La partie commence!"

               #---------------------------------------------------------
               # Tous les joueurs dans l'etat READY passent dans l'etat PLAY
               #---------------------------------------------------------
               for gamerId in self._gamersQueue.values() :
                  if self._gamersState[gamerId] is LabyrinthState.STATE_READY_KEY :
                     self._gamersState[gamerId] = gamerState 

               #---------------------------------------------------------
               # Diffusion a tous les autres joueurs de l'etat du jeu.
               #---------------------------------------------------------               
               self._gamerTurn  = self.getScheduledGamer()
               self.sendMessageOtherGamer(payloadNotification, self._gamerTurn)

               #---------------------------------------------------------
               # Envoi du signal au joueur dont le tour est a jouer
               #---------------------------------------------------------                              
               payloadNotification += " C'est votre tour."
               self.sendMessageScheduledGamer(payloadNotification)

         else :
            #-----------------------------------------------------------
            # Envoie la reponse au joueur pour le quotas atteint 
            #-----------------------------------------------------------
            playStatus = False
            payloadNotification = "Une partie est en cours. Attendez sa fin pour entrer dans le jeu."
            self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)
      else :
         #-----------------------------------------------------------
         # La commande n'est pas disponible
         #-----------------------------------------------------------
         playStatus = False
         payloadNotification = "Cette action n'est pas disponible!"
         self.sendMessageGamer(payloadNotification, gamerIdentifier, playStatus)
         
      return 
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @server_method_tracker(TRACKFLAG)
   def getGamerSchedule(self, gamerIdentifier) :
      """
      Cette methode permet de recuperer le tour d'un joueur dont l'identifiant
      est passe en parametre.
      """
      gamerPosition = 0
      
      #-----------------------------------------------------------
      # Classement des joueurs par timestamp croissant 
      #-----------------------------------------------------------
      self._gamersQueue.sort()

      #-----------------------------------------------------------
      # Calcul de la position du tour de jeu du joueur
      #-----------------------------------------------------------
      for gamerTime in self._gamersQueue.keys() :
         if self._gamersQueue[gamerTime] is gamerIdentifier :
            break
         else :
            gamerPosition += 1
      return gamerPosition
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def gameScheduler(self, gamerIdentifier):
      """
         Cette methode est un ordonanceur pour les tours de jeu.
         Chaque joueur, identifie par le parametre gamerIdentifier, 
         est insere dans une file d'attente de type dictionnaire, dont les cles sont
         des horodateurs. Le tour de jeu de prochain joueur est determine par la valeur de 
         l'horodateur la plus petite dans le file.
         
         Si le tour du joueur est recupere, sa valeur d'horodateur est mise a jour. La valeur 
         0 est retournee pour le tour de jeu.
         
         Sinon, la position du joueur dans la file d'attente est retournee et sa commande de jeu ne sera pas 
         traitee.
         
         Retourne :
         * 0   : si le tour du joueur se presente.
         * N>0 : pour le nombre de tours avant le tour du joueur.
      """
      gamerPosition = 0
      gamerTime     = None
      
      #-----------------------------------------------------------
      # Si le joueur n'a pas encore joue, c'est encore son tour
      #-----------------------------------------------------------
      if self._gamerTurn is gamerIdentifier :
         return 0
      
      #-----------------------------------------------------------
      #Classement des joueurs par timestamp croissant 
      #-----------------------------------------------------------
      self._gamersQueue.sort()
      
      #-----------------------------------------------------------
      # Calcul de la position du tour
      #-----------------------------------------------------------
      for gamerTime in self._gamersQueue.keys() :
         if self._gamersQueue[gamerTime] == gamerIdentifier :
            break
         else :
            gamerPosition += 1

      #-----------------------------------------------------------
      # Reprogrammation du tour de jeu du joueur si son tour de 
      # jouer se presente (gamerPosition == 0).
      #-----------------------------------------------------------
      if 0 == gamerPosition :
         del(self._gamersQueue[gamerTime])
         timestamp = time.time()
         self._gamersQueue[timestamp] = gamerIdentifier 
         self._gamerTurn = gamerIdentifier
         
      return gamerPosition
   #---------------------------------------------------------------------------
      
   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def _set_gamerLocation(self, gamerIdentifier, position) :
      """
         Cette methode enregistre la position du robot d'un joueur avec son identifiant. 
         L'enregistrement des positions de tous les joueurs est retourne a chacun des joueurs. 
         De fait, les robots de ces derniers peuvent etre differencies lors de 
         l'affichade de la carte.
      """
      if gamerIdentifier in self._gamersQueue.values() :
         self._gamersLocation[gamerIdentifier] = position
      
   #---------------------------------------------------------------------------      
   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def _get_gamerLocation(self, gamerIdentifier) :
      """
         Cette methode retourne la position du robot 
         associee a l'identifiant d'un joueur.         
      """
      position = None
      if gamerIdentifier in self._gamersQueue.values() :
         position = self._gamersLocation[gamerIdentifier]
      
      return position
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def _get_gamersState(self, identifier) :
      """
         Cette methode retourne l'etat d'un joueur.
      """
      status = False
      state  = None
      if identifier in self._gamersQueue.values() :
         state = self._gamersState[identifier]
         status = True
      return status, state
   #---------------------------------------------------------------------------      
   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def _set_gamersState(self, identifier, state) :
      """
         Cette methode enregistre l'etat d'un joueur.
      """
      if identifier in self._gamersQueue.values() :
         self._gamersState[identifier] = state
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def _set_gamer(self, identifier, symbol) :
      """
         Cette methode enregistre l'association de l'identifiant du joueur et du symbole de 
         son robot.
         Cela permet une representation symbolique unique des robots des joueurs.
         
         Retour :
         ------
            True  : l'enregistrement a reussi
            False : sinon
      """
      status    = False
      timeStamp = None
      if identifier not in self._gamersQueue.values() :            
         timeStamp = time.time()
         self._gamersQueue[timeStamp] = identifier
         self._gamersSymbol[identifier] = symbol
         status = True
      return status      
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------      
   #
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def _drop_gamer(self, identifier) :
      """
         Cette methode permet de purger un joueur du jeu. Toutes les ressources 
         allouees pour ce joueur sont liberees.
         Cette fonction est appelee apres avoir envoye une reponse au joueur

         Le joueur est identifie par le parametre identifier.
         Retourne True en cas de succes, False sinon
      """
      status = False
      self.mylog("\n*** _drop_gamer() Entering : Gamers= {}".format(self._gamersCount))
      if identifier in self._gamersQueue.values() : 
         #-----------------------------------------------------------      
         # La liste des symboles des obstacles du jeu est mise a jour 
         #-----------------------------------------------------------      
         gamerRobotSymbol = self._gamersSymbol[identifier]
         
         #-----------------------------------------------------------      
         # Le robot du joueur est efface de la carte.
         # Pour ce faire, une case vide occupe la position du robot. 
         #-----------------------------------------------------------      
         oObstacle = Obstacle(gamerRobotSymbol, Protocol._zeroPosition)
         position  = self._gamersLocation[identifier]
         
         # position = self.oCarte.getPosition(oObstacle)
         
         self.mylog("\n*** _drop_gamer() Robot position= {}".format(position))
         if position is not None :
            oObstacle = Obstacle(Symbol._symbolEmpty, position)
            self.oCarte._setObstacle(oObstacle)
         
         #-----------------------------------------------------------      
         # Le symbole du robot est purge de la liste des symboles
         #-----------------------------------------------------------      
         if gamerRobotSymbol in Symbol.SYMBOL_LIST :
            Symbol.SYMBOL_LIST.remove(gamerRobotSymbol)

         #-----------------------------------------------------------      
         # Les ressources liees a ce joueur sont liberees.
         #-----------------------------------------------------------      
         status = False
         if self._gamerTurn is identifier :
            self._gamerTurn = None
         
         self._gamersSymbol.pop(identifier)
         self._gamersLocation.pop(identifier)
         self._gamersState.pop(identifier)
         self._gamersConnection.pop(identifier)      
         for timeStamp in self._gamersQueue.keys() :
            if self._gamersQueue[timeStamp] == identifier :
               del(self._gamersQueue[timeStamp])
               status = True
               break
      

         #-----------------------------------------------------------      
         # Le nombre de joueurs est decremente
         #-----------------------------------------------------------      
         self._gamersCount -= 1
         
         #-----------------------------------------------------------      
         #Si le nombre de joueurs 0, le serveur passe dans l'etat WAIT
         #-----------------------------------------------------------      
         if self._gamersCount is 0 :
            self._state = LabyrinthState.STATE_END_KEY
         
      else :
         #-----------------------------------------------------------      
         # Si la connexion du joueur a ete enregistree, elle est purgee.
         #-----------------------------------------------------------      
         self.mylog("*** WARNING : _drop_gamer() No gamer found in list for identifier= {}".format(identifier))
         if identifier in self._gamersConnection.keys():      
            self._gamersConnection.pop(identifier)      
      
      self.displayGamersRessources()
      
      self.mylog("\n*** _drop_gamer() Leaving : Gamers= {}".format(self._gamersCount))
      return status
      
   #---------------------------------------------------------------------------      
   #---------------------------------------------------------------------------      
   #
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def _drop_allgamers(self) :
      """
         Cette methode permet de purger tous les joueurs du jeu.
         Retourne True en cas de succes, False sinon
      """
      status =  True
      for gamerId in self._gamersQueue.values() :
         status = (self._drop_gamer(gamerId) and status)

      status = (status and (self._gamersCount is 0))

      return status
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def sendMessageScheduledGamer(self, payloadNotification) :
      """
      Cette methode permet d'envoyer une reponse au joueur dont c'est le tour de jouer.
      Le joueur dont c'est le tour est recupere de l'ordonanceur de jeu et la notification 
      passee en parametre est envoyee au joueur.
      """
      messageNotification = ""
      
      #-----------------------------------------------------------      
      #  Le tour de jeu du joueur est re-ordonance
      #-----------------------------------------------------------      
      self._gamerTurn  = self.getScheduledGamer()
      if self._gamerTurn is None :
         # Le joueur n'a pas ete enregistre.
         pass
      else :
         gamerState = self._gamersState[self._gamerTurn]

         #-----------------------------------------------------------      
         # Construction du message : entete + payload 
         #-----------------------------------------------------------      
         replyMessage = self.buildHeader(True, messageNotification, self._gamerTurn)
         
         replyMessage['payload'] = {'carte':self.oCarte,'notify':payloadNotification,\
          'playstatus':False, 'turn':True, 'state':gamerState, 'location':self._gamersLocation}

         #-----------------------------------------------------------      
         # Envoie du message au joueur dont c'est le tour de jeu.
         #-----------------------------------------------------------      
         self.mylog("\n*** INFO : sending message to gamer turn id= {}".format(self._gamerTurn))
         self.sendMessage(self._gamerTurn, replyMessage)
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------      
   #
   #---------------------------------------------------------------------------      
   @server_method_tracker(TRACKFLAG)
   def sendMessageOtherGamer(self, payloadNotification, gamerIdentifier) :
      """
         Cette methode envoie la notification payloadNotification a tous les joueurs excepte 
         celui dont l'indentifiant gamerIdentifier est passe en parametre.
      """
      #-----------------------------------------------------------      
      # Envoie a tous les autres joueurs la notfication passee en parametre.
      #-----------------------------------------------------------      
      
      self.mylog("\n*** INFO : sendMessageOtherGamer() : Entering : gamerIdentifier= {}".format(gamerIdentifier));
      self.displayGamersRessources()
      
      playStatus = False
      messageNotification = ""
      for gamerId in self._gamersQueue.values() :
         replyPayload = dict()
         replyMessage = dict()

         self.mylog("\n*** INFO : sendMessageOtherGamer() : (gamerID, gamerIdentifier) = {}".\
         format((gamerId, gamerIdentifier)));

         if gamerId != gamerIdentifier :
            #-----------------------------------------------------------      
            # Construction du message pour les joueurs en attente de jouer
            #-----------------------------------------------------------      
            self.mylog("\n*** INFO : sendMessageOtherGamer() : (gamerId, gamerIdentifier)=({},{}) / Status={}".\
            format(gamerId, gamerIdentifier, (gamerId != gamerIdentifier)))
            replyMessage = self.buildHeader(True, messageNotification, gamerId)
            gamerState = self._gamersState[gamerId]
            replyPayload = {'notify':payloadNotification, 'playstatus':playStatus, 'state':gamerState, 'turn':False}
            replyMessage['payload'] = replyPayload
            self.sendMessage(gamerId, replyMessage)
         else :
            #-----------------------------------------------------------      
            # Le joueur passe en parametre ne doit pas recevoir ce message.
            #-----------------------------------------------------------      
            pass;     
   #---------------------------------------------------------------------------   

   #---------------------------------------------------------------------------   
   #
   #---------------------------------------------------------------------------   
   @server_method_tracker(TRACKFLAG)
   def sendMessageGamer(self, payloadNotification, gamerIdentifier, playStatus, symbolList=None) :
      """
      Cette methode permet d'envoyer au joueur identifie par le parametre gamerIdentifier 
      la notification payloadNotification.
      
      Si le joueur n'est pas enregistre dans le jeu, le message lui est envoye avec l'etat WAIT.
      Les ressources liees au joueur sont alors purgees.
      
      Si le parametre symbolList est different de None, il est insere dans la payload du message.
      Le recepteur utilisera ce champ pour trouver un symbole et s'enregistrer a nouveau.
      """

      messageNotification = ""
      gamerState     = None
      gamerTurnState = False
      symbol         = None
      isGamerRecorded = False

      if gamerIdentifier in self._gamersQueue.values() :
         isGamerRecorded = True

      #-----------------------------------------------------------      
      # L'etat du joueur est recupere
      #-----------------------------------------------------------      
      if isGamerRecorded is True :
         gamerState = self._gamersState[gamerIdentifier]
      else :
         gamerState = LabyrinthState.STATE_WAIT_KEY

      #-----------------------------------------------------------      
      # Est-ce encore le tour de ce joueur?
      #-----------------------------------------------------------      
      if gamerIdentifier is self._gamerTurn :
         gamerTurnState = True

      #-----------------------------------------------------------      
      # Le joueur a t-il gagne? Si oui l'etat (playStatus, gamerTurnState) = (True, True)
      # indique au joueur qu'il a gagne la partie.
      #-----------------------------------------------------------      
      if playStatus is True :
         gamerTurnState = True
      
      #-----------------------------------------------------------      
      # Recuperation du symbol du robot de ce joueur 
      #-----------------------------------------------------------      
      if gamerIdentifier in self._gamersSymbol.keys() :
         symbol = self._gamersSymbol[gamerIdentifier]
      else :
         pass

      #-----------------------------------------------------------
      # Construction du message a envoyer
      #-----------------------------------------------------------      
      replyMessage = self.buildHeader(True, messageNotification, gamerIdentifier)
      replyPayload = {'notify':payloadNotification,'playstatus':playStatus,\
      'turn':gamerTurnState, 'state':gamerState, 'carte':self.oCarte, 'location':self._gamersLocation}
      if symbol is not None :
         replyPayload['symbol'] = symbol
      else :
         pass

      if symbolList is not None :
         replyPayload['symbolList'] = symbolList
      else :
         pass
      replyMessage['payload'] = replyPayload
      
      #-----------------------------------------------------------
      # Envoie du message.
      #-----------------------------------------------------------
      self.sendMessage(gamerIdentifier, replyMessage)
      
      #-----------------------------------------------------------
      # Si le joueur n'est pas enregistre dans le jeu, ses ressources 
      # sont purgees.
      #-----------------------------------------------------------
      if isGamerRecorded is False :
         self._drop_gamer(gamerIdentifier)
   #---------------------------------------------------------------------------   

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------   
   @server_method_tracker(TRACKFLAG)
   def sendMessageGamerTurnStatus(self, gamerIdentifier) :
      """
      Cette methode permet de diffuser a presque tous les joueurs un message 
      notifiant le statut de leur tour de jeu.
      L'identifiant du joueur passe en parametre ne recoit pas ce message.
      """
      playStatus = False
      for gamerId in self._gamersQueue.values() :
         if gamerId != gamerIdentifier :
            playPosition        = self.getGamerSchedule(gamerId)
            if 0 < playPosition :
               payloadNotification = " Il reste {} joueur(s).e(s) / {} joueurs avant votre tour".\
               format(playPosition, self._gamersMax)
            elif 0 == playPosition :
               payloadNotification = "C'est votre tour"
            else :
               self.mylog_error(" sendMessageGamerTurnStatus() : Incorrect value for playPosition= {}".\
               format(playPosition))
               
            self.sendMessageGamer(payloadNotification, gamerId, playStatus)

         else :
            pass

   #---------------------------------------------------------------------------   
   #
   #---------------------------------------------------------------------------   
   @server_method_tracker(TRACKFLAG)
   def getScheduledGamer(self) :
      """
         Retourne l'identifiant du joueur dont c'est le tour de jouer.
         Si le joueur n'est pas trouve, retourne None.
      """
      gamerTurn = None
      self._gamersQueue.sort()
      try :
         key = self._gamersQueue.keys()[0]
         self._gamerTurn = self._gamersQueue[key]
      except  IndexError :
         self._gamerTurn = None
      return self._gamerTurn
   #---------------------------------------------------------------------------   
      
   #---------------------------------------------------------------------------   
   #
   #---------------------------------------------------------------------------   
   def displayGamersRessources(self) :
      """
         Affiche les ressources allouees aux joueurs.
         Cette methode est utilisee pour la mise au point de l'application.
      """
      self.mylog("\n Gamers location   = {}".format(self._gamersLocation))
      self.mylog("\n Gamers state      = {}".format(self._gamersState))
      self.mylog("\n Gamers symbol     = {}".format(self._gamersSymbol))
      self.mylog("\n Gamers queue      = {}".format(self._gamersQueue))
      self.mylog("\n Gamers Turn       = {}".format(self._gamerTurn))
      self.mylog("\n Gamers connection = {}".format(self._gamersConnection))
      self.mylog("\n Gamers count      = {}".format(self._gamersCount))

      
   #---------------------------------------------------------------------------   

