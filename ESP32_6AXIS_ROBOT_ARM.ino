/*
  ////////////////////////////////////////////////////////////////////////////////////
  //   AUTOR: Francisco Colls                                                Mayo/2020
  ////////////////////////////////////////////////////////////////////////////////////
  //   PROGRAMA: 6 AXIS ROBOT ARM                         VERSIÓN: 1.0
  //   DISPOSITIVO: ESP32                                 COMPILADOR: AVR
  //   Entorno IDE: 1.8.10                                SIMULADOR:
  //   TARJETA DE APLICACIÓN: Node MCU                    DEBUGGER:
  ////////////////////////////////////////////////////////////////////////////////////
  Controlar los servomores de un brazo robot. Se pueden controlar hasta 6 servomotores
  con la placa "6 AXIS ROBOT ARM".
  El programa lee los datos enviados por la Raspberry,y dependiendo del color y la forma
  de la pieza detectada los clasifica en el lugar indicado.
  ////////////////////////////////////////////////////////////////////////////////////
*/
///////////////////////////////////////////////////////////////////////////////////
// LIBRERÍAS //////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////
#include <ESP32Servo.h>

////////////////////////////////////////////////////////////////////////////////////
// VARIABLES GLOBALES //////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////
String cadena;
Servo servoBase;  //Creamos el objeto servoBase
Servo servoSubeBaja;  //Creamos el objeto servoSubeBaja
Servo servoAdelanteAtras;  //Creamos el objeto servoAdelanteAtras
Servo servoPinza;  //Creamos el objeto servoPinza

const int ServoA_B = 4; //Declaramos los pines utilizados por cada servo.
const int ServoB_SB = 16;
const int ServoC_AA = 17;
const int ServoD_P = 5;

////////////////////////////////////////////////////////////////////////////////////
// FUNCIONES ///////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////
void moverBrazo(String cadena);
void origenServos();
void buscarPieza();

////////////////////////////////////////////////////////////////////////////////////
// CONFIGURACIÓN ///////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////
void setup()
{
  Serial.begin(115200);// Configuramos la velocidad del puerto serie.
  servoBase.attach(ServoA_B);
  servoSubeBaja.attach(ServoB_SB);
  servoAdelanteAtras.attach(ServoC_AA);
  servoPinza.attach(ServoD_P);

  //Movemos los servos al ángulo de la posición de inicio.
  origenServos();

}
////////////////////////////////////////////////////////////////////////////////////
// PRINCIPAL ///////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////
void loop()
{
  while (Serial.available() > 0) //Leemos el puerto serie
  {
    cadena = Serial.readString(); //Leemos el String enviado desde la Raspberry.
    Serial.print(cadena);
    moverBrazo(cadena);

  }
}

void moverBrazo(String cadena) {
  if (cadena == "Cuadrado Rojo" || cadena == "Circulo Rojo")
  {
    Serial.println("\nMOVER ROJO");
    //MOVEMOS EL BRAZO HACIA LA PIEZA.
    buscarPieza();
    //MOVEMOS EL BRAZO A LA POSICIÓN 1.
    servoAdelanteAtras.write(150);
    delay(1000);
    servoBase.write(110);
    delay(2000);
    servoSubeBaja.write(128);
    delay(2000);
    servoPinza.write(30);
    delay(1000);
    //MOVEMOS EL BRAZO AL ORIGEN.
    origenServos();
  }
  if (cadena == "Cuadrado Blanco"  || cadena == "Circulo Blanco")
  {
    Serial.println("\nMOVER BLANCO");
    //MOVEMOS EL BRAZO HACIA LA PIEZA
    buscarPieza();
    //MOVEMOS EL BRAZO A LA POSICIÓN 3.
    servoAdelanteAtras.write(125);
    delay(1000);
    servoBase.write(0);
    delay(2000);
    servoPinza.write(30);
    delay(1000);
    //ORIGEN.
    origenServos();
  }
  if (cadena == "Cuadrado Verde" || cadena == "Circulo Verde")
  {
    Serial.println("\nMOVER VERDE");
    //MOVEMOS EL BRAZO HACIA LA PIEZA
    buscarPieza();
    //MOVEMOS EL BRAZO A LA POSICIÓN  2.
    servoAdelanteAtras.write(125);
    delay(1000);
    servoBase.write(60);
    delay(2000);
    servoSubeBaja.write(100);
    delay(2000);
    servoPinza.write(30);
    delay(1000);
    //ORIGEN.
    origenServos();
  }
}

void origenServos() {
  servoBase.write(180);
  servoSubeBaja.write(80);
  servoAdelanteAtras.write(125);
  servoPinza.write(20);
}

void buscarPieza() {
  servoAdelanteAtras.write(175);
  delay(1000);
  servoPinza.write(62);
  delay(1000);
}
