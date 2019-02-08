#!/usr/bin/python3.5
##-*- coding: utf-8 -*-
# -*-coding:Latin-1 -*
import socket
import select
import signal
import sys
import core

from util.MessageHolder   import *
from util.TCPConnection   import *
from core.LabyrinthServer import *
from util.common          import *
from util.Mylog           import *

#---------------------------------------------------------------------------      
#
#---------------------------------------------------------------------------      
def tcpServer_close(signal, frame) :
   """
      Cette fonction est activee lorsque le signal SIGINT est intercepte.
      Elle est passive si le mode de jeu definie dans la class Protocol 
      n'est pas 'server'.
      Dans le cas contraire, la connection du serveur est fermee ainsi que 
      toutes les connexions client encore actives.
   
   """
   mylog = Mylog(debug=False)
   mylog.mylog("\n*** Mode serveur= {}\n".format(Protocol.CURRENT_MODE))

   if (Protocol.CURRENT_MODE is 'premier') or (Protocol.CURRENT_MODE is 'client'):
      client_close()

   elif Protocol.CURRENT_MODE is 'server' :
      print("\n*** Fermeture des connexions\n")
      if LabyrinthTCPServer.clients_connectes is not None :
         for client in LabyrinthTCPServer.clients_connectes:
             client.close()

      if LabyrinthTCPServer.connexion_principale is not None :
         LabyrinthTCPServer.connexion_principale.close()

      server_tracker_print()
   else :
      pass
   sys.exit(0)
#---------------------------------------------------------------------------      
signal.signal(signal.SIGINT, tcpServer_close)
         

