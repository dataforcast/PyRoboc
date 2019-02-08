#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-
from core.Obstacle import *
from util.Protocol import *
class Robot(Obstacle,Protocol) :
   """ 
   Cette classe modelise le robot. Le robot est un obstacle qui se deplace.
   """
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __init__(self,position,symbol='X') :
      """ 
      Initialise le robot a partir d'une commande de controle. 
      Le deplacement du robot sur la carte est calcule a partir de la commande de controle 
      et de la position du robot sur la carte.
      Par defaut, le robot est initialise en mode 'None'; dans ce mode, il ne communique pas 
      avec d'autres objets qui heritent de la classe Protocol.
      
      """
      Obstacle.__init__(self,symbol, position)

      # Le robot est initialise en mode 'None': il ne communique pas par le reseau.
      Protocol.__init__(self,symbol,self)

      self.moovable    = True

      # Position intermediaire du robot occupee dans son deplacement successif case par case.
      self._oldPosition = position
      
      #Position originale du robot avant son deplacement.
      self._originalPosition = self._newPosition

      #Compagnon du robot: c'est un obstacle de type particulier.
      self._oObstacle = Obstacle(' ',Protocol._zeroPosition)

      #Autre robot compagnon du robot:
      #self._oRobotOther       = Robot(Protocol._zeroPosition)

   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __str__(self) :
      message  ="\n---------------ROBOT--------------------------"
      message += Obstacle.__str__(self)
      message +="\nOld  position = \'{}\'".format(self._oldPosition)
      message +="\nOrig position = \'{}\'".format(self._originalPosition)
      message +="\nDirection     = \'{}\'".format(self._direction)
      message +="\n--->Compagnon =   {}  ".format(self._oObstacle)
      message +="\n----------------------------------------------"
      return message
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def restState(self) :
      """ Initialise la direction de l'objet a 'R' """
      self._direction = self._directions[0]
   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def isRestState(self) :
      """ Retourne True si la direction de l'objet a 'R', False sinon """
      status = self._direction == self._directions[0]
      return status
   #---------------------------------------------------------------------------
      
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def positionReset(self) :
      """
         Permet de reinitialiser la position du robot a sa position 
         originale, i.e avant le calcule de son deplacement.
      """
      self._newPosition = self._originalPosition
      self._oldPosition = self._originalPosition
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #  Properties
   #---------------------------------------------------------------------------
   #------------------------------#

   def _get_originalPosition(self) :
      return self._originalPosition

   def _get_oldPosition(self) :
      return self._oldPosition


   #------------------------------#
   def _set_originalPosition(self,position) :
      self._originalPosition = position
      
   def _set_oldPosition(self,position) :
      self._oldPosition = position

   #------------------------------#
   
   originalPosition = property(_get_originalPosition, _set_originalPosition)
   oldPosition      = property(_get_oldPosition,      _set_oldPosition)

   #---------------------------------------------------------------------------


