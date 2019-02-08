#!/usr/bin/python3.5
#-*- coding: utf-8 -*-
from  util.common import *
import sys
class Outputdevice() :
   """ 
      Cette classe implemente un peripherique d'affichage.
   """

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def __init__(self, isGUI=False) :
      #self._isGUI     = isGUI
      #self.oOutputGUI = OutputGUI()
      pass
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   @client_method_tracker(TRACKFLAG)
   def setOutput(self, message) :
      """
         Cette fonction implemente la l'affichage d'un message sur un peripherique.

         Si sortie graphique est activee (option -g au lancement de l'application)
         alors l'affichage se faiit dans une fenetre graphique.

         Dans le cas contraire, la sortie est affichee sur la sortie standard de la fonction 
         systeme print.
      """
      #if self._isGUI is True :
         #self.oOutputGUI = OutputGUI()
         #print("\n*** INFO : Outputdevice = {}".format(self.oOutputGUI))
         #self.oOutputGUI.setOutput(message)
      #else :
      print(message)
   #---------------------------------------------------------------------------
   
   