#---------------------------------------------------------------------------      
#
#---------------------------------------------------------------------------      
class LabyrinthTCPServer(LabyrinthServer, Thread) :
   """
      Cette classe implemente la logique d'un serveur TCP.
      Un objet de cette classe se charge de la communication client/serveur sur un reseau TCP.

      Elle herite de la classe LabyrinthServer qui lui permet de transmettre les requetes 
      du reseau a l'instance de LabyrinthServer.
      
      L'impementation du serveur TCP est repris du cours et modifié pour la circonstance.
      Un client peu arrêter le serveur en envoyant la commande d'arrêt '0'
      
   """
   connexion_principale = None
   clients_connectes    = None
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   def __init__(self, gamers, debug, passwd="roboc", pserverAddress=None) :
      """
         Initialise le serveur TCP qui se met en ecoute sur une addresse reseau.
         gamers : nombre de joueurs 
         passwd : le mot de passe du serveur
         debug  : True pour activation des traces.
         pserverAddress : l'adresse du serveur sous forme (IP,port)
         Si la valeur de pserverAddress est None, la valeur par defaut definie dans TCPConnection est utilisee.
      """
      mode = 'server'
      Thread.__init__(self)
      LabyrinthServer.__init__(self, mode, gamers, debug)

      self._gamersConnection = dict()
      self._passwd = hashlib.sha1(passwd.encode()).hexdigest()
      self.initAddress(pserverAddress)
      
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def halt(self) :
      """
      Cette methode permet d'arreter le serveur de jeu sans passer par un message 
      issue de la classe Potocol.
      Une connexion telnet est utilisee.
      """
      #------------------------------------------------------------------------
      # Connnexion telnet...
      #------------------------------------------------------------------------
      connection = telnetlib.Telnet(self._serverAddress[0], self._serverAddress[1])
      
      # Si la connexion au serveur de jeu a reussie, l'objet retournne est du type Telnet.
      status = str(type(connection)).find('Telnet') > 0

      #------------------------------------------------------------------------
      # Le serveur est arrete violement
      #------------------------------------------------------------------------
      if status is True :
         connection.write(b"stop")
         connection.close()
      else :
         pass


   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def initAddress(self, serverAddress) :
      """
      Cette methode permet d'initialiser l'ojet avec une adresse reseau.
      Si tout ou partie des composantes du tuple (IP, PORT) sont indefinies,
      ces composantes prennent leur valeur dans de la classe  TCPConnection.
      """
      self.mylog("\n Server Address = {}".format(serverAddress))
      
      if serverAddress is None : 
         self._serverAddress = TCPConnection.SERVER
      else :
         if serverAddress[0] is None :
            host = TCPConnection.HOST 

         else :
            host = serverAddress[0]
            
         if serverAddress[1] is None :
            port = TCPConnection.PORT

         else :
            port = serverAddress[1]
         
         self._serverAddress = (host,port)
   #---------------------------------------------------------------------------

      
   #---------------------------------------------------------------------------      
   #
   #---------------------------------------------------------------------------      
   def _set_gamerConnection(self, gamerIdentifier, gamerConnection) :
      """
      Cette methode associe un indentifiant de joueur a sa connection TCP
      """
      self._gamersConnection[gamerIdentifier] = gamerConnection      
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------      
   #
   #---------------------------------------------------------------------------      
   def _get_gamerConnection(self, gamerIdentifier) :
      """
      Cette methode retourne la connection TCP associee a un identifiant de joueur.
      """
      return self._gamersConnection[gamerIdentifier]  
   #---------------------------------------------------------------------------      
      
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------      
   def run(self) :
      """
      Methode principale du thread.
      Elle attend sur un port reseau les connections des clients.
      Elle gere le cycle de vie des connections clients.
      Elle se charge de recevoir les requetes des clients et d'en transferer 
      le traitement a l'objet de type LabyrinthServer.
      
      """
      #Efface de la carte le robot initialement charge avec la carte du jeu.
      self.oCarte.cleanRobot()
      self.mylog("*** INFO : Server address= {}".format(self._serverAddress))            
      LabyrinthTCPServer.connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      LabyrinthTCPServer.connexion_principale.bind(self._serverAddress)
      LabyrinthTCPServer.connexion_principale.listen(self._gamersMax)

      print ("\nLe serveur ecoute a present sur l'adresse {}\n".format(self._serverAddress))

      LabyrinthTCPServer.clients_connectes = []
      serveur_lance = True
      while serveur_lance :
          # On va verifier que de nouveaux clients ne demandent pas a se connecter
          # Pour cela, on ecoute la connexion_principale en lecture
          # On attend maximum 50ms
          try :
             connexions_demandees, wlist, xlist = select.select([LabyrinthTCPServer.connexion_principale],
                 [], [], 0.05)
          except OSError :
            pass
          except ValueError :
            pass 
            
          #self.mylog("\nDemande de connexion ...")
          for connexion in connexions_demandees:
            connexion_avec_client, infos_connexion = connexion.accept()
            self.mylog("\nConnexion acceptee = {}".format(infos_connexion))
            # On ajoute le socket connecte a la liste des clients
            LabyrinthTCPServer.clients_connectes.append(connexion_avec_client)
          
          # Maintenant, on ecoute la liste des clients connectes
          # Les clients renvoyes par select sont ceux devant etre lus (recv)
          # On attend la encore 50ms maximum
          # On enferme l'appel a select.select dans un bloc try
          # En effet, si la liste de clients connectes est vide, une exception
          # Peut etre levee
          clients_a_lire = []
          try:
            clients_a_lire, wlist, xlist = select.select(LabyrinthTCPServer.clients_connectes,\
            [], [], 0.05)
          except select.error:
            print("*** WARNING : select.error on select()")
          except ValueError :
            print("*** WARNING : value error on select()")
          else:
              # On parcourt la liste des clients a lire
              for client in clients_a_lire:
                  # Client est de type socket
                  try :
                     receivedRequest = client.recv(TCPConnection.MAXDATALENGTH)
                     self.mylog("\n *** LabyrinthTCPServer <--- received message length= {}".\
                     format(len(receivedRequest)))
                  except  ConnectionResetError :
                     self.mylog("\n *** LabyrinthTCPServer: Connection ERROR from client {}".format(client))
                     if client in self._gamersConnection.values() :
                        for timeStamp in self._gamersQueue.keys() :
                           gamerId = self._gamersQueue[timeStamp]
                           gamerConnection = self._gamersConnection[gamerId]
                           if client is gamerConnection :
                              self._drop_gamer(gamerId)
                              gamerConnection.close()
                              LabyrinthTCPServer.clients_connectes.remove(gamerConnection)
                     else :
                        client.close()
                        LabyrinthTCPServer.clients_connectes.remove(client)
                  except OSError :
                     pass

                     
                  #------------------------------------------------------------
                  # Traitement du message recu et renvoie de la reponse au joueur.
                  #------------------------------------------------------------
                  message = self.processRequest(receivedRequest, client)
                  
                  #------------------------------------------------------------
                  # Verifier les clients connectes; ceux qui ont ete purges du 
                  # jeu sont, ici, purges de la liste des clients connectes.
                  #------------------------------------------------------------
                  self.mylog("\n self._gamersConnection= {}".format(self._gamersConnection))
                  
                  for client in LabyrinthTCPServer.clients_connectes:
                     if client not in self._gamersConnection.values() :
                        client.close()
                        LabyrinthTCPServer.clients_connectes.remove(client)
                  #------------------------------------------------------------
                  # Affichage des clients connectes
                  #------------------------------------------------------------
                  self.mylog("\n self.LabyrinthTCPServer.clients_connectes= {}".\
                  format(LabyrinthTCPServer.clients_connectes))
                  self.displayGamersRessources()

                  #------------------------------------------------------------
                  # Un client a demande l'arret du serveur.
                  #------------------------------------------------------------
                  if self._isServerHalted is True :
                     serveur_lance = False

                  #------------------------------------------------------------
                  # La partie s'est terminee
                  #------------------------------------------------------------
                  if LabyrinthState.STATE_END_KEY is self._state :

                     # Le serveur passe dans l'etat WAIT; des joueurs 
                     # peuvent s'enregistrer.
                     self._state = LabyrinthState.STATE_WAIT_KEY

                     # La carte est rechargee
                     self.oCarte.load(self.oLabyrinth._carteID)

                     # La carte est nettoyee de tout symbole robot 
                     self.oCarte.cleanRobot()

                     
      #------------------------------------------------------------
      # Arret du serveur.
      #------------------------------------------------------------
      print("\n*** INFO : Arret du serveur. Patientez... ***".center(80))
      LabyrinthTCPServer.connexion_principale.close()
      server_tracker_print()
   #---------------------------------------------------------------------------      

   #---------------------------------------------------------------------------      
   #
   #--------------------------------------------------------------------------- 
   @server_method_tracker(TRACKFLAG)     
   def processRequest(self,receivedRequest, client) :
      """
         Cette methode deserialise la requete passee en parametre 
         et verifie que l'entete du message soit conforme au protocole.
         L'identifiant du client est relevé et associé a la connexion TCP passee 
         en parametre.
         Si l'entete du message n'est pas conforme, une notification est renvoyee au client.
         Dans le cas contraire, le contenu du message (la payload) est envoyé a la methode 
         LabyrinthServer.payloadProcess pour traitement.
         
         Le message recu est retourne.
      """
      #------------------------------------------------------------------------
      # Deserialisation de la requete.
      #------------------------------------------------------------------------
      oMessageHolder = MessageHolder(None,receivedRequest)
      oMessageHolder = oMessageHolder.deserialized(receivedRequest)
      if oMessageHolder is not None :
         message        = oMessageHolder.data
      else :
         client.close()
         self._isServerHalted = True
         return 
      #------------------------------------------------------------------------
      # La conformite de la requete envoyee par un joueur est verifiee
      #------------------------------------------------------------------------
      status, notification = self.messageCheck(message)

      #------------------------------------------------------------------------
      # Cas de reception d'une requete non conforme : construction du message 
      # retourne au joueur.
      #------------------------------------------------------------------------
      if status is False :
         playStatus = False
         self.sendMessageGamer(notification, message['id'], playStatus)
         return 

      self.mylog("\n *** LabyrinthTCPServer.processRequest() : message= {}".format(message))      

      #------------------------------------------------------------------------
      # La connexion du joueur est associee a l'identifiant du joueur
      #------------------------------------------------------------------------
      self._set_gamerConnection(message['id'], client)
      self.mylog("\n *** LabyrinthTCPServer.processRequest() : Connection recorded= {}".format(client))      


      #------------------------------------------------------------------------
      # Le message est traite et une reponse est retournee au joueur.
      # Tous les autres joueurs sont notifies de l'etat du jeu.
      #------------------------------------------------------------------------
      self.processPayload(message)
      return message
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def sendMessage(self, gamerIdentifier, message) :
      """
      Cette methode se charge de serialiser le message passe en parametre 
      et de l'envoyer sur la connexion TCP du joueur gamerIdenfitier.
      Le message est serialise avant d'etre transmis.
      """
      self.mylog("\n---------------------------------------")
      self.mylog("\n*** sendMessage() : Message = {}".format(message))
      self.mylog("\n---------------------------------------")

      oMessageHolder = MessageHolder(None, message)
      serializedData = oMessageHolder.serialized()

      self._gamersConnection[gamerIdentifier].sendall(serializedData)
      
   #---------------------------------------------------------------------------
#---------------------------------------------------------------------------      

