#!/usr/bin/python3.5
# #-*- coding: utf-8 -*-
# -*-coding:Latin-1 -*
#from tkinter     import *
import threading
from threading   import Thread

import util

from util.common import *

#@singleton
#class OutputGUI(Thread) :
def labelBuild():
   # On cree une fenetre, racine de notre interface
   fenetre = Tk()

   # On cree un label (ligne de texte) souhaitant la bienvenue
   # Note : le premier parametre passe au constructeur de Label est notre
   # interface racine
   champ_label = Label(fenetre, text="Salut les Zer0s !")

   # On affiche le label dans la fenetre
   champ_label.pack()

   # On demarre la boucle Tkinter qui s'interrompt quand on ferme la fenetre
   fenetre.mainloop()

#@singleton
class OutputGUI(Thread) :
   """
   Cette classe implemente une interface graphique avec tkinter
   """

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------   
   @client_method_tracker(TRACKFLAG)
   def __init__(self) :
      """
      Cette methode initialise les ressources de l'objet et lance le thread.
      """
      Thread.__init__(self)
      self.eventStatus = threading.Event()

      self._guiStatus = False
      # On cree une fenetre, racine de notre interface
      self.fenetre = Tk()

      # On cree un label (ligne de texte) souhaitant la bienvenue
      # Note : le premier parametre passe au constructeur de Label est notre
      # interface racine
      self.labelField = Label(self.fenetre, text="Notifications : ")

      # On affiche le label dans la fenetre
      self.labelField.pack()

   #---------------------------------------------------------------------------   

   #---------------------------------------------------------------------------   
   #
   #---------------------------------------------------------------------------   
   @client_method_tracker(TRACKFLAG)
   def run(self) :
      # On demarre la boucle Tkinter qui s'interrompt quand on ferme la fenetre
      #self.fenetre.mainloop()   
      isRunning = True
      while isRunning is  True:
         isRunning = self._getStatus()
         
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------   
   @client_method_tracker(TRACKFLAG)
   def setOutput(self, message) :
      """
      Cette methode a la charge d'afficher un message dans une feletre 
      graphique de l'objet.
      """
      self.labelField["text"]  = message
      #print("\nMessage = {}".format(message))

   @client_method_tracker(TRACKFLAG)
   def _getStatus(self) :
      status = None
      self.eventStatus.wait()
      status = self._guiStatus
      self.eventStatus.clear()
      return status      
      
   @client_method_tracker(TRACKFLAG)
   def _setStatus(self,status) :
      self._guiStatus = status
      self.eventStatus.set()
      return

