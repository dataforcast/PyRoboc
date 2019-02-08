#!/usr/bin/python3.5
#-*- coding: utf-8 -*-
import time
import unittest
import time
import random 

from util.TCPConnection  import *
from util.Mylog          import *

from core.LabyrinthState     import *
from core.RobotController    import *
from core.LabyrinthTCPServer import *

_debugServer  = False
_debugClient  = False
_debugTest    = False
_symbol = 'A'

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def LabyrinthTCPServer_start(debug=False, gamers=1, qserverAddress=None):
   #------------------------------------------------------------------------
   # Le serveur est initialise
   #------------------------------------------------------------------------
   card   = 2
   if qserverAddress is None :
      serverAddress = (TCPConnection.HOST, TCPConnection.PORT)
   else :
      serverAddress = qserverAddress
   
   oLabyrinthTCPServer = LabyrinthTCPServer(gamers, debug, passwd="roboc", pserverAddress=serverAddress)

   #------------------------------------------------------------------------
   # Le menu est force au choix de la carte 2
   #------------------------------------------------------------------------
   cardId = oLabyrinthTCPServer.oLabyrinth.menu(cardID=card)

   if(-1 == cardId) :
      return
   #------------------------------------------------------------------------
   # L'affichage de la carte est desactivee sur le serveur
   #------------------------------------------------------------------------
   oLabyrinthTCPServer.oCarte._isDisplayed = False

   #------------------------------------------------------------------------
   # Le serveur est lance dans un thread.
   #------------------------------------------------------------------------
   oLabyrinthTCPServer.start()
   print("\nLabyrinthe lance avec la carte= {}".format(cardId))
   return oLabyrinthTCPServer      
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def RobotController_serverHalt(oRobotController) :   
   """ Arrete le serveur auquel le contrleur de robot passe en parametre est connecte. """   

   #------------------------------------------------------------------------
   # Commande d'enregistrement du joueur dans le jeu.
   #------------------------------------------------------------------------
   

   #------------------------------------------------------------------------
   # Commande d'enregistrement du joueur dans le jeu.
   #------------------------------------------------------------------------
   command =  Protocol.CTRL_ACTIONS_START
   oRobotController.send(command)
   time.sleep(1)

   #------------------------------------------------------------------------
   # Envoie de la commande d'arret du serveur.
   # Le mot de passe est injecte dans la commande.
   #------------------------------------------------------------------------
   command = Protocol.CTRL_ACTIONS_HALT
   clearPasswd = "roboc"
   cipheredPasswd = hashlib.sha1(clearPasswd.encode()).hexdigest()
   command = command.capitalize()+"_"+cipheredPasswd

   oRobotController.send(command)
   time.sleep(1)
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def RobotController_start(isAuto = False, debug=False, symbol=None, port=None):
   #------------------------------------------------------------------------
   # Un joueur est initialise en mode automatique et lance dans un thread.
   # Dans le mode automatique la commande C est lance ue fois la connexion 
   # TCP avec le serveur etablie.
   #------------------------------------------------------------------------
   serverAddress = (TCPConnection.HOST,TCPConnection.PORT)
   if port is None :
      pass
   else :
      serverAddress = (TCPConnection.HOST,port)

   if symbol is None :
      symbol = _symbol
   else :
      pass 

   oRobotController = RobotController(None, symbol, mode='client', isAuto=isAuto, debug=debug, \
   pserverAddress=serverAddress)
   
   oRobotController.start()

   #------------------------------------------------------------------------
   # Attente du signal de passage du controle au joueur
   #------------------------------------------------------------------------
   while oRobotController.signalplaying is False :
      # En attente du signal d'enregistrement dans le jeu.
      #print("*** control() : Signal received = {}".format(oRobotController._startPlay))
      #print("*** control() : Signal received = {} / Thread state= {}".\
      #format(oRobotController._startPlay, oRobotController._state))

      if LabyrinthState.STATE_END_VALUE == LabyrinthState.STATE_MACHINE[oRobotController._state] : 
         break

   return oRobotController
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
class RobotControllerTest(unittest.TestCase) :
   """
      Cette classe permet de tester unitairement les services fournies 
      par la classe RobotController.
      Les tests portent sur : 
         * l'ensemble des commandes du jeu, 
         * l'ensemble des commandes de controle,
         * l'ensemble des commandes d'actions, percer une porte et murer,
         * l'ensemble des commandes d'actions etendues, comme poser une porte de sortie,
         * la commande de victoire,
         * la commande d'arret du serveur.
         
      Le serveur de jeu TCP est active et les commandes sont envoyees a ce dernier 
      via un objet de type RobotController.
   """
   nbTest=0
      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def setUp(self):
      """
      Pour chaque test unitaire, le joueur est enregistre.
      """
      print("\n-------------------------------------")
      print("*** INFO() : New test started : {} *** ".format(RobotControllerTest.nbTest))
      #print("\n Server state = {}".format(RobotControllerTest.oLabyrinthTCPServer._state))
      print("---------------------------------------\n")

      self._commandListMoove     = ['n','n10','s','s10','e','e10','o','o10','u','u10','d','d10']
      self._commandListRealMoove = ['n2','e2','s2','o2']
      self._commandListAction    = ['mn','ms','me','mo','pn','ps','pe','po', 'xn','xs','xe','xo']
      self._commandListActionNoExit = ['mn','ms','me','mo','pn','ps','pe','po']
      self._commandListControl = ['C','?','t']
      self._haltCommand = ['0']
      self._port = TCPConnection.PORT
      self._host = TCPConnection.HOST
      self._serverAddress = (self._host, self._port)
      self._mylog = Mylog(_debugTest)
      util.common.TRACKFLAG  = True
      RobotControllerTest.nbTest += 1
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def tearDown(self):
      pass 
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_1_robotcontroller_control(self) :
      """
      Cette fonction teste les commandes de controle du jeu.
      
      Le test est valide si le joueur est dans l'etat attendu.

      """
      status = True
      
      #------------------------------------------------------------------------
      # Le serveur de jeu est lance ; le port differe du test precedant pour 
      # eviter le desagreable message "address in use..."
      #------------------------------------------------------------------------
      gamers = 1      
      
      port = random.randint(1030, 65535-1)
      oLabyrinthTCPServer = LabyrinthTCPServer_start(debug=_debugServer, gamers=gamers,\
      qserverAddress=(TCPConnection.HOST, port))

      #------------------------------------------------------------------------
      # Le joueur est intialise et se connecte au serveur 
      #------------------------------------------------------------------------
      oRobotController = RobotController_start(debug=_debugClient, port=port)
      
      status = (oRobotController._state == LabyrinthState.STATE_WAIT_KEY)
      print("*** INFO :  (1.1) oRobotController._state= {}".format(oRobotController._state))

      self.assertTrue(status)
      
      #------------------------------------------------------------------------
      # Les commandes de deplacement sont testees.
      #
      # Si une commande de tchat se presente, elle est completee avec un message.
      # Dans ce cas de figure, le joueur s'envoie un message.
      #------------------------------------------------------------------------
      status = True
      for index, command in enumerate(self._commandListControl)  :
         command = self._commandListControl[index]
         if command.upper() == Protocol.CTRL_ACTIONS_TCHAT :
            command = command.upper() + " "+_symbol+" Hello world"
            print("\n*** test_robotcontroller_control() :Command= {}\n".format(command))
         oRobotController.send(command)
         time.sleep(1)
         
      #------------------------------------------------------------------------
      # Le joueur quitte le jeux
      #------------------------------------------------------------------------      
      command = Protocol.CTRL_ACTIONS_LEAVE
      oRobotController.send(command)
      
      oRobotController.join()
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY) 
      print("*** INFO :  (1.2) oRobotController._state= {}".format(oRobotController._state))
      
      self.assertTrue(status)

      #------------------------------------------------------------------------
      # Un joueur entre dans le jeux pour y mettre fin en arretant le serveur.
      #------------------------------------------------------------------------      
      oRobotController = RobotController_start(debug=_debugClient, port=port)
      oRobotController._debug=False

      #------------------------------------------------------------------------
      # Le joueur arrete le jeu
      #------------------------------------------------------------------------      
      RobotController_serverHalt(oRobotController)
      oRobotController.join()
      oLabyrinthTCPServer.join()

      print("*** INFO :  (1.3) oRobotController._state= {}".format(oRobotController._state))
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY) 
      
      self.assertTrue(status)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_2_robotcontroller_moove(self) :
      """
      Cette fonction test les commandes de jeu pour le deplacement d'un robot.
      
      Le test est valide si le joueur passe dans les etats attendus.

      """
      status = True
      #------------------------------------------------------------------------
      # Le serveur de jeu est lance 
      #------------------------------------------------------------------------
      gamers = 1      
      port = random.randint(1030, 65535-1)
      oLabyrinthTCPServer = LabyrinthTCPServer_start(debug=_debugServer, gamers=gamers,\
      qserverAddress=(TCPConnection.HOST, port))


      #------------------------------------------------------------------------
      # Le joueur est intialise 
      #------------------------------------------------------------------------
      oRobotController = RobotController_start(debug=_debugClient, port=port)

      #------------------------------------------------------------------------
      # Commande d'enregistrement du joueur dans le jeu.
      #------------------------------------------------------------------------
      command =  Protocol.CTRL_ACTIONS_START
      oRobotController.send(command)
      time.sleep(1)

      print("*** INFO :  (2.1) oRobotController._state= {}".format(oRobotController._state))


      status = (oRobotController._state == LabyrinthState.STATE_PLAY_KEY) or \
      (oRobotController._state == LabyrinthState.STATE_PLAYING_KEY) or \
      (oRobotController._state == LabyrinthState.STATE_READY_KEY) 
      self.assertTrue(status)
      
       
      #------------------------------------------------------------------------
      # Les commandes de deplacement sont testees.
      #------------------------------------------------------------------------
      status = True
      for index, command in enumerate(self._commandListMoove)  :
         command = self._commandListMoove[index]
         oRobotController.send(command)
         time.sleep(1)

      #------------------------------------------------------------------------
      # Le joueur quitte le jeux
      #------------------------------------------------------------------------      
      command = Protocol.CTRL_ACTIONS_LEAVE
      oRobotController.send(command)
      time.sleep(1)
      
      oRobotController.join()
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY) or \
      (oRobotController._state == LabyrinthState.STATE_WAIT_KEY)
      print("*** INFO :  (2.2) oRobotController._state= {}".format(oRobotController._state))
      
      self.assertTrue(status)

      #------------------------------------------------------------------------
      # Un joueur entre dans le jeux pour y mettre fin en arretant le serveur.
      #------------------------------------------------------------------------      
      oRobotController = RobotController_start(debug=_debugClient, port=port)

      #------------------------------------------------------------------------
      # Commande d'arret du serveur.
      #------------------------------------------------------------------------
      RobotController_serverHalt(oRobotController)
      oRobotController.join()
      oLabyrinthTCPServer.join()
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY) 


      print("*** INFO :  (2.3) oRobotController._state= {}".format(oRobotController._state))
      self.assertTrue(status)

   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_4_robotcontroller_win(self) :
      """
       Ce test valide la commmande WIN.
       Cette commande force la victoire pour le joueur qui l'emet.
       
       Le test est valide si le joueur est dans l'etat attendu une fois 
       la commade traitee par le serveur.

       Le serveur envoie une commande d'arret au serveur.
      """
      status = True
      #------------------------------------------------------------------------
      # Le serveur de jeu est lance 
      #------------------------------------------------------------------------
      gamers = 1      
      port = random.randint(1030, 65535-1)
      oLabyrinthTCPServer = LabyrinthTCPServer_start(debug=_debugServer, gamers=gamers,\
      qserverAddress=(TCPConnection.HOST, port))

      #------------------------------------------------------------------------
      # Le joueur est intialise 
      #------------------------------------------------------------------------
      oRobotController = RobotController_start(debug=True, port=port)
      oRobotController._debug = False

      print("*** INFO : (4.0) oRobotController._state= {}".format(oRobotController._state))      
      status = (oRobotController._state == LabyrinthState.STATE_WAIT_KEY) 
      self.assertTrue(status)

      #------------------------------------------------------------------------
      # Commande d'enregistrement du joueur dans le jeu.
      #------------------------------------------------------------------------
      command =  Protocol.CTRL_ACTIONS_START
      oRobotController.send(command)
      time.sleep(1)
      
      print("*** INFO : (4.1) oRobotController._state= {}".format(oRobotController._state))      
      status = (oRobotController._state == LabyrinthState.STATE_PLAY_KEY) or \
      (oRobotController._state == LabyrinthState.STATE_PLAYING_KEY)
      self.assertTrue(status)

      
      #------------------------------------------------------------------------
      # Le joueur quitte le jeux en forcant la victoire.
      #------------------------------------------------------------------------      
      command = Protocol.CTRL_ACTIONS_WIN
      clearPasswd = "roboc"
      cipheredPasswd = hashlib.sha1(clearPasswd.encode()).hexdigest()
      command = command.capitalize()+"_"+cipheredPasswd
      oRobotController.send(command)
      time.sleep(1)
      
      oRobotController.join()      
      print("*** INFO : (4.2)  oRobotController._state= {}".format(oRobotController._state))      
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY)
      
      #------------------------------------------------------------------------
      # Un joueur entre dans le jeux pour y mettre fin en arretant le serveur.
      #------------------------------------------------------------------------      
      oRobotController = RobotController_start(debug=_debugClient, port=port)

      #------------------------------------------------------------------------
      # Commande d'arret du serveur.
      #------------------------------------------------------------------------
      RobotController_serverHalt(oRobotController)
      oRobotController.join()
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY) 
      
      oRobotController.join()      
      oLabyrinthTCPServer.join()
      print("*** INFO : (4.3)  oLabyrinthTCPServer._isServerHalted= {}".\
      format(oLabyrinthTCPServer._isServerHalted))      
      
      self.assertTrue(status)
   #---------------------------------------------------------------------------
   
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_5_robotcontroller_halt(self) :
      """
       Ce test valide la commmande d'arret du serveur.
       Cette commande force la victoire pour le joueur qui l'emet.
       Le test est valide si : 
         *  le joueur passe dans les etats attendus.
         *  le serveur est dans l'etat arrete une fois la commande d'arret traitee.
      """
      status = True
      #------------------------------------------------------------------------
      # Le serveur de jeu est lance 
      #------------------------------------------------------------------------
      gamers = 1      
      port = random.randint(1030, 65535-1)
      oLabyrinthTCPServer = LabyrinthTCPServer_start(debug=_debugServer, gamers=gamers,\
      qserverAddress=(TCPConnection.HOST, port))
      
      #------------------------------------------------------------------------
      # Le joueur est intialise 
      #------------------------------------------------------------------------
      oRobotController = RobotController_start(debug=_debugClient, port=port)
      
      #------------------------------------------------------------------------
      # Le joueur arrete le jeu
      #------------------------------------------------------------------------      
      RobotController_serverHalt(oRobotController)
      
      oLabyrinthTCPServer.join()
      oRobotController.join()

      print("\n*** INFO : (5.2) Server halt status = {} ***\n".format(oLabyrinthTCPServer._isServerHalted))
      self.assertTrue(oLabyrinthTCPServer._isServerHalted is True)
      
      print("\n*** INFO : (5.3) Client state = {} ***\n".format(oRobotController._state))
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY)
      self.assertTrue(status)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_6_robotcontroller_auto_moove(self) :
      """
      Cette fonction test les commandes de jeu pour le deplacement d'un robot 
      qui demarre automatiquement une partie en reseau.
      Le robot est identifie avec le symbole F.
      
      Le test est valide si le joueur passe dans les etats attendus.

      """
      status = True
      #------------------------------------------------------------------------
      # Le serveur de jeu est lance 
      #------------------------------------------------------------------------
      gamers = 1      
      port = random.randint(1030, 65535-1)
      oLabyrinthTCPServer = LabyrinthTCPServer_start(debug=_debugServer, gamers=gamers,\
      qserverAddress=(TCPConnection.HOST, port))


      #------------------------------------------------------------------------
      # Le joueur est intialise 
      #------------------------------------------------------------------------
      oRobotController = RobotController_start(debug=_debugClient, port=port, isAuto=True, symbol='F')

      print("*** INFO :  (6.1) oRobotController._state= {}".format(oRobotController._state))

      status = (oRobotController._state == LabyrinthState.STATE_PLAY_KEY) or \
      (oRobotController._state == LabyrinthState.STATE_PLAYING_KEY) or \
      (oRobotController._state == LabyrinthState.STATE_READY_KEY) 
      self.assertTrue(status)
      
       
      #------------------------------------------------------------------------
      # Les commandes de deplacement sont envoyees au server.
      #------------------------------------------------------------------------
      status = True
      for index, command in enumerate(self._commandListMoove)  :
         command = self._commandListMoove[index]
         oRobotController.send(command)
         time.sleep(1)

      #------------------------------------------------------------------------
      # Le joueur quitte le jeux
      #------------------------------------------------------------------------      
      command = Protocol.CTRL_ACTIONS_LEAVE
      oRobotController.send(command)
      time.sleep(1)
      
      oRobotController.join()
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY)
      print("*** INFO :  (6.2) oRobotController._state= {}".format(oRobotController._state))
      
      self.assertTrue(status)

      #------------------------------------------------------------------------
      # Un joueur entre dans le jeux pour y mettre fin en arretant le serveur.
      #------------------------------------------------------------------------      
      oRobotController = RobotController_start(debug=_debugClient, port=port)

      #------------------------------------------------------------------------
      # Commande d'arret du serveur.
      #------------------------------------------------------------------------
      RobotController_serverHalt(oRobotController)

      oRobotController.join()
      oLabyrinthTCPServer.join()

      status = (oRobotController._state == LabyrinthState.STATE_END_KEY) 
      self.assertTrue(status)
      
      status = oLabyrinthTCPServer._isServerHalted 
      self.assertTrue(status)

      print("*** INFO :  (6.3) oRobotController._state= {}".format(oRobotController._state))
      self.assertTrue(status)

   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_7_robotcontroller_actions(self) :
      """
      Cette fonction test les commandes d'actions sur les obstacles.
      Le robot du joueur est identifie avec le symbole Z.
      Pour ce faire, l'application client du joeur est lancee en mode automatique 
      et le symbole Z lui est assigne.
      
      Le test est valide si le joueur passe dans les etats attendus.
      """
      status = True
      #------------------------------------------------------------------------
      # Le serveur de jeu est lance 
      #------------------------------------------------------------------------
      gamers = 1      
      port = random.randint(1030, 65535-1)
      oLabyrinthTCPServer = LabyrinthTCPServer_start(debug=_debugServer, gamers=gamers,\
      qserverAddress=(TCPConnection.HOST, port))


      #------------------------------------------------------------------------
      # Le joueur est intialise 
      #------------------------------------------------------------------------
      oRobotController = RobotController_start(debug=_debugClient, port=port, isAuto=True, symbol='Z')

      print("*** INFO :  (7.1) oRobotController._state= {}".format(oRobotController._state))

      status = (oRobotController._state == LabyrinthState.STATE_PLAY_KEY) or \
      (oRobotController._state == LabyrinthState.STATE_PLAYING_KEY) or \
      (oRobotController._state == LabyrinthState.STATE_READY_KEY) 
      self.assertTrue(status)
      
       
      #------------------------------------------------------------------------
      # Les commandes d'actions sont envoyees au server.
      #------------------------------------------------------------------------
      status = True
      for index, command in enumerate(self._commandListAction)  :
         command = self._commandListAction[index]
         oRobotController.send(command)
         time.sleep(1)

      #------------------------------------------------------------------------
      # Le joueur quitte le jeux
      #------------------------------------------------------------------------      
      command = Protocol.CTRL_ACTIONS_LEAVE
      oRobotController.send(command)
      time.sleep(1)
      
      oRobotController.join()
      status = (oRobotController._state == LabyrinthState.STATE_END_KEY)
      print("*** INFO :  (7.2) oRobotController._state= {}".format(oRobotController._state))
      
      self.assertTrue(status)

      #------------------------------------------------------------------------
      # Un joueur entre dans le jeux pour y mettre fin en arretant le serveur.
      #------------------------------------------------------------------------      
      oRobotController = RobotController_start(debug=_debugClient, port=port)

      #------------------------------------------------------------------------
      # Commande d'arret du serveur.
      #------------------------------------------------------------------------
      RobotController_serverHalt(oRobotController)

      oRobotController.join()
      oLabyrinthTCPServer.join()

      status = (oRobotController._state == LabyrinthState.STATE_END_KEY) 
      self.assertTrue(status)
      
      status = oLabyrinthTCPServer._isServerHalted 
      self.assertTrue(status)

      print("*** INFO :  (7.3) oRobotController._state= {}".format(oRobotController._state))

   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_8_robotcontroller_gamers(self) :
      """ 
      Ce test valide le jeu a plusieurs joueurs. Au moins 5 symboles de robot sont 
      positionnes sur la carte. Un jeu de commandes de deplacement est envoye a chacun d'eux.
      Un jeu d'actions consistant a poser des murs et percer des portes est envoye a chacun d'eux.
           
      Pour terminer le jeu, un des robots pose une porte de sortie et passe cette porte.
      Le seveur de jeu est ensuite arrete.
      
      Le test est valide si : 
         * les etats de chacun des joueurs est aux valeurs attendues.
         * serveur est dans l'etat HALTED a la fin du test.

      """

      symbolList = list()
      symbolList.append('A')
      symbolList.append('=')
      symbolList.append('#')
      symbolList.append('@')
      symbolList.append('!')
      symbolList.append(':')
      symbolList.append('1')
      symbolList.append('2')
      symbolList.append('3')
      symbolList.append('4')
         
      gamers = len(symbolList)
      
      port = random.randint(1030, 65535-1)
      oLabyrinthTCPServer = LabyrinthTCPServer_start(debug=_debugServer, gamers=gamers,\
      qserverAddress=(TCPConnection.HOST, port))
      status = True

      #------------------------------------------------------------------------
      # Les joueurs sont intialises 
      #------------------------------------------------------------------------
      oRobotControllerList = list()
      for symbol in symbolList :
         oRobotController = RobotController_start(debug=_debugClient, isAuto=True, symbol=symbol, port=port)
         oRobotControllerList.append(oRobotController)
         time.sleep(0.5)
         
      lastGamer = len(oRobotControllerList) - 1
      
      for oRobotController in oRobotControllerList :
         #------------------------------------------------------------------------
         # Les notifications ne sont pas affichees 
         #------------------------------------------------------------------------
         oRobotController._isNotificationDisplayed = False
         #------------------------------------------------------------------------
         # La carte du jeu n'est pas affichee au travers d'un joueur.
         #------------------------------------------------------------------------
         oRobotController._isCardDisplayed         = False
      
      ind = 0
      
      # Le status est wait ou ready
      if False :
         for oRobotController in oRobotControllerList :
            status = status and ((oRobotController._state==LabyrinthState.STATE_READY_KEY) or \
             (oRobotController._state==LabyrinthState.STATE_PLAY_KEY))
             
            print("*** INFO : (8.0) oRobotController[{}]._state= {}".format(ind, oRobotController._state))      
            ind += 1

      self.assertTrue(status) 

      #------------------------------------------------------------------------
      # Affichage de la carte par le biais d'un joueur.
      #------------------------------------------------------------------------
      oRobotControllerList[0]._isCardDisplayed=True


      ind = 0
      for oRobotController in oRobotControllerList :
         print("*** INFO : (8.1) oRobotController[{}]._state= {}".format(ind, oRobotController._state))      
         ind += 1
      
      #------------------------------------------------------------------------
      # Les joueurs jouent tour a tour la liste de commandes de jeu 
      #------------------------------------------------------------------------      
      for index, command in enumerate(self._commandListActionNoExit)  :
         for oRobotController in oRobotControllerList :
            oRobotController.send(command)
            time.sleep(0.5)


      for index, command in enumerate(self._commandListRealMoove)  :
         for oRobotController in oRobotControllerList :
            oRobotController.send(command)
            time.sleep(0.5)

      #------------------------------------------------------------------------
      # Un des joueurs gagne la partie; la victoire est forcee
      #------------------------------------------------------------------------            
      # Une porte de sortie est posee au sud du 1er joueur
      command = "XS"
      oRobotControllerList[0].send(command)
      time.sleep(1)

      #------------------------------------------------------------------------
      # Les joueurs jouent leur tour en se deplacant au sud, y compris le gagnant 
      # qui a pose une sortie a cet effet.
      #------------------------------------------------------------------------            
      command = 'S'
      for oRobotController in oRobotControllerList :
         oRobotController.send(command)
         time.sleep(0.5)

      #------------------------------------------------------------------------
      # La carte n'est plus affichee
      #------------------------------------------------------------------------
      #oRobotControllerList[0]._isCardDisplayed=True

      #------------------------------------------------------------------------
      # Les traces pour ce joueur sont (des)activees.
      #------------------------------------------------------------------------
      oRobotControllerList[0]._debug=False

      #------------------------------------------------------------------------
      # Les traces du serveur sont (des)activees avant la reception de l'arret du serveur.
      #------------------------------------------------------------------------
      oLabyrinthTCPServer.oLabyrinth._debug = False

      #------------------------------------------------------------------------
      # Le joueur 1 franchit la porte de sortie posee au sud et gagne la partie
      #------------------------------------------------------------------------
      command = "S"
      oRobotControllerList[0].send(command)
      time.sleep(1)


      #------------------------------------------------------------------------
      # les threads se synchronisent.
      #------------------------------------------------------------------------
      for oRobotController in oRobotControllerList :
         oRobotController.join()

      ind = 0
      for oRobotController in oRobotControllerList :
         print("*** INFO : (8.2) oRobotController[{}]._state= {}".format(ind, oRobotController._state))      
         ind += 1

      for oRobotController in oRobotControllerList :
         status = status and ((oRobotController._state==LabyrinthState.STATE_END_KEY))

      self.assertTrue(status)

      #------------------------------------------------------------------------
      # Un joueur entre dans le jeux pour y mettre fin en arretant le serveur.
      #------------------------------------------------------------------------      
      oRobotController = RobotController_start(debug=_debugClient, port=port)

      #------------------------------------------------------------------------
      # Commande d'arret du serveur.
      #------------------------------------------------------------------------
      RobotController_serverHalt(oRobotController)

      oRobotController.join()
      oLabyrinthTCPServer.join()

      status = (oRobotController._state == LabyrinthState.STATE_END_KEY) 
      self.assertTrue(status)
      
      status = oLabyrinthTCPServer._isServerHalted 
      self.assertTrue(status)

      print("*** INFO :  (8.3) oRobotController._state= {}".format(oRobotController._state))

   #---------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
