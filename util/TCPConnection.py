#!/usr/bin/python3.5
# #-*- coding: utf-8 -*-
#-*-coding:Latin-1 -*
import random
class TCPConnection() :
   """
   Cette classe definie les constantes pour les connexions TCP.
   """
   HOST  = "127.0.0.1"
   PORT  = 2000

   SERVER         = (HOST,PORT)
   MAXDATALENGTH  = 1024*16
