#!/usr/bin/python3.5
#-*- coding: utf-8 -*-
import time
import unittest
from test.util.test_util import *
from socketserver import BaseRequestHandler 
from util.Protocol import *
from util.Mylog import *
from util.common import *


class ProtocolTest(unittest.TestCase,Mylog) :
   """
      Cette classe permet de tester unitairement l'ensemble des services fournies 
      par la classe Protocol.
      Ces services sont :
         * Le formatage et la verification des commandes de deplacement d'un robot, dans toutes les directions.
         * Le formatage et la verification des commandes d'action sur les obstacles, dans toutes les directions.
         * Le traitement des commandes erronees.

      5 tests unitaires sont deroules.
   """
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def setUp(self):
      """Initialisation des tests."""
      self.commandList=['n','n10','n0','s','s10','e','e10','o','o10','u','u10','d','d10','mn','ms','me','mo']
      self.commandList.append('pn')
      self.commandList.append('ps')
      self.commandList.append('pe')
      self.commandList.append('po')

      self.commandCtrlList=['c','C','?','T']
      self.invalidCommandCtrlList=['.','','A','@']


      self.invalidCommandList=['A','10n','b','10s','10e','h','10o','zE','10u','F','10d','nm','sm','em','om']
      self.invalidCommandList.append('np')
      self.invalidCommandList.append('sp')
      self.invalidCommandList.append('ep')
      self.invalidCommandList.append('op')
      self.invalidCommandList.append('')
      self.invalidCommandList.append('erpoer')
      self.invalidCommandList.append(' e')
      self.invalidCommandList.append('O ')
      self.invalidCommandList.append('23 ')
      self.invalidCommandList.append('32')
      
      self.commandStart='c'
      
      self.debug = False
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_send_primary_validCmd(self) :
      """
         Teste : 
         * le protocole des messages pour jouer 
         * le service d'envoi des messages en version premiere.

         Le test est valide si les conditions suivantes sont satisfaites :
          1) Le message est formate conformement aux specifications
          2) Un message est renvoye par le serveur.
          
          
          Pre-requis: aucun
          
      """
      # 'T' pour test
      symbol    = 'T'

      # L'emetteur et le recepteur sont le meme objet; 
      oProtocol = Protocol(symbol,mode='premier', debug=self.debug)
   

      # Les commandes valides simulees sont testees
      status = True
      for index, command in enumerate(self.commandList)  :
         command = self.commandList[index]
         message = oProtocol.send(command)
         status = status and message['status']
         if message['status'] is False :
            #print("\n*** test_send_primary() : {}\n".format(message['notify']))
            pass

      self.assertTrue(status)
            
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_send_primary_invalidCmd(self) :
      """
         Teste : 
         * le protocole des messages pour jouer 
         * le service d'envoi des messages en version premiere.

         Le test est valide si les conditions suivantes sont satisfaites :
          1) Le message est formate conformement aux specifications
          2) Un message est renvoye par le serveur.
          
          
          Pre-requis: aucun
          
      """
      # 'T' pour test
      symbol    = 'T'

      # L'emetteur et le recepteur sont le meme objet; 
      oProtocol = Protocol(symbol, mode='premier', debug=self.debug)
   

      # Les commandes invalides simulees sont testees
      status = True
      for index, command in enumerate(self.invalidCommandList)  :
         command = self.invalidCommandList[index]
         message = oProtocol.send(command)
         #print("\n*** test_send_primary() : commande invalide: message retour= {}\n".format(message))
         if message['status'] is True :
            #print("\n*** test_send_primary() : commande invalide detectee comme valide : {}\n".format(command))
            status = True
            break;
         else : 
            status = status and message['status']            

      self.assertFalse(status)

      
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_send_primary_validCtrl(self) :
      """
         Teste : 
         * le protocole des messages de controle
         * le service d'envoi des messages en version premiere.
          
      """
      # 'T' pour test
      symbol    = 'T'

      # L'emetteur et le recepteur sont le meme objet; 
      oProtocol = Protocol(symbol,mode='premier', debug=self.debug)
   

      # Les commandes invalides simulees sont testees
      status = True
      for index, command in enumerate(self.commandCtrlList)  :
         command = self.commandCtrlList[index]
         if command.startswith(Protocol.CTRL_ACTIONS_TCHAT) or \
              command.startswith(Protocol.CTRL_ACTIONS_TCHAT.capitalize()) :
              command = command +" "+symbol+" Hello World!"
         message = oProtocol.send(command)
         if message['status'] is False :
            print("\n*** ERREUR : test_send_primary_validCtrl() : Test invalide pour la commande= {}\n".format(command))
         status = status and message['status']            
         
      #Pour enregistrer les traces d'appels de fonctions dans le fichier log/client_calltrack_sorted.txt
      client_tracker_print()
      self.assertTrue(status)
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_send_primary_invalidCtrl(self) :
      """
         Teste : 
         * le protocole des messages de controle
         * le service d'envoi des messages en version premiere.
         Le test est valide si les conditions suivantes sont satisfaites :
          1) Le message est formate conformement aux specifications
          2) Un message est renvoye par le serveur.
          
         Le test est valide si tous les status retournes sont False          
      """
      # 'T' pour test
      symbol    = 'T'

      # L'emetteur et le recepteur sont le meme objet; 
      oProtocol = Protocol(symbol, mode='premier', debug=self.debug)
   

      # Les commandes invalides simulees sont testees
      status = False
      for index, command in enumerate(self.invalidCommandCtrlList)  :
         command = self.invalidCommandCtrlList[index]
         message = oProtocol.send(command)
         #print("\n*** test_send_primary() : commande invalide: message retour= {}\n".format(message))
         status = status or message['status']            

      #Pour enregistrer les traces d'appels de fonctions dans le fichier log/client_calltrack_sorted.txt
      client_tracker_print()
      self.assertFalse(status)
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_send_network(self) :
      """
         Teste le service Protococl.send en version reseau.
         Un message est envoye sans que le serveur ne soit demarre.
         
         Le test est valide si les conditions suivantes sont satisfaites :
          1) Le code de retour est faux
          
          Pre-requis: aucun
          
      """
      symbol = 'A'      
      oProtocol = Protocol(symbol,mode="client",debug=self.debug)
      command = "N200"
      message = oProtocol.send(command)
      #if message['status'] is False :
         #print("\n*** ERROR : test_send_network : {}".format(message['notify']))

      #Pour enregistrer les traces d'appels de fonctions dans le fichier log/client_calltrack_sorted.txt
      client_tracker_print()
      self.assertTrue( (message['status'] is not True) )

   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def notest_send_recv_network(self) :
      """
         Teste les services client / serveur de la classe Protocol.
         Le serveur TCP est initialise.
         
         Un serveur de type Protocol est instancie.
         Une classe MyHandler est construite et enregistree aupres du serveur 
         pour gerer les messages du client.
         Le serveur est active dans un thread en attente de reception d'un message.
         Le serveur renvoie le message au client avec la notification "Received".
         
         Un client de type Protocol est initialise et a et un message est envoye au serveur.
         
         Le test est valide si les conditions suivantes sont satisfaites :
          1) Le code de retour est vrai
          
          Pre-requis: aucun
          
      """

      # Demarrage du serveur
      symbol = 'S'      
      oProtocol_server = Protocol(symbol,mode="server",debug=self.debug)
      # tcpHandlerMethods est definie dans le module test.util.test_util
      tcpHandlerMethods["process"] = test_Protocol_process
      oProtocol_server.handlerRegister(tcpHandlerMethods)
      oProtocol_server.start()
      
      # Attente de l'etat actif du serveur.
      while oProtocol_server.isActivated is not True :
         time.sleep(1)

      # Toutes les commandes du protocole sont testees
      symbol = 'X'
      oProtocol_client = Protocol(symbol,mode="client", debug=self.debug)
      
      status = True
      # Les commandes entrees par le joueur sont simulees 
      for index, command in enumerate(self.commandList)  :
         command = self.commandList[index]
         message = oProtocol_client.send(command)
         # print("\n*** Received message= {}".format(message))
         status = status and message['status']
         if message['status'] is False :
            print("\n*** test_send_recv_network() : {}\n".format(message['notify']))

      # Le serveur est arrete
      oProtocol_server.shutdown()

      # Attend la terminaison des threads
      oProtocol_server.join()
      
      self.assertTrue( status )
      
      
   #---------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
