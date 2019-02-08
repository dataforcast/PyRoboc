#!/usr/bin/python3.5
#-*- coding: utf-8 -*-
import sys
import util
from util.Protocol         import *
from util.DictionnaireOrdonne           import *
from core.Carte            import *
from core.RobotController  import *
from core.Robot            import *
from core.Symbol           import *

   
class Labyrinth(Protocol,Obstacle,Inputdevice) :
   """ 
   Cette classe implemente la logique du jeu du labyrinthe. 
   Dans l'etat actuel, cette logique consiste a deplacer des robots sur une carte 
   et a realiser des actions sur les obstacles de la carte.
   
   Le labirynthe est un obstacle particulier; son symbole est L.
   Il n'est pas represente sur la carte.
   Les services de cette classe sont de : 
   1) presenter le menu du jeu
   2) charger la carte selectionnee par la.le joueu.r.se 
   3) charger et sauvegarder une partie en cours (version 1 du jeu)
   4) creer les objets necessaires au bon deroulement du jeu 
   5) lancer le jeu
   6) Realiser les deplacements et les actions du jeu.
   Ses methodes lui permettent de gerer les obstacles de la carte.

   """
   isInstantiated = False
   POSITION=(0,0,0)
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __init__(self,mode='server', gamers=1, debug=True) :
      """ 
      Initialise les objets necessaires au jeu du labyrinthe.
      Charge la liste des cartes disponibles 
      """
      print("\n Labyrinth.__init__() : debug= {}".format(debug))
      displayable      = False

      Protocol.__init__(self, Symbol._symbolLabyrinth, self, mode=mode, debug=debug)
      Obstacle.__init__(self, Symbol._symbolLabyrinth, Labyrinth.POSITION, displayable=displayable, debug=debug)
      self._oCarte         = Carte(debug=debug)
      self._leaveCmd       = "Q"
      self._oCarte.readList()
      self._carteID        = -1
      self._cardFolder     = "cartes"
      self._gamersCount    = 0
      self._oRobot         = Robot(Protocol._zeroPosition)
      self.mylog("\n*** INFO : Labyrinth active en mode debug= {}\n".format(debug))
   #---------------------------------------------------------------------------   
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def loadParty(self,cardName) :
      """
         Si le jeu le jeu n'est pas lance en mode "premier", la methode retourne 
         silencieusement.
         
         Dans le cas contraire, cette methode permet de reprendre s'il en existe, une partie en cours.
         L'existence d'une partie en cours correspondant au nom de la carte passee en parametre.
         Si une partie existe, il est demande au joueur de valider le rejeu.   
      """
      if self._mode is not 'premier' :
         return
   
      messageOldParty = "\nUne partie en cours existe pour cette carte. Souhaitez vous la continuer (o=oui, n=non)?\n"
      isParty,dataName  = self._oCarte.getDataName(cardName)
      if  True == isParty :
         # Une partie en cours a ete trouvee: demande au joueur de la rejouer
         strReponse =  self.getInput(messageOldParty)
         if  'O' == strReponse.capitalize() :
            #Chargement de la partie en cours
            status ,self._oCarte = self._oCarte.loadParty(dataName)
            self.mylog(" *** menu() : Loaded Card= {} ".format(self._oCarte))
            if True == status :
               pass
            else :
               print("*** ERREUR : la partie n'a pu etre chargee *** \n")
      
   #---------------------------------------------------------------------------
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def menu(self, cardID=None):
      """ 
      Permet au joueu.r.se de selectionner une carte dans le menu.
      La carte selectionnee est chargee en memoire.

      S'il existe une partie en cours pour la carte selectionnee, il est 
      propose au joueu.r.se de rejouer la partie en cours.
      """
             
      message = "\nSelectionnez un identifiant de carte (Quittez le jeu en entrant \""+ self._leaveCmd+"\") :\n "

      isValid = False
      while( False == isValid ):
         self._oCarte.displayList()
         if cardID is None :
            strCarteID =  self.getInput(message)
         else :
            strCarteID = str(cardID)
         if( strCarteID == self._leaveCmd or strCarteID.capitalize() == self._leaveCmd) :
            print(" Au plaisir de vous revoir !")
            self._carteID = -1
            break

         else : 
            # Verification de la selection 
            isValid = self._oCarte._checkInput(strCarteID)
            if(True == isValid):
            
               # Les identifiant de carte et de nom sont stockes dans le labyrinthe.
               self._carteID    = int(strCarteID)

               # Chargement de la carte 
               self._oCarte.load(self._carteID)
               status, self._carteName  = self._oCarte.getCardName(self._carteID)
               
               # Chargement d'une partie en cours
               self.loadParty(self._carteName)
               
               # Affichage de la carte 
               self._oCarte.display()         
               

            else :
               print("*** Selection invalide! *** \n")
      return self._carteID
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   def play(self) : 
      """
         Affiche la carte a l'ecran, creer l'objet de type RobotController, le controleur 
         du robot, transfert le contrôle du jeu au controleur de robot.
      """
      self._oCarte.display()
      print("\n*** play() : Mode= {} Debug= {}".format(self._mode, self._debug))
      self._oRobotController = RobotController(self, self._oCarte.symbolRobot, mode=self._mode, debug=self._debug)
      self._oRobotController.control()
   #---------------------------------------------------------------------------
         
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   def gameScheduler(self, gamerIdentifier):
      """
         Programme, dans la file d'attente, le joueur identifie par le parametre gamerIdentifier .

         Si le tour du joueur se presente, ce dernier est positionne en fin de file d'attente et 
         la valeur 0 est retournee.
         
         Sinon, la position du joueur dans la file d'attente est retournee.
      """
      gamerPosition = 0
      gamerTime     = None
      #Classement par timestamp croissant 
      self._gamersQueue.sort()
      
      # Calcul de la position du tour
      for gamerTime in self._gamersQueue.keys() :
         if self._gamersQueue[gamerTime] == gamerIdentifier :
            break
         else :
            gamerPosition += 1
            
      # Reprogrammation du joueur si son tour de jouer se presente.
      del(self._gamersQueue[gamerTime])
      timestamp = time.time()
      self._gamersQueue[timestamp] = gamerIdentifier 
         
      return gamerPosition
   #---------------------------------------------------------------------------

   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   def process(self,controlCmd):
      """
         Implemente le traitement de la commande de controle passee en parametre.
         Calcul le deplacement du robot sur la carte.
         Positionne le robot sur la carte du jeu.
         Sauvegarde la partie en cours.
         
         Retourne une notification sur l'etat du traitement du controle. 
         Lorsque la.le joueu.r.se a gagne.e, la partie en cours est purgee.
      """
      
      # La commande de controle est le rafraîchissement de la carte 
      if '?' in controlCmd or 'G' in controlCmd:
         self._oCarte.display()
         return False,""#"\nA vous de jouer!"
                     
      # Calcul la position du symbole sur la carte si le robot n'a pas ete deplace.
      # C'est le cas quand le jeu n'a pas commence. Le robot sera instantie a la 
      # position qu'il a sur la carte.
      if True == self._oRobot.isRestState()  :
         position = self._oCarte.getRobotPosition()
         if Protocol._zeroPosition == position :
            message = "\n*** ERREUR :  PAS DE ROBOT TROUVe SUR LA CARTE!\n"
            return True,message
         
         self._oRobot = Robot(position,self._oCarte.symbolRobot)
         self.mylog("*** self.process()  : Initialized robot= {}".format(self._oRobot))

      # Calcul la position du robot sur la carte
      status, notification = self._oRobot.compute(controlCmd)
      if False == status :
         self.mylog(" *** ERREUR : oRobot.compute() returned= {}".format(status))
         return status, notification
               
      # Le robot est positionne sur la carte. Si la valeur de playStatus est a la valeur True, 
      # la partie est gagnee.
      playStatus, notification,self._oRobot = self._oCarte.setPosition(self._oRobot)
   
      if self._mode is 'premier' :
         self.mylog("*** process() : playStatus = {}".format(playStatus))
         if True == playStatus :
            # La partie est gagne.e : la partie en cours est purgee
            self._oCarte.dropParty()
         else :
            # La partie en cours est sauvegardee
            self.mylog("*** process() : backupParty()")
            self._oCarte.backupParty()

      return playStatus,notification
   #---------------------------------------------------------------------------
   

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   def processAction(self, actionCmd) :
      """
         Cette methode implemente le traitement de la commande d'action passee en parametre.
         Elle calcule la position de l'obstacle sur la carte issue de la commande.
         Elle positionne sur la carte l'obstacle issue de la commande.
         
         Retourne une notification sur l'etat du traitement de la commande. 

      """
      #------------------------------------------------------------------------
      # Creation de l'obstacle a partir de la commande d'action.     
      #------------------------------------------------------------------------
      status, symbolObstacle = self.action2symbol(actionCmd[1]) 
      
      if False == status :
         notification = "*** ERREUR : Action non reconnue = '{}'".format(actionCmd[1])
         self.mylog(" *** ERREUR : Labyrinth.processAction() : action2symbol() returned= {}".format(status))
         return status, notification
      
      #------------------------------------------------------------------------
      # L'obstacle a positionner sur la carte est initilise a la position du robot.
      #------------------------------------------------------------------------
      position = self._oCarte.getRobotPosition()
      oObstacle = Obstacle(symbolObstacle, position)
      
      #------------------------------------------------------------------------
      # Calcul la position de l'obstacle sur la carte en fonction de la commande de jeu.
      # Cela revient a calculer un deplacement.
      #------------------------------------------------------------------------
      status, notification = oObstacle.compute(actionCmd)
      
      if False == status :
         notification = "*** ERREUR : Calcul de la position de l'obstacle!"
         self.mylog(" *** ERREUR : Labyrinth.processAction : oObstacle.compute() returned= {}".format(status))
         return status, notification
               
      #------------------------------------------------------------------------
      # Verification que l'obstacle ne soit pas la sortie
      #------------------------------------------------------------------------
      newPosition   = oObstacle.newPosition
      exitPosition  = self._oCarte._getPosition(Symbol._symbolExit)
      if newPosition is exitPosition :
         return True, ""

      #------------------------------------------------------------------------
      # Verification que l'obstacle a remplacer ne soit pas un symbole 
      # non autorise pour cette action.
      #------------------------------------------------------------------------
      symbol = self._oCarte.getSymbol(newPosition)
      #if symbol is Symbol.SYMBOL_LIST :
      if symbol not in Symbol.SYMBOL_LIST_ACTION_ALLOWED :
         return False, "Action impossible sur cette position!"

      #------------------------------------------------------------------------
      # L'obstacle est positionne sur la carte. 
      #------------------------------------------------------------------------
      self._oCarte._setObstacle(oObstacle)

      if self._mode == 'premier'  :
         self._oCarte.display()
      status = False
      return status, notification
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def action2symbol(self, action) :
      """
         Cette commande permet de transcrire une action issue d'une commande de controle 
         en un symbole de la carte de jeu.
      """
      status = True
      symbol = None
      if action in Protocol.PLAY_ACTIONS :
         if action == 'M' :
            symbol = Symbol._symbolWall
         elif action == 'P' :         
            symbol = Symbol._symbolDoor
         elif action == 'X' :         
            symbol = Symbol._symbolExit
         else :
            self.mylog(" *** ERREUR : Labyrinth.action2symbol() Action= {} not yet implemented!".format(action))
            status = False
            symbol = None
      else :
         self.mylog(" *** ERREUR : Labyrinth.action2symbol() Unknown action= {}".format(action))
         status = False
         symbol = None
         
      return status, symbol
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------      
   def _set_gamersState(self, identifier, state) :
      """
         Cette methode enregistre l'etat d'un joueur, pour un joueur enregistre dans 
         le jeu.
      """
      if identifier in self._gamersQueue.values() :
         self._gamersState[identifier] = state
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------      
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
   def _set_gamer(self, identifier, symbol) :
      """
         Cette methode enregistre joueur dans le jeu.
         Le tour de jeu du joueur est definie par son ordre d'arrivee dans le jeu.
         
         L'identite d'un joueur est enregistree dans un dictonnaire sous la forme : {'identifier':symbol}
         L'ordre d'arrivee d'un joueur est enregistre dans un dictonnaire sous la forme : {'timestamp':identifier}
         
         Il y a donc une correspondance unique entre l'etat du joueur, son identifiant et son tour de jeu.
            *  timestamp <--> identifier 
            *                 identifier <--> symbol
            *                 identifier <--> state
         
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
   def _drop_gamer(self, identifier) :
      """
         Cette methode permet retirer un joueur du jeu.
         Le joueur est identifie par le parametre identifier
      """
      status = False
      for gamerKey in self._gamersQueue.keys():
         if identifier == self._gamersQueue[gamerKey]:
            del(self._gamersQueue[gamerKey])
            del(self._gamersSymbol[identifier])
            del(self._gamersState[identifier])
            self._gamersCount -= 1
            status = True
            break
      return status
      
   #---------------------------------------------------------------------------      
   
   #---------------------------------------------------------------------------      
   #
   #---------------------------------------------------------------------------      
   def setRandomRobotPosition(self, symbol) :
      """
         Positionne aleatoirement, sur la carte, le symbole d'un robot passe en parametre. 
         Retourne :
         * La position du robot.
      """
      playStatus = True
      randomPosition = (0,0,0)
      randomPosition = self._oCarte.getRandomPosition()
      if randomPosition == (0,0,0) :
         return None

      oRobot   = Robot(randomPosition, symbol)
      
      # Le robot est positionne sur la carte.
      self._oCarte._setObstacle(oRobot)


      # La position du robot est retournee.
      return oRobot.newPosition      
   #---------------------------------------------------------------------------      

