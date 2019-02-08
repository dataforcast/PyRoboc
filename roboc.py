#!/usr/bin/python3.5
#-*-coding:Latin-1 -*
##-*- coding: utf-8 -*-
import argparse
import core
import os
import hashlib

import util 

from util.common     import *
from util.Mylog import *
from core.Labyrinth import *
from core.LabyrinthServer import *
from core.LabyrinthTCPServer import *

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def roboc(mode='client', gamers=1, debug=False, isGUI=False, host=None, \
          port=None, symbol=None, isAuto=False, passwd="roboc"):
   """ 
      Cette fonction est le point d'entree principal du jeu du labyrinthe. 
      Elle presente au.a la joueu.r.se le menu du jeu et active le jeu du labyrinthe.
      Les cartes du jeu sont stockees dans le repertoire 'cartes'.
      
      ------------------------------------------------------------------
      - Le fichier README.txt detaille l'utilisation de l'application. -
      ------------------------------------------------------------------

      Fonctionnement :  
      ---------------
      --> Lancez le jeu: 
          * python roboc.py -h pour afficher toutes les options 

         1) En mode serveur pour N joueurs:
            --> python roboc.py -s -n N
      
         2) En mode client:
            Il est donné la possibilité au joueur de choisir son symbole de robot.
            De cette façon, il lui est possible de tchater avec un joueur qui aura fait de même.

      * Lancement de base avec l'adresse réseau par défaut: Host=127.0.0.1 , Port= 2000
         --> python roboc.py -c
         Dans ce mode, lorsque le client est connecté au serveur, il faut envoyer la commande C pour démarrer le jeux.
         L'adresse réseau par défaut est définie dans la classe TCPConnection. 
         Sa valeur est :  (IP, Port) = (127.0.0.1,2000)

      * Lancement de base en choisissant l'adresse réseau :
         --> python roboc.py -c -H 127.0.0.1 -P 5000
         
         Il convient alors de lancer le serveur avec les options minimum :
         --> python roboc.py -s -H 127.0.0.1 -P 5000
      
      * Pour choisir le symbole du robot (ici, @ pour l'exemple), demarrage en mode manuel :
         --> python roboc.py -c -r @
         Dans ce mode, lorsque le joeur est connecté, il doit envoyer la commande C pour démarrer le jeux.

      * Pour choisir le symbole du robot (ici, @ pour l'exemple), demarrage en mode automatique :
         --> python roboc.py -c -r @ -a
         Dans ce mode,  une fois la connection avec le serveur établie, la commande C est envoyée 
         automatiquement pour démarrer le jeux.
   
      Quelques regles du jeu
      ----------------------
         --> '?' permet d'avoir un rafraîchissement de la carte
         --> Deplacez vous dans le labyrinthe jusqu'a la sortie modelise par le symbole 'U'
         --> Si le robot rencontre un mur lors de son deplacement, 
             il revient a sa position originale, la position avant son deplacement.
         --> Si le deplacement du robot est commande hors des limites du labyrinthe, 
             il revient a sa position originale, la position avant son deplacement.
         --> Le jeu se termine une fois la sortie atteinte. 
         --> Il est possible d'interrompre une partie a tout moment. Vous pourrez reprendre cette partie en 
             relancant le jeu.
   """
   isGUI = False

   if symbol is None :
      symbol = 'X'

   mylog = Mylog(debug=debug)

   Protocol.CURRENT_MODE = mode

   if mode == 'client' :
      oRobotController = RobotController(None, symbol, mode, debug=debug, isGUI=isGUI,isAuto=isAuto, pserverAddress=(host, port))
      oRobotController.start()
      oRobotController.control()      
      oRobotController.join()      

   elif mode == 'server' :
      status = False
      symbol = 'L'    

      oLabyrinthTCPServer = LabyrinthTCPServer(gamers, debug, passwd=passwd, pserverAddress=(host,port))
      
      cardId = oLabyrinthTCPServer.menu()
      if(-1 == cardId) :
         return
      
      print("\nLabyrinthe lance avec la carte= {}".format(cardId))
      oLabyrinthTCPServer.start()
      oLabyrinthTCPServer.join()

   elif mode == 'premier' :
      mylog.mylog("\n *** Mode= {} ***".format(mode))
      labyrinth = Labyrinth(mode='premier',debug=debug)

      carteId   = labyrinth.menu()
      if(-1 == carteId) :
         return
      mylog.mylog("\n *** Labyrinth mode= {} ***".format(labyrinth._mode))
      ret = labyrinth.play()
      
   else :
      mylog.mylog("Mode de jeu inconnu : {}".format(mode))
#---------------------------------------------------------------------------


parser = argparse.ArgumentParser(prog='roboc',description="*** Jeu du labyrinthe Version 2.0 ***")

parser.add_argument("-s", "--server",  action="store_true",  help="Activer le serveur.")
parser.add_argument("-w", "--passwd",  type=str,  help="Mot de passe du serveur (roboc par defaut)")
parser.add_argument("-H", "--host",    type=str,  help="Adresse IP du serveur")
parser.add_argument("-P", "--port",    type=int,  help="Port reseau du serveur")
parser.add_argument("-c", "--client",  action="store_true",  help="Mode joueur ")
parser.add_argument("-g", "--graphique", action="store_true",   help="Interface graphique")
parser.add_argument("-n",  type=int,   help="Nombre de joueur(s), 1 par defaut")
parser.add_argument("-r",  type=str,   help="Symbole du robot pour le joueur")
parser.add_argument("-a", "--auto",action="store_true",   help="Demarrage du jeu en mode automatique")
parser.add_argument("-p", "--premier", action="store_true",  help="Mode premier : jouer avec la 1ere version du robot.")
parser.add_argument("-d", "--debug",   action="store_true",  help="Option de debug")
parser.add_argument("-t", "--track",   action="store_true",  help="Option de tracking des appels de fonctions")


args = parser.parse_args()

#-----------------------------------------------------------------
# Initialisation des paramètres de debug
#-----------------------------------------------------------------
Mylog._debug  = args.debug
util.common.TRACKFLAG  = args.track
#-----------------------------------------------------------------


mylog = Mylog()   

mylog.mylog("\nArguments de roboc() par defaut : {}\n".format(args))

if args.n is not None :
   gamers = args.n
else :
   gamers = 1



if util.common.TRACKFLAG is True :
   try :
      os.remove("log/*.txt")
   except FileNotFoundError :
      pass

if args.r is not None :
   symbol = args.r
else :
   symbol = 'X'    

if args.passwd is None :
   args.passwd = "roboc"
else :
   pass


# -----------------------------------------------------------------------------
# Lancement du jeu
# -----------------------------------------------------------------------------
if args.client is True :
   roboc(mode='client', debug=args.debug, symbol=symbol, isGUI=args.graphique, isAuto=args.auto, host=args.host, port=args.port)
elif args.premier is True :
   roboc(mode='premier', debug=args.debug, isGUI=args.graphique)
elif args.server is True :
   roboc(mode='server', gamers=gamers, debug=args.debug, isGUI=args.graphique, host=args.host, port=args.port,\
    passwd=args.passwd)
else :
   print("\n*** ERREUR : aucune des options -h -c, -p, -s n'est precisee (-h pour l'aide): {}\n")

