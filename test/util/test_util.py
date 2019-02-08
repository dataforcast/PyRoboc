#!/usr/bin/python3.5
#-*- coding: utf-8 -*-

from util.Protocol import *
#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def notest_util_requestHandler(myInstance,time2sleep=0) :
   receivedData          = myInstance.request.recv(Protocol.maxDataLength)
   #print("\n<--- From     : {} ".format(myInstance.client_address[0]))
   oMessageHolder = MessageHolder(None,None)
   oMessageHolder = oMessageHolder.deserialized(receivedData)

   
   oMessageHolder._notification = "Received"
   message = oMessageHolder.data

   message = myInstance.process(message)
   
   oMessageHolder = MessageHolder(None,message,None)
   serializedData = oMessageHolder.serialized()

   time.sleep(time2sleep)
   myInstance.request.sendall(serializedData)
#---------------------------------------------------------------------------


# Dictionnaire des méthodes
tcpHandlerMethods = {
    "handle": test_util_requestHandler,
}


