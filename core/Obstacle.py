#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-  
from util.Mylog import *
from util.Protocol import *
from util.common import *
from core.Symbol import *

class Obstacle(Mylog) :
   """ 
    Cette classe implemente les attributs d'un obstacle sur une carte.
    Tous les objets sur la carte sont susceptibles d'heriter de cette classe.
   """
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __init__(self,symbol,position,displayable=True, debug=False) :
      """ 
         Initialise l'obstacle avec le symbole passe en parametre.
         L'obstacle a une position sur la carte, il ne se deplace pas.  
         Il peut etre affichable ou pas. Par defaut du constructeur, il est affichable. 
      """
      Mylog._debug        = debug
      self._mylog        = Mylog()
      self._displayable  = displayable
      self._symbol       = symbol
      self._newPosition  = position 
      self._moovable     = None 
      self._direction    = 'R'

   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __str__(self) :
      message  ="\n----------- Obstacle -----------"
      message +="\nSymbol       = \'{}\'".format(self._symbol)
      message +="\nNew Position = \'{}\'".format(self._newPosition)
      message +="\nDisplayable  = \'{}\'".format(self._displayable)
      message +="\nMoovable     = \'{}\'".format(self._moovable)
      message +="\n--------------------------------"
      return message
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def compute(self,controlCommand):
      """ 
      Calcule la nouvelle position du symbole sur la carte a partir de son ancienne position 
      et de la commande de controle.
      La position originale du symbole est sauvegardee
      """
      jump = 0
      # Analyse de la commande de controle : deplacement ou action?
      if controlCommand[0] in Symbol.SYMBOL_LIST :
         if controlCommand[2] in Protocol.PLAY_DIRECTIONS :
            # La commande de controle est un deplacement
            self._direction  = controlCommand[2]

         if common_isValidType(controlCommand[1],"int"):
            #  La commande de controle est un deplacement
            jump = controlCommand[1]

         elif common_isValidType(controlCommand[1],"str"):
            if controlCommand[1].capitalize() in Protocol.PLAY_ACTIONS :
               # La commande de controle est une action
               jump = 1
            else :
               message = "*** ERREUR : Commande de jeu inconnue : {}".format(controlCommand)
               self.mylog("*** compute() : "+message)
               return False, message
            
         else :
            message = "*** ERREUR : Commande de jeu : Type de controle inconne {}".format(controlCommand)
            self.mylog("*** compute() : "+message)
            return False, message

      else :
         message = "*** ERREUR : routage de commande : Source={} != Destination={}".\
         format(str(controlCommand[0]),self._symbol)
         self.mylog("*** compute() : "+message)
         return False, message
         
      
      self.mylog("*** compute() : Jump      = {} ".format(jump))
      self.mylog("*** compute() : Direction = {} ".format(self._direction))
      

      self.mylog("*** compute() : Control commande = {} ".format(controlCommand))
      position  = self._newPosition
      direction = self._direction
      
      self.mylog("*** compute() : Before computing Robot= {}".format(self))

      # La position originale du robot est sauvegardee
      self._originalPosition =       self._newPosition

      #Calcul de la nouvelle position 
      line      = position[0]
      column    = position[1]
      if direction in Protocol.PLAY_DIRECTIONS :   
         #Calcul effectif de la position sur la carte
         if 'N' == direction :
            line -= jump
         elif 'S' == direction :
            line += jump
         elif 'E' == direction :
            column += jump
         elif 'O' == direction :
            column -= jump
         elif 'U' == direction :
            notification = "*** WARNING : monter non encore active : {}\n".format(direction)
            return False, notification
         elif 'D' == direction :
            notification = "*** WARNING : descendre non encore active : {}\n".format(direction)
            return False, notification
         elif 'R' == direction :
            notification = "\nVous etes dans la place!\n"
            return True, notification
         else :
            notification = "*** ERREUR : direction inconnue : {}\n".format(direction)
            return False, notification

         self._newPosition = [line,column,0]
      else : 
         notification = "*** ERREUR : direction inconnue : {}\n".format(direction)
         return False, notification

      return True, ""
   #---------------------------------------------------------------------------
      

   #---------------------------------------------------------------------------
   #  Properties
   #---------------------------------------------------------------------------

   #------------------------------#
   def _get_newPosition(self) :
      return self._newPosition

   def _set_newPosition(self,position) :
      self._newPosition = position

   def _get_symbol(self) :
      return self._symbol

   def _get_moovable(self) :
      return self._moovable

   def _get_direction(self) :
      return self._direction
   #------------------------------#


   #------------------------------#
   def _get_displayable(self) :
      return self._displayable

   def _set_symbol(self, symbol) :
      self._symbol = symbol

   def _set_moovable(self,moovable) :
      self._moovable = moovable

   def _set_direction(self,direction) :
      self._direction = direction
   #------------------------------#

   symbol      = property(_get_symbol,      _set_symbol)
   newPosition = property(_get_newPosition, _set_newPosition)   
   moovable    = property(_get_moovable,    _set_moovable)   
   displayable = property(_get_displayable)   
   direction   = property(_get_direction,        _set_direction)

   #---------------------------------------------------------------------------


