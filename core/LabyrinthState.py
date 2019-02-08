#!/usr/bin/python3.5
##-*- coding: utf-8 -*-
# -*-coding:Latin-1 -*

class LabyrinthState() :
   """
   Cette classe ne contient les constantes des machines a etats du jeu du labyrinth.
   Il est en mesure d'etre importee par toutes les classes implemantant une machine a etat 
   liee au jeu.
   """

   STATE_WAIT_VALUE    = 0
   STATE_READY_VALUE   = 1
   STATE_PLAY_VALUE    = 2
   STATE_PLAYING_VALUE = 3
   STATE_END_VALUE     = 4

   STATE_WAIT_KEY    = 'wait'
   STATE_READY_KEY   = 'ready'
   STATE_PLAY_KEY    = 'play'
   STATE_PLAYING_KEY = 'playing'
   STATE_END_KEY     = 'end'

   STATE_MACHINE = {STATE_WAIT_KEY:STATE_WAIT_VALUE, \
   STATE_READY_KEY:STATE_READY_VALUE,\
   STATE_PLAY_KEY:STATE_PLAY_VALUE, \
   STATE_PLAYING_KEY:STATE_PLAYING_VALUE, \
   STATE_END_KEY:STATE_END_VALUE}   

   def __init__(self) :
      pass

      
