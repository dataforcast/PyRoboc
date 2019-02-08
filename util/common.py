#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-
import os
import sys
import time
import signal
import telnetlib

from util.DictionnaireOrdonne import *

"""
   Ce module contient les fonctions communes à toute l'application.
"""

TRACKFLAG = True

oDictionnaireOrdonne        = DictionnaireOrdonne()
oDictionnaireOrdonne_server = DictionnaireOrdonne()

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def common_isValidType(data,dataType) :
   """
      Retourne True si le paramètre data est du type dataType, False sinon.
   """
   status    = False
   
   if data is not None :
      typeData  = type(data)
      strData   = str(typeData)
      foundType = strData.find(dataType)
      
      if 0 < foundType :
         status = True
         
   return status
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def client_method_tracker(trackflag):
   """
      Idem a client_method_tracker côté serveur.
   """      
   def decorator_calltrack(method) :
      def modified_function(self, *parameters, **named_parameters):
         if trackflag is True :
            timeStamp = time.time()
            oDictionnaireOrdonne[timeStamp] = "--> "+str(method)
         
         returned_method = method(self, *parameters, **named_parameters)   
            
         if trackflag is True :
            timeStamp = time.time()
            oDictionnaireOrdonne[timeStamp] = "<-- "+str(method)
         return returned_method
      return modified_function
   return decorator_calltrack
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def server_method_tracker(trackflag):
   """
      Idem a method_tracker côté serveur.
   """      
   def decorator_calltrack(method) :
      def modified_function(self, *parameters, **named_parameters):
         if trackflag is True :
            timeStamp = time.time()
            oDictionnaireOrdonne_server[timeStamp] = "--> "+str(method)
         
         returned_method = method(self, *parameters, **named_parameters)   
            
         if trackflag is True :
            timeStamp = time.time()
            oDictionnaireOrdonne_server[timeStamp] = "<-- "+str(method)
         return returned_method
      return modified_function
   return decorator_calltrack
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def tracker_print(trackerHolder, fileName) :
   """
   Cette méthode permet d'afficher les traces ordonnées par timestamp 
   des appels des méthodes du serveur.
   """
   
   if TRACKFLAG is True :
      trackFile = open(fileName, "w")

      trackerHolder.sort()
      for timeStamp in trackerHolder.keys() :
         track = trackerHolder[timeStamp]
         trackFile.write("\n {} : {}".format(timeStamp, track))

      trackFile.close()      
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def server_tracker_print() :
   """
   Cette méthode permet d'afficher les traces ordonnées par timestamp 
   des appels des méthodes du serveur fonctionnant en mode TCP.
   """
   
   if TRACKFLAG is True :
      
      fileName = "log/server_calltrack_sorted.txt"      
      trackFile = open(fileName, "w")

      oDictionnaireOrdonne_server.sort()
      for timeStamp in oDictionnaireOrdonne_server.keys() :
         track = oDictionnaireOrdonne_server[timeStamp]
         trackFile.write("\n {} : {}".format(timeStamp, track))

      trackFile.close()      
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def client_tracker_print() :
   """
   Cette méthode permet d'afficher les traces ordonnées par timestamp 
   des appels des méthodes du client fonctionnant en mode premier ou en mode client.
   """
   
   if TRACKFLAG is True :
      
      fileName = "log/client_calltrack_sorted.txt"      
      trackFile = open(fileName, "w")

      oDictionnaireOrdonne.sort()
      for timeStamp in oDictionnaireOrdonne.keys() :
         track = oDictionnaireOrdonne[timeStamp]
         trackFile.write("\n--> {} : {}".format(timeStamp, track))
         #print("\n--> {} : {}\n".format(timeStamp, track))

      trackFile.close()      
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def singleton(classe_definie):
   """
   Decorateur singleton.
   """
   instances = {} # Dictionnaire de nos instances singletons
   def get_instance():
      if classe_definie not in instances:
         # On crée notre premier objet de classe_definie
         instances[classe_definie] = classe_definie()
         return instances[classe_definie]
   return get_instance
#---------------------------------------------------------------------------

