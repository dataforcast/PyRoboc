#!/usr/bin/python3.5
# -*-coding:Latin-1 -*
##-*- coding: utf-8 -*-

"""
Ce package contient les classes propres au jeu du labyrinthe.

--> Symbol          : definie la representation symbolique des obstacles sur la carte.
--> Carte           : modèlise une carte du jeu du labyrinthe et implemente la règle du jeu.
--> Labyrinth       : contrôle le deroulement du jeu du labyrinthe en fonction des etats du jeu.
--> LabyrinthServer : implemente la logique du jeu en reseau a plusieurs joueurs.
--> LabyrinthTCPServer : implemente le serveur TCP dedie au jeu du labyrinthe.
--> LabyrinthState  : definie tous les etats de la machine a etat du serveur.
--> Obstacle        : modèlise un obstacle sur la carte. 
--> Robot           : modèlise le robot. Un robot est un obstacle qui se deplace sur la carte du jeu.
--> RobotController : implemente la communication entre le.a joueu.r.se et le robot qui se deplace dans le 
                      labyrinthe.
"""
