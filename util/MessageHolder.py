#!/usr/bin/python3.5
##-*- coding: utf-8 -*-
# -*-coding:Latin-1 -*
import pickle

from util.common import *

#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------
class MessageHolder() :
   """ 
   Cette classe permet d'envoyer des messages sur un reseau.

   Elle permet de serialiser (emetteur) et deserialiser (recepteur) les messages 
   a transmettre.
   
   """

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __init__(self, controlCmd, data, notification="") :
      """
         Initilisation de l'objet dont les attributs seront echanges entre le client 
         et le serveur.
         Les champs du protocole sont ranges dans un dictionnaire.
      """
      self._data         = dict()
      self._notification = notification
      self._controlCmd   = controlCmd
      self._status       = True
      
      # L'attribut _data est initialise si le parametre data est un dictionnaire.
      if common_isValidType(data,'dict') is True :
         # data est de type dictionnaire
         self._data = data
      else :
         self._data['data'] = data
   #---------------------------------------------------------------------------   


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def deserialized(self, serializedData) :
      try :
         oMessageHolder = pickle.loads(serializedData)
      except EOFError :
         return None
      except pickle.UnpicklingError:
         return None
      return oMessageHolder
   #---------------------------------------------------------------------------
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def serialized(self) :
      oMessageHolder = pickle.dumps(self)
      return oMessageHolder
   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------
   #  Properties
   #---------------------------------------------------------------------------

   #------------------------------#
   def _get_data(self) :
      return self._data
   #------------------------------#
   def _set_data(self,data) :
      self._data = data
   #------------------------------#
   
   data = property(_get_data, _set_data)
   
   #---------------------------------------------------------------------------
#-----------------------------------------------------------------------------

