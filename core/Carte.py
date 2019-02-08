#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-
import os
import pickle
import util
import re
import random

from util.Outputdevice import *
from util.Mylog import *
from core.Robot import *
from core.Obstacle import *
from core.Symbol import *

class Carte(Outputdevice,Mylog) :
   """
      Cette classe modelise une carte du jeu du labyrinthe.
      Elle implemente les regles de ce jeu. Elle gere les deplacements du robot et les 
      interactions entre le robot et les differents obstacles positionnes sur la carte.

      Elle implemente les services permettant le contrôle du jeu : 
         --> le listage et le chargement des cartes enregistrees dans le repertoire 'cartes'
         --> le chargement d'une partie en cours enregistree dans le repertoire 'cartes/data'
         --> l'affichage de la carte lue
         --> la sauvegarde d'une partie en cours
         --> le rejeu d'une partie sauvegardee
         --> le deplacement, sur la carte, du robot qui lui est asscocie, conformement aux regles du jeu.
         --> le positionnement d'une porte ou d'un mur
         --> la purge dans le repertoire 'cartes/data'd'une partie gagnee

   """
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __init__(self,cardFolderName="cartes", debug=False) :
      """ Initialise l'objet avec les valeurs par defaut.
      \n Le parametre \"cardFolderName\" est le nom du repertoire ou sont entreposes les cartes du jeu.
      \n Le nom du repertoire par defaut est \"cartes\"." 
      \n """
      Outputdevice.__init__(self)
      Mylog.__init__(self, debug)
      self._listCarte = [] 
      self._listMax   = 0 
      self._loadedObstacle= [] #Contient le contenu de la carte chargee en memoire 
      self._cardExtension   = ".txt" # Extension des fichiers cartes.
      self._dataExtension   = ".data" #Extension des fichiers pour les cartes en cours de jeu
      self._cardFolderName  = cardFolderName
      self._dataFolderName  = self._cardFolderName+"/data/"
      self._symbolWall      = Symbol._symbolWall
      self._symbolEmpty     = Symbol._symbolEmpty
      self._symbolDoor      = Symbol._symbolDoor
      self._symbolExit      = Symbol._symbolExit
      self._symbolRobot     = Symbol._symbolRobot
      self._symbolMaried    = Symbol._symbolMaried
      self._symbolMask      =  []
      self._symbolMask.append(self._symbolEmpty)
      self._symbolMask.append(self._symbolEmpty)
      self._lineMax         = 0
      self._columnMax       = 0
      self._cardID          = -1
      self._isDisplayed     = True

   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __str__(self) :
      message  ="\nListe des cartes       = {}".format(self._listCarte)
      message +="\n Symboles en cache     = {}".format(self._symbolMask)
      message +="\nNom de la carte chargee= {}".format(self._cardFolderName)
      message +="\n(Lignes, Colonnes)     = ({},{})".format(self._lineMax,self._columnMax)
      return message
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #  Properties
   #---------------------------------------------------------------------------
   def _get_symbolWall(self) :
      return self._symbolWall

   def _get_symbolEmpty(self) :
      return self._symbolEmpty

   def _get_symbolDoor(self) :
      return self._symbolDoor

   def _get_symbolExit(self) :
      return self._symbolExit

   def _get_symbolRobot(self) :
      return self._symbolRobot

   def _get_lineMax(self) :
      return self._lineMax
   
   def _get_columnMax(self) :
      return self._columnMax


   def _set_isDisplayed(self, isDisplayable) :
      self._isDisplayed = isDisplayable

   def _set_symbolRobot(self, symbolRobot) :
      self._symbolRobot = symbolRobot

      
   symbolWall  = property(_get_symbolWall)
   symbolEmpty = property(_get_symbolEmpty)
   symbolDoor  = property(_get_symbolDoor)
   symbolExit  = property(_get_symbolExit)
   symbolRobot = property(_get_symbolRobot, _set_symbolRobot)      
   columnMax   = property(_get_columnMax)      
   lineMax     = property(_get_lineMax)      
   
   isDisplayed = property(_set_isDisplayed)      
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def getCardName(self,cardID) :
      """ 
      Retourne le nom formate d'une carte a partir de l'identifiant passe en 
      parametre.
      """
      status   = False
      cardName = ""
      if 0 > cardID  :
         return status, cardName
      
      status, cardName       = self._buildCardName(cardID)
      self._cardID   = cardID

      return status, cardName
   #---------------------------------------------------------------------------
   
   def getDataName(self,cardName):
      """ 
         Retourne, si elle existe, une partie du jeu en cours et qui 
         correspond au nom de la carte passee en argument.
      """
      dataName = cardName+self._dataExtension
      # Lecture de la liste des fichiers dans le repertoire data.
      listData = os.listdir(self._dataFolderName)
      
      # Verification de la correspondance d'un fichier data avec un fichier carte.
      if dataName in listData :
         return True, dataName
      return False,""      
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def displayList(self):
      """ Affiche les cartes disponibles.
      """   
      status = False
      self.setOutput("Liste des Cartes du jeu :\n")
      for carteId, carteName in enumerate(self._listCarte) :
         # Les noms sans l'extension ".txt" sont filtres
         if self._cardExtension in carteName :
            status, cardName     = self.getCardName(carteId)
            if False == status :
               pass
            self.setOutput(" Entrez {} : {}".format(carteId , cardName.capitalize()))
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def display(self):
      """ 
      Affiche sur un peripherique de sortie la carte chargee en memoire
      """   
      if self._isDisplayed is False :
         return
      self.mylog("Affichage de la carte chargee en memoire...")

      self.setOutput("\n")
      for line, symbolsLane in enumerate(self._loadedObstacle) :
         self.setOutput("{}".format(symbolsLane))
      self.setOutput("\n")

   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def readList(self):
      """
      Lit dans le systeme de fichiers, la liste des cartes disponibles.
      Les cartes sont recherchees dans le repertoire 'cartes'.
      Seuls les fichiers avec l'extension ".txt" sont retenues dans la liste des cartes
      """
      
      # Tous les fichiers dans le repertoire des cartes sont enregistres dans la liste 
      # des fichiers de cartes.
      self._listCarte = os.listdir(self._cardFolderName)

      # La liste des fichiers issus du repertoire des cartes est filtree.
      # Seuls les fichiers avec l'extension ".txt" sont retenus.
      for index,fileName in enumerate(self._listCarte) :
          if None == re.search(self._cardExtension,self._listCarte[index]):
            self._listCarte.pop(index)

      # La liste des cartes est triee pour rendre le menu plus coherent
      self._listCarte.sort()
      
      self._listMax   = len(self._listCarte)
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def _checkInput(self,strValue):
      """ 
      Verifie que l'identifiant selectionne est dans le rang des cartes possibles
      """  
      index = -1
      status = False
      if(strValue.isnumeric()):
         enteredCarteID = int(strValue)
         for carteId, carteName in enumerate(self._listCarte) :
            if(carteId == enteredCarteID) : 
               status = True
               break
      else:
         status = False
      return status
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def load(self,carteId):
      """ 
         Charge la carte dont l'indentifiant est passe en argument 
         Parametre : carteId l'identifiant de la carte selectionnee par la.le joueu.r.se.
      """
      # Recuperation du chemin d'acces a la carte dont la referecce est passee en parametre
      status,self._cardName = self.getCardName(carteId)
      self.mylog("\n Chargement de la carte= \""+self._cardName+"\" ...")
      fileName = self._cardFolderName+"/"+self._listCarte[carteId]
      self.mylog("*** load() : Fichier = "+fileName)
      try:
         with open(fileName,"r") as cardFile:
            self._loadedObstacle = cardFile.read().split("\n")


      except FileNotFoundError: 
         self.setOutput("\n *** ERREUR : fichier non trouve : "+fileName) 
         return   
      except NameError: 
         self.setOutput("\n *** ERREUR : nom de fichier inconnu : "+fileName)  
         return 

      # Calcul des bords de la carte
      index = 0
      for line,colum in enumerate (self._loadedObstacle) :
         if 0 < len(colum) :
            self._lineMax   = index 
            self._columnMax = max(len(colum)-1,self._columnMax) 
            index +=1
         
      self.mylog("\n Carte chargee! Bords = {}".format((self._lineMax,self._columnMax)))
      return            
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def loadParty(self,dataFile) :
      """ Charge en memoire une partie en cours."""
      fileName = self._dataFolderName+dataFile 
      status   = False
      data     = None
      try:
         with open(fileName,"rb") as dataFile:
            oUnpickler = pickle.Unpickler(dataFile)
            data = oUnpickler.load()
            status = True
      except FileNotFoundError: 
         self.setOutput("\n*** ERREUR : Partie en cours : fichier "+fileName+" introuvable!")
         status = False   
      
      self.mylog("\n*** loadParty() :")
      self.mylog(data)
      return status, data
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def cleanRobot(self) :
      """ Cette fonction efface de la carte tous les symboles 
          de robot."""
      # Le symbole du robot initialement dans la carte est efface.
      isPresent = True
      
      self.symbolRobot = Symbol._symbolRobot
      while isPresent is True :
         position  = self.getRobotPosition()
         if position is not None :
            # Une case vide est instanciee  a la position du robot.
            oObstacle = Obstacle(Symbol._symbolEmpty, position)
          
            # Le robot est efface de la carte 
            self._setObstacle(oObstacle)
         else : 
            isPresent = False
      self.display()
      
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def _getPosition(self,symbol) :
      """
      Retourne la position, sur la carte, du symbole passe en parametre.
      """
      high = 0
      for line, symbolsLane in enumerate(self._loadedObstacle) :
         if symbol in symbolsLane :
            column =  symbolsLane.find(symbol)
            return True, line,column,high #In fact, returns (Y,X,Z)
      return False,0,0,high         
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def getRobotPosition(self) : 
      """ 
         Recupere, sur la carte, la position du symbole du robot 
         associe a la carte.
         Ce symbole petu changer si les joueurs decident de jouer avec 
         leur propre symbole.
      """
      oObstacle = Obstacle(self._symbolRobot,[0,0,0])
      position  = self.getPosition(oObstacle)
      return position
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def getSymbol(self, position) :
      """
      Cette methode permet de retourner le symbole occupé par la position 
      passee en parametre.
      """
      line   = position[0]
      column = position[1]
      symbol = self._loadedObstacle[line][column]
      return symbol
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def getPosition(self,oObstacle) : 
      """ 
         Recherche, sur la carte, la position de l'obstacle passe en parametre.

         Retourne :
         * La position de l'obstacle, s'il existe a cette position.
         * None sinon.
      """
      symbol = oObstacle.symbol
      high   = 0
      for line, symbolsLane in enumerate(self._loadedObstacle) :
         if symbol in symbolsLane :
            column =  symbolsLane.find(symbol)
            oObstacle.newPosition = [line,column,high]
            return [line,column,high]
      return None
   #---------------------------------------------------------------------------
   
   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def _getObstacleList(self,oRobot) : 
      """ 
         Renvoie la liste d'obstacles sur la trajectoire du robot.
         La trajectoire du robot commence a oldPosition et se termine a newPosition.
      """
      
      symbol      = oRobot.symbol 
      
      newPosition = oRobot.newPosition 
      if self._symbolRobot == symbol :
         oldPosition = oRobot.oldPosition 
      else :
         oldPosition = newPosition

      status    = True
      jump      = 0
      direction = 'R'

      listObstacle = []
      
      if newPosition[0] == oldPosition[0] :
         # Deplacement horizontal, parcours des colonnes 
         line   = oldPosition[0]
         column = oldPosition[1] 
         
         if newPosition[1] >= oldPosition[1] :
            # Parcours dans le sens croissant des colonnes
            distance = newPosition[1] - oldPosition[1]
            jump     = 1
         else :
            # Parcours dans l'autre sens decroissant des colonnes
            distance = oldPosition[1] - newPosition[1]
            jump     = -1
            
         
         while distance > 0 :
            column   +=jump
            distance -=1
            position = (line,column)
            if self._checkPosition(position) :
               try :
                  symbol  = self._loadedObstacle[line][column]
                  oObstacle1 = Obstacle(symbol,position)
                  self.mylog("*** _getObstacleList() : Obstacle= {}".format(oObstacle1))
                  listObstacle.append(oObstacle1) 
                  if self._symbolWall == symbol :
                     # Un mur a ete atteint 
                     break
               except IndexError :
                  self.setOutput("*** ERREUR : position (ligne,colonne) = {}".format(newPosition))
                  status = False
            else :
               self.setOutput("*** ERREUR : Position hors cadre= {}".format(position))
               status = False
               break
      elif newPosition[1] == oldPosition[1] :
         # Deplacement vertical, parcours des lignes 
         line   = oldPosition[0]
         column = oldPosition[1]

         if newPosition[0] >= oldPosition[0] :
            # Parcours dans le sens croissant des lignes
            distance = newPosition[0] - oldPosition[0]
            jump     = 1
         else :
            # Parcours dans le sens decroissant des lignes
            distance = oldPosition[0] - newPosition[0]
            jump     = -1
            
         while distance > 0 :
            line   +=jump
            distance -=1
            position = (line,column)
            if self._checkPosition(position) :
               try :
                  symbol = self._loadedObstacle[line][column]
                  oObstacle1 = Obstacle(symbol,position)
                  self.mylog("*** _getObstacleList() : Obstacle= {}".format(oObstacle1))
                  listObstacle.append(oObstacle1) 
                  if self._symbolWall == symbol :
                     # Un mur a ete atteint 
                     break
                     #return symbol 
               except IndexError :
                  status = False
                  self.setOutput("*** ERREUR : position (ligne,colonne) = {}".format(newPosition))
                  #return ""
                  break
            else :
               #return symbol
               status = False
               self.setOutput("*** ERREUR : Position hors cadre= {}".format(position))
               break
      if False == status :
         # Erreur dans le calcule de la trajectoire; la liste des obstacles est videe
         listObstacle = []
         
      return status,listObstacle
   #---------------------------------------------------------------------------
 
   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def setPosition(self,oObstacle):
      """ 
      Positionne, sur la carte du jeu, l'obstacle (le robot) passe en parametre.
      La carte renvoie une notification sur l'etat du positionnement de l'obstacle. 

      Retourne True lorsque la sortie a ete atteinte.
      """
      output = False
      notification   = "Deplacement impossible!"
      
   
      self.mylog("*** setPosition() : After compute() oObstacle= {}".format(oObstacle))
   
      newPosition = oObstacle.newPosition
      symbol      = oObstacle.symbol
      
      #La nouvelle position du symbole est verifiee dans le cadre de la carte.
      #self.mylog("*** setPosition() : checking new position= {}".format(newPosition))
      if self._checkPosition(newPosition) :
         if Symbol._symbolRobot == oObstacle.symbol :
            if True == oObstacle.isRestState() :
               output,oObstacle,notification = self._swapObstacle(oObstacle,oObstacle)
               self.display()
         else :
            self.mylog("*** setPosition() : Symbol= {}".format(oObstacle.symbol))
               
         # La liste d'obstacles sur la trajectoire est recuperee
         status,listObstacle = self._getObstacleList(oObstacle)
         if True == status :            
            # Le deplacement est effectue 
            index      = 0
            self.mylog("*** setPosition() : list symbol length = "+str(len(listObstacle)))
            # Si l'obstacle peut se deplacer, le deplacement se fait selon la trajectoire
            # enregistree dans  listObstacle.
            # Dans le cas contraire, il s'agit d'un obstable immobile a positionner sur la carte.
            if oObstacle.moovable is True :
               while index < len(listObstacle) :
                  oObstacleToSwap = listObstacle[index]
                  output,oObstacle,notification = self._swapObstacle(oObstacle,oObstacleToSwap)

                  # Affichage de la carte a chaque deplacement.
                  self.display()                 
                  index +=1
            else :
               #Positionnement de l'obstacle sur la carte
               output,oObstacle,notification = self._setObstacle(oObstacle)
               
               
         else :
            # La position du robot ne s'est pas deplace: il est reinitialise a sa position originale
            self.mylog("*** setPosition() : _getObstacleList() FAILED! ")
            oObstacle.positionReset()
            self.display()                 

      else : 
         # La nouvelle position du robot sort des limites de la carte; la nouvelle position est abandonnee
         self.display()
         notification = "\n Trop loin! Pas de deplacement"
         
      return output, notification, oObstacle
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def _swapObstacle(self,oRobot,oObstacleToSwap) :
      """
         Echange la position sur la carte de deux obstacles. L'echange se fait selon les regles du jeu.
         
         --> Le remplacement de oObstacleToSwap par oRobot est realise si oObstacleToSwap est :
             * une case vide,
             * une porte,
             * la sortie,
             * tout autre obstacle franchissable,
         --> Le swap n'est pas realise si oObstacleToSwap est :
             * un mur

         oRobot se deplace case par case sur la carte. Cette derniere est re-affichee a chaque etape.
         Lorsque le swap n'est pas realise, oRobot revient a sa position de depart.
         
         Lorsque oRobot quitte sa position, l'obstacle qui occupait cette position avant le deplacement 
         du robot est reaffiche.
         
         Retourne le tuple (status,oRobot,notification)
         
         Evolution: l'interaction entre le robot et l'obstacle pourrait etre implemente dans le robot.
                    Les objets de type Robot et Obstacle pourraient communiquer via la classe Protocol.
      """
      symbolRobot    = oRobot.symbol
      symbolObstacle = oObstacleToSwap.symbol
      newPosition    = oObstacleToSwap.newPosition # Nouvelle position que le robot occupera
      oldPosition    = oRobot.oldPosition
      status         = False
      
      self.mylog("*** _swapObstacle() : Robot to be set=........{}".format(oRobot))
      self.mylog("*** _swapObstacle() : obstacle to be swaped=..{}".format(oObstacleToSwap))
      #self.mylog("*** _swapObstacle() : Mask=                  {}".format(self._symbolMask[0]))
      
      notification   = ""
      if(symbolObstacle == self._symbolEmpty) :
         
         # L'obstacle cache par le robot est restitue a la position qu'occupait le robot
         oObstacleCached = Obstacle(self._symbolMask[0],oRobot.oldPosition)
         self.mylog("*** _swapObstacle() : obstacle masked= {}".format(oObstacleCached))
         self._setObstacle(oObstacleCached)

         # L'obstacle occupe par le robot est cache 
         self._symbolMask[0] = symbolObstacle

         # Le robot occupe une nouvelle position
         oRobot.oldPosition = newPosition
         oObstacle = Obstacle(oRobot.symbol,newPosition)
         self._setObstacle(oObstacle) 

         notification = "Continuez..."

      elif(symbolObstacle == self._symbolExit) :
         # L'obstacle cache par le robot est restitue a la position qu'occupait le robot
         oObstacleCached = Obstacle(self._symbolMask[0],oRobot.oldPosition)
         self.mylog("*** _swapObstacle() : obstacle masked= {}".format(oObstacleCached))
         self._setObstacle(oObstacleCached)

         # L'obstacle occupe par le robot est cache 
         self._symbolMask[0] = symbolObstacle

         # Le robot occupe une nouvelle position
         oRobot.oldPosition = newPosition
         oObstacle = Obstacle(oRobot.symbol,newPosition)
         self._setObstacle(oObstacle) 
         
         self.mylog("*** _swapObstacle() : Card name= ".format(self._cardName))
         # La regle du jeu de certaines cartes est implementee en dur.
         # Une regle du jeu pourrait etre associee a chaque carte.
         self.mylog("*** _swapObstacle() : Robot position= {}".format(oRobot.newPosition))
         if "cage-aux-folles" == self._cardName :
            if 14 !=  oRobot.newPosition[0] :
               notification = "\nVous avez perdu! Mauvaise sortie!\n\n"
               oObstacle = Obstacle(symbolObstacle,newPosition)
               self._setObstacle(oObstacle) 
               status = True                        
            else :
               if oRobot._oObstacle.symbol == self._symbolMaried :
                  notification = "\nBravo! Vous avez gagne.e la sortie en bonne compagnie!\n\n"
                  status = True
               else :
                  notification = "\n Perdu.e! Vous ne pouvez sortir que marie.e!\n\n"
                  status = True
         else :
            notification = "\nBravo! Vous avez gagne.e la sortie! Fin de la partie!\n\n"
            status = True
         self.mylog("*** _swapObstacle() : Notification= {}".format(notification))
      elif(symbolObstacle == self._symbolWall) :
         # L'obstacle cache par le robot est restitue a la position qu'occupait le robot
         oObstacleCached = Obstacle(self._symbolMask[0],oRobot.oldPosition)
         self._setObstacle(oObstacleCached)

         # Pas de deplacement : le robot revient a sa position originale
         oRobot.positionReset()
         self._setObstacle(oRobot)
         notification = "\nEh! En plein dans le mur!"
                  
      elif(symbolObstacle == self._symbolDoor) :
         # L'obstacle cache par le robot est restitue a la position qu'occupait le robot
         oObstacleCached = Obstacle(self._symbolMask[0],oRobot.oldPosition)
         self.mylog("*** _swapObstacle() : obstacle masked= {}".format(oObstacleCached))
         self._setObstacle(oObstacleCached)

         # L'obstacle occupe par le robot est cache 
         self._symbolMask[0] = symbolObstacle

         # Le robot occupe une nouvelle position
         oRobot.oldPosition = newPosition
         oObstacle = Obstacle(oRobot.symbol,newPosition)
         self._setObstacle(oObstacle) 
                  
         notification = "\nPorte franchie!"

      elif(symbolObstacle == self._symbolMaried) :
         # L'obstacle cache par le robot est restitue a la position qu'occupait le robot
         oObstacleCached = Obstacle(self._symbolMask[0],oRobot.oldPosition)
         self.mylog("*** _swapObstacle() : obstacle masked= {}".format(oObstacleCached))
         self._setObstacle(oObstacleCached)

         # L'obstacle occupe par le robot est cachepar une case vide
         self._symbolMask[0] = self._symbolEmpty

         # Le robot occupe une nouvelle position
         oRobot.oldPosition = newPosition
         oObstacle = Obstacle(oRobot.symbol,newPosition)
         self._setObstacle(oObstacle) 

         if "cage-aux-folles" == self._cardName :
            notification      = "\n XXX Mariage reussie! Dirigez vous vers la BONNE sortie! XXX"
            oObstacle         = Obstacle(symbolObstacle,Protocol._zeroPosition)
            oRobot._oObstacle = oObstacle

      elif(symbolObstacle == self._symbolRobot) :
         # L'obstacle cache par le robot est restitue a la position qu'occupait le robot
         oObstacleCached = Obstacle(self._symbolMask[0],oRobot.oldPosition)
         self.mylog("*** _swapObstacle() : obstacle masked= {}".format(oObstacleCached))
         self._setObstacle(oObstacleCached)

         # L'obstacle occupe par le robot est cache 
         self._symbolMask[0] = symbolObstacle

         # Le robot occupe une nouvelle position
         oRobot.oldPosition = newPosition
         oObstacle = Obstacle(oRobot.symbol,newPosition)
         self._setObstacle(oObstacle) 

         notification = "\nRobot repositionne!"
      else :
         notification = "\n*** ERREUR : symbole a remplacer inconnu : {}".format(symbolObstacle)
      return status, oRobot,notification       
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def _setObstacle(self,oObstacle):
      """ 
         Positione sur la carte, l'obstacle passe en parametre 
      """
      
      position = oObstacle.newPosition
         
      line   = position[0]
      column = position[1]
      symbol = oObstacle.symbol

      symbolLine = self._loadedObstacle[line]
      listNewLine = list()
      for col,obstacle in enumerate( symbolLine ):
         if col == column :
            listNewLine.append(symbol)
         else :
            listNewLine.append(obstacle)
            
      self._loadedObstacle[line] = "".join(listNewLine)
      return 
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def _buildCardName(self,cardID) :
      """
         Construit le nom de la carte du jeu a partir d'un identifiant 
         passe en parametre.
         
      """ 
      status = False
      if 0 > cardID :
         return status, ""
      
      try : 
         cardNameList   = self._listCarte[cardID].rsplit(self._cardExtension)
      except IndexError:
         self.setOutput("\n*** ERREUR : Identifiant de carte = {}".format(cardID))         
         return status, ""
         
      cardName = cardNameList[0]
      if 0 < len(cardName) : 
         status = True
      return status, cardName
      
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def backupParty(self):
      """
         Sauvegarde de la partie en cours de jeu.
         l'objet de type Carte est serialise dans un fichier correspond a la carte 
         identifiee par self._cardID.
      """
      status = False
      if 0 > self._cardID :
         self.mylog_error("\n CarteID= \""+str(self._cardID)+"\" : valeur invalide!")         
         return status

      status, fileName = self._buildCardName(self._cardID)      
      if False == status :
         self.setOutput("*** ERREUR : jeu en cours identifie par {} non sauvegarde".format(self._cardID))
         return status 

      fileName = self._dataFolderName+fileName + self._dataExtension
      with open(fileName,"wb") as partyInProgress:
         oPickler = pickle.Pickler(partyInProgress)
         oPickler.dump(self)
      status = True         
      self.mylog("\n Carte \""+fileName+" \" sauvegardee !")
      return status
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def dump(self) :
      """ Serialize les obstacles de la carte.
      Ces obstacles serialises peuvent etre tranmis en reseau.
      """
      serializedObstacles = pickle.dumps(self._loadedObstacle)
      return serializedObstacles
   #---------------------------------------------------------------------------


   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def dropParty(self):
      """
         Purge du fichier contenant la partie en cours de jeu.
      """
      status = False
      
      if 0 > self._cardID :
         self.mylog_error("\n CarteID= \""+str(self._cardID)+"\" : valeur invalide!")         
         return ""
      status, fileName = self._buildCardName(self._cardID)      
      fileName = self._dataFolderName+fileName + self._dataExtension
      try : 
         os.remove(fileName)
      except FileNotFoundError :
         print(" Fichier a purger itrouvable !")
         return status 
      status = True  
      self.mylog("\n Carte \""+fileName+" \" purgee !")
      return status
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def _checkPosition(self,position) :
      """ Verifie que la position passee en parametre reste dans le cadre de la carte. 
         Parametre : position = [ligne,colonne]
      """
      #if( 0 <= position[0] and position[0] < self._lineMax 
      #and 0 <= position[1] and position[1] < self._columnMax) :
      #   return True
      #else : 
      #   return False
      
      #Si le robot ne rencontre pas de mur, le deplacement est autorise.
      return True
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   # 
   #---------------------------------------------------------------------------
   def getRandomPosition(self) :
      """
         Calcul aleatoirement une position sur la carte qui ne soit pas un obstacle.
      """   

      isFreePosition = False
      randomPosition = (0,0,0)
      symbolsLane    = ""
      columnCount    = 0
      freeSymbol     = ""
      mytry          = 0
      
      # Recuperation d'une valeur aleatoire entre ]0, lineMax[ x ]0, colMax[
      while isFreePosition is False and mytry < 20:
         lineRandom   = random.randint(1, self._lineMax-1)
         columnRandom = random.randint(1, self._columnMax-1)
         self.mylog("\n*** Carte : (lineRandom, columnRandom) = ({},{}) x Carte=({},{})".\
         format(lineRandom, columnRandom, self._lineMax,self._columnMax))

         # On s'assure que les valeurs aleatoires sont bien dans l'ordre de grandeur
         if lineRandom < self._lineMax and columnRandom < self._columnMax :
            try :
               freeSymbol = self._loadedObstacle[lineRandom][columnRandom]
            except IndexError:
               freeSymbol     = ""
               pass
            if Symbol._symbolEmpty == freeSymbol :
               randomPosition = (lineRandom,columnRandom,0)
               isFreePosition = True
            else :
               pass
         mytry += 1
      self.mylog("\n*** Carte : Found random position = {}".format(randomPosition))
      return randomPosition

   #---------------------------------------------------------------------------
   
