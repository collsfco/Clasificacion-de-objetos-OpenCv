#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
////////////////////////////////////////////////////////////////////////////////////
//   AUTOR:   Francisco Colls                                            Abril/2020
////////////////////////////////////////////////////////////////////////////////////
//   PROGRAMA: Detección de color y objetos.                            VERSIÓN: 1.0      
//   DISPOSITIVO: Broadcom BCM2837B0, Cortex-A53 (ARMv8) 64-bit SoC                              
//   Versión Python:   3.5.3                             
//   TARJETA DE APLICACIÓN: Raspberry Pi 3 B+                   
////////////////////////////////////////////////////////////////////////////////////

Con la ayuda de una cámara se detectará movimiento en una zona de la pantalla, al
detectar movimiento, se procederá a la identificación de la pieza. Luego de tener
su forma se realiza la identificación del color y se envia por puerto serie la
figura+color, así el brazo robot puede realizar la clasificación del objeto.

////////////////////////////////////////////////////////////////////////////////////
"""
#////////////////////////////////////////////////////////////////////////////////////
# IMPORTAR LIBRERÍAS E INSTANCIAR CLASES
#////////////////////////////////////////////////////////////////////////////////////
import cv2          #Importamos cv2.                            >>>>> OpenCv.
import numpy as np  #Importamos numpy y creamos el objeto 'np'. >>>>> Sirve para trabajar con matrices, vectores, etc...   
import time         #Importamos time (time.sleep)
import serial       #Importamos "serial" para mandar los datos al ESP32.

webcam_id = 0                      #Seleccionamos el id de la cámara web.
cap = cv2.VideoCapture(webcam_id)  #Creamos el objeto 'cap'

#////////////////////////////////////////////////////////////////////////////////////
# VARIABLES GLOBALES
#////////////////////////////////////////////////////////////////////////////////////

mensajeEnviado=False
piezaDetectada=False

#////////////////////////////////////////////////////////////////////////////////////
# FUNCIONES
#////////////////////////////////////////////////////////////////////////////////////
def color_detectado(imagenHSV):
        
    # Rojo
    rojoBajo = np.array([161, 155, 84], np.uint8)      #Rango color Bajo ([H,S,V])
    rojoAlto = np.array([180, 255, 255], np.uint8)     #Rango color Alto ([H,S,V])
    #Blanco
    blancoBajo = np.array([11, 20, 20], np.uint8)
    blancoAlto = np.array([19, 155, 255], np.uint8)
    #Verde
    verdeBajo = np.array([25, 52, 72], np.uint8)
    verdeAlto = np.array([102, 255, 255], np.uint8)

    # Se buscan los colores en la imagen, según los límites indicados. 
    
    maskRojo = cv2.inRange(imagenHSV, rojoBajo, rojoAlto)        #Se crea una máscara en cada imagen, si detecta 
    maskBlanco = cv2.inRange(imagenHSV, blancoBajo, blancoAlto)  #algo dentro del rango indicado ese pixel será 
    maskVerde = cv2.inRange(imagenHSV, verdeBajo, verdeAlto)     #blanco, si no detecta nada ese pixel será negro.

    cntsRojo = cv2.findContours(maskRojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]      #Dibuja el contorno en la imagen detectada.
    cntsBlanco = cv2.findContours(maskBlanco, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1] 
    cntsVerde = cv2.findContours(maskVerde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1] 

    if len(cntsRojo)>0: color = 'Rojo'        #Dependiedo del contorno dibujado, si es mayor a 0
    elif len(cntsBlanco)>0: color = 'Blanco'  #devuelve el nombre del color.
    elif len(cntsVerde)>0: color = 'Verde'
    return color

def figura_detectada(approx):
    
    if len(approx)<6:
        figura='Cuadrado'
    elif len(approx)>10:
        figura='Circulo'
    return figura
   

#////////////////////////////////////////////////////////////////////////////////////
# CONFIGURACIÓN PUERTOS GPIO Y RECURSOS A UTILIZAR
#////////////////////////////////////////////////////////////////////////////////////
ser=serial.Serial('/dev/ttyAMA0',115200)  #Inicializamos el puerto ttyAMA0
#ser=serial.Serial('/dev/ttyUSB0',115200)

#////////////////////////////////////////////////////////////////////////////////////
# PROGRAMA PRINCIPAL
#////////////////////////////////////////////////////////////////////////////////////
try:
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, image = cap.read()   #"ret" es una variable booleana que devuelve "True" si hay imagen disponible.
                                  #"image" es un vector de matriz de imágenes capturado en función de los fotogramas

        if ret == True:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #Convertimos la imagen a escala de grises.

            canny = cv2.Canny(image, 10, 150, 3)   #Canny es un detector de bordes,
                                                   #(imagen de entrada, limite1,limite2,tamaño del borde)

            #Transformaciones Morfológicas: cv2.erode(), cv2.dilate(), cv2.morphologyEx() etc.
        
            canny = cv2.dilate(canny, None, iterations=1) #(imagen de entrada,None,Número de veces que se aplica la dilatación)
            canny = cv2.erode(canny, None, iterations=1)  #(imagen de entrada,None,Número de veces que se aplica la erosión)

            imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) #Convertimos la imagen a formato HSV.

            pixG=gray[240,320]    #Leemos el valor del pixel central de la imagen en escala de grises.
            
            if pixG < 20:         #Si el valor del pixel es menor a 20 no hay pieza.
                mensajeEnviado=False
                piezaDetectada=False
                time.sleep(0.1)

            if pixG > 25:        #Si el valor del pixel es mayor a 25 se ha detectado 
                piezaDetectada=True         #pieza y se procede a la identificación.
                time.sleep(0.25)
            
            if piezaDetectada==True:

                _,contorno,_ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                #image,contours,hierarchy = cv.FindContours(image, storage, mode)
                
                for c in contorno:           #C, representa cada contorno dibujado.
                    area=cv2.contourArea (c) #La función calcula un área de contorno.
                    if area > 3000:           #Si el área es mayor a la cantidad indicada procedemos.
                
                        epsilon = 0.01*cv2.arcLength(c,True)       #Especifica la precisión de aproximación. Calcula un perímetro de contorno o una longitud de curva.
                        approx = cv2.approxPolyDP(c,epsilon,True)  #Aproxima una curva poligonal con la precisión especificada.
                                                                   #cv2.approxPolyDP(curve, epsilon, closed)
                                                                   #Closed> True=Curva cerrada...False=Curva abierta                                                     

                        x,y,w,h = cv2.boundingRect(approx)         #Sea (x,y)la coordenada superior izquierda y (w,h) ancho y alto.
                                                                   #Obtenemos las coordenas (X,Y), para escribir el nombre.  
                        
                        imAux = np.zeros(image.shape[:2], dtype="uint8")   #Con numpy creamos una máscara de la imagen original.
                        imAux = cv2.drawContours(imAux, [c], -1, 255, -1)  #Dibujamos los contornos en la máscara.

                        maskHSV = cv2.bitwise_and(imageHSV,imageHSV, mask=imAux) #cv2.bitwise_and(src1, src2, mask) 
                                                                                 #(src1:primera matriz ,src2:segunda matriz, máscara)
                        color = color_detectado(maskHSV)
                        forma = figura_detectada(approx) + ' ' + color  #La variable forma, será el mensaje enviado por el puerto serie.

                        cv2.putText(image,forma, (x,y-5),1,1,(0,255,0),1)   #Escribimos el texto
                        time.sleep(0.1)                                                       #(Coordenadas,Color,Grosor de línea)
                        
                        #Enviamos solo una vez el mensaje por el puerto serie.
                            
                        if mensajeEnviado==False:                        
                            if piezaDetectada==True:
                                print('OBJETO=',forma)  
                                ser.write(forma.encode())   #Enviamos el mensaje
                                ser.flushInput()            #Limpiamos el buffer de la UART ttyUSB0
                                mensajeEnviado=True
                                time.sleep(0.1)
                                                             
                        cv2.drawContours(image, [c], 0, (0,255,0),2)    #cv2.drawContours(image, contours, maxLevel, color)
                                                                        #maxLevel= Si es 0, solo se dibuja el contorno especificado.

                        cv2.imshow('image',image)   #Los valores que muestran son R,G,B
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
   
except KeyboardInterrupt:         #Si el usuario pulsa CONTROL+C entonces...
    print("El usuario ha pulsado Ctrl+C...")
    """
    CERRAMOS RECURSOS ABIERTOS
    """
except:
    print("error inesperado")
    """
    CERRAMOS RECURSOS ABIERTOS
    """
finally:
# Liberar todo si el trabajo ha terminado.
    cap.release()
    cv2.destroyAllWindows()
