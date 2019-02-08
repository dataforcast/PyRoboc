#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-

class Symbol() :
   """
   Cette classe contient la definition de tous les symboles de la carte de jeu du labyrinthe.
   Elle est en mesure d'etre importee par tout les autres modules du package core qui utilisent les 
   symboles.
   """

   _symbolWall      = 'O'
   _symbolEmpty     = ' '
   _symbolDoor      = '.'
   _symbolExit      = 'U'
   _symbolRobot     = 'X'
   _symbolMaried    = 'M'
   _symbolLabyrinth = 'L'
   

   SYMBOL_LIST_ACTION_ALLOWED = [_symbolWall, _symbolEmpty, _symbolDoor]
   SYMBOL_LIST = [_symbolWall, _symbolEmpty, _symbolDoor, _symbolExit, _symbolRobot, _symbolMaried, _symbolLabyrinth]

   SYMBOL_LIST_ALLOWED = ['1','2','3','4','5','6','7','8','9','B','C','D','E','F','G','H','I','J','K','N','P','Q','R']
   SYMBOL_LIST_ALLOWED.append('S') 
   SYMBOL_LIST_ALLOWED.append('T') 
   SYMBOL_LIST_ALLOWED.append('V') 
   SYMBOL_LIST_ALLOWED.append('W') 
   SYMBOL_LIST_ALLOWED.append('X') 
   SYMBOL_LIST_ALLOWED.append('Y') 
   SYMBOL_LIST_ALLOWED.append('Z') 
   SYMBOL_LIST_ALLOWED.append('@') 
   SYMBOL_LIST_ALLOWED.append('\&') 
   SYMBOL_LIST_ALLOWED.append('#') 
   SYMBOL_LIST_ALLOWED.append('=') 
   def __init__(self) :
      pass

      
