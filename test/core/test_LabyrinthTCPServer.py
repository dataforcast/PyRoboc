#!/usr/bin/python3.5
#-*- coding: utf-8 -*-
import time
import unittest
import telnetlib


from util.TCPConnection  import *
from util.Mylog          import *
from core.LabyrinthTCPServer import *
_debug  = False

class LabyrinthTCPServerTest(unittest.TestCase) :
   """
      Cette classe permet de tester unitairement l'ensemble des services fournies 
      par la classe RobotController.

   """

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def setUp(self):
      self._port = TCPConnection.PORT+1
      self._host = TCPConnection.HOST
      self.serverAddress = (self._host, self._port)
      self.mylog = Mylog(_debug)
      util.common.TRACKFLAG  = True

   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def notest_LabyrinthTCPServer_start(self) :
      """
         Ce test permet de valider le lancement du serveur de jeu.
      """
      status = False
      #------------------------------------------------------------------------
      # Le serveur est initialise
      #------------------------------------------------------------------------
      gamers = 1
      debug  = False
      card   = 2
      
      oLabyrinthTCPServer = LabyrinthTCPServer(gamers, debug, passwd="roboc" , pserverAddress=self.serverAddress)

      #------------------------------------------------------------------------
      # Le menu est force au choix de la carte 2
      #------------------------------------------------------------------------
      cardId = oLabyrinthTCPServer.oLabyrinth.menu(cardID=card)

      if(-1 == cardId) :
         return
      #------------------------------------------------------------------------
      # Le serveur est lance dans un thread.
      #------------------------------------------------------------------------
      oLabyrinthTCPServer.start()
      print("\nLabyrinthe lance avec la carte= {}".format(cardId))
      time.sleep(2)

      connection = telnetlib.Telnet(self._host,self._port)
      status = str(type(connection)).find('Telnet') > 0

      #------------------------------------------------------------------------
      # Le serveur est arrete violement
      #------------------------------------------------------------------------
      connection.write(b"stop")
      connection.close()
      oLabyrinthTCPServer.join()
      self.assertTrue(status)      
   
   #---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
