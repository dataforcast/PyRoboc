#!/usr/bin/python3.5
#-*- coding: utf-8 -*-
import unittest
from core.Carte import *

class CarteTest(unittest.TestCase) :
   """
      Cette classe permet de tester unitairement l'ensemble des services fournies 
      par la classe Carte.

      NB:
      Les services sont les méthodes (fonctions) appelées par des fonctions externes à la classe testée.
      Par convention, les méthodes dites \"internes\" à une classe commencent par le caractère \"_\"
   """
   
   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def setUp(self):
      """Initialisation des tests."""
      self._cardID = 0
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_readList(self) :
      """
         Teste le service Carte.readList
         Le test est validé si les conditions suivantes sont satisfaites :
          1) Les cartes recherchées sont dans le repertoire 'cartes'
          2) La liste des cartes ne contient que des noms avec l'extention dédiée aux cartes.
          
          Pré-requis: le repertoire 'cartes' doit exister et contenir au moins un fichier carte.
          
      """
      #
      status = False
      
      #Test du renvoie du status d'erreur
      oCarte = Carte()
      status = 0==oCarte._listMax
      self.assertTrue( status )
      
      # Test de la lecture de la liste des cartes
      oCarte.readList()
      status = 0<oCarte._listMax
      self.assertTrue( status  )
      
      # Tous les élements de la liste sont ils des noms de fichiers carte?
      for index,fileName in enumerate(oCarte._listCarte) :
         if None == re.search(oCarte._cardExtension,oCarte._listCarte[index]):
            status = False
            break;

      self.assertTrue( status  )   
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_getCardName(self):
      """
         Test le service Carte.getCardName
         Le test est validé si les conditions suivantes sont satisfaites :
         1) Un identifiant de carte erronée est supporté
         2) Si le nom de la carte existe 

         Pré-requis: le repertoire 'cartes' doit exister et contenir au moins un fichier carte.

      """
      status = False
      cardID = -1
      oCarte = Carte()
      
      status, cardName1 = oCarte.getCardName(cardID)
      status = not status
      status1, cardName2 = oCarte.getCardName(self._cardID)
      status1 = not status1
      
      status = status and status1
      self.assertTrue( status )
      
      # On lit les cartes et on verifie que tous les éléments de la liste lue correspond à nom de carte
      oCarte.readList()
      self.assertTrue( 0 < oCarte._listMax )

      index = 0
      while index <  oCarte._listMax :      
         status1,cardName =  oCarte.getCardName(cardID)
         status1 = status1 and (0 < len(cardName))
         index  += 1
      
      self.assertTrue( status )
   #---------------------------------------------------------------------------

   #---------------------------------------------------------------------------
   #
   #---------------------------------------------------------------------------
   def test_getDataName(self):
      """
      Test du servide de lecture des parties enregistrées : Carte.getDataName

      Le test est validé si les conditions suivantes sont satisfaites :
      1) Un identifiant de partie erronée est supporté
      2) Si une partie en cours correspondant a une carte de la liste existe


      Pré-requis: 
      1) le repertoire 'cartes' doit exister et contenir au moins un fichier carte correspondant 
      à une partie en cours.
      2) le repertoire 'cartes/data' doit exister et contenir au moins un fichier dont 
      l'extension correspond à un fichier de partie en cours.
               
      """
      status    = False
      dataCount = 0
      
      oCarte = Carte()
      oCarte.readList()

      cardID = -1
      
      # La liste des cartes est parcourue et pour chaque element de cette liste,
      # La présence d'une partie en cours est vérifiée. Si c'est le cas, le compteur de parties 
      # en cours est incrémenté.
      while cardID <  oCarte._listMax :      
         status1,cardName = oCarte.getCardName(cardID)
         status2,dataName = oCarte.getDataName(cardName)
         if( True == status2 and 0<len(dataName)):
            dataCount +=1
         cardID  += 1
         
      status = (0<dataCount)
      
      self.assertTrue( status )
   #---------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
