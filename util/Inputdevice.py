#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-

class Inputdevice() :
   """ 
      Cette classe implemente un peripherique de communication permettant a un utilisateur 
      d'envoyer des donnees.
   """

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def __init__(self) :
      pass

   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def getInput(self,message,prompt=None) :
      """
         Cette fonction implemente la fonction systeme 'input'"
      """
      if prompt is None :
         return input(message)
      else :
         return input(prompt+message)
   #---------------------------------------------------------------------------
   
   

