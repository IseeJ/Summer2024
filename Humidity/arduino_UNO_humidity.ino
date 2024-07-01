//This code was written to be easy to understand.
//Modify this code as you see fit.
//This code will output data to the Arduino serial monitor.
//Type commands into the Arduino serial monitor to control the humidity sensor.
//This code was written in the Arduino 1.8.13 IDE
//An Arduino UNO was used to test this code.
//This code was last tested 8/2020


#include <SoftwareSerial.h>                           //we have to include the SoftwareSerial library, or else we can't use it
#define rx 2                                          //define what pin rx is going to be
#define tx 3                                          //define what pin tx is going to be

SoftwareSerial myserial(rx, tx);                      //define how the soft serial port is going to work


String inputstring = "";                              //a string to hold incoming data from the PC
String sensorstring = "";                             //a string to hold the data from the Atlas Scientific product
boolean input_string_complete = false;                //have we recived all the data from the PC
boolean sensor_string_complete = false;               //have we recived all the data from the Atlas Scientific product




void setup() {                                        //set up the hardware
  Serial.begin(9600);                                 //set baud rate for the hardware serial port_0 to 9600
  myserial.begin(9600);                               //set baud rate for the software serial port to 9600
  inputstring.reserve(10);                            //set aside some bytes for reciving data from the PC
  sensorstring.reserve(30);                           //set aside some bytes for reciving data from Atlas Scientific product
  
}


void serialEvent() {                                  //if the hardware serial port_0 recives a char
  inputstring = Serial.readStringUntil(13);           //read the string until we see a <CR>
  input_string_complete = true;                       //set the flag used to tell if we have recived a completed string from the PC
}


void loop() {                                         //here we go...

  if (input_string_complete == true) {                //if a string from the PC has been recived in its entirety
    myserial.print(inputstring);                      //send that string to the Atlas Scientific product
    myserial.print('\r');                             //add a <CR> to the end of the string
    inputstring = "";                                 //clear the string
    input_string_complete = false;                    //reset the flag used to tell if we have recived a completed string from the PC
  }

  if (myserial.available() > 0) {                     //if we see that the Atlas Scientific product has sent a character
    char inchar = (char)myserial.read();              //get the char we just recived
    sensorstring += inchar;                           //add the char to the var called sensorstring
    if (inchar == '\r') {                             //if the incoming character is a <CR>
      sensor_string_complete = true;                  //set the flag
    }
  }


  if (sensor_string_complete == true) {               //if a string from the Atlas Scientific product has been recived in its entirety
    if (isdigit(sensorstring[0]) == false) {          //if the first character in the string is a digit
      Serial.println(sensorstring);                   //send that string to the PC's serial monitor
    }
    else                                              //if the first character in the string is NOT a digit
    {
      print_Humidity_data();                          //then call this function 
    }
    sensorstring = "";                                //clear the string
    sensor_string_complete = false;                   //reset the flag used to tell if we have recived a completed string from the Atlas Scientific product
  }
}



void print_Humidity_data(void) {                      //this function will pars the string  

  char sensorstring_array[30];                        //we make a char array
  char *HUM;                                          //char pointer used in string parsing.
  char *TMP;                                          //char pointer used in string parsing.
  char *NUL;                                          //char pointer used in string parsing (the sensor outputs some text that we don't need).
  char *DEW;                                          //char pointer used in string parsing.

float HUM_float;                                      //float var used to hold the float value of the humidity.
float TMP_float;                                      //float var used to hold the float value of the temperatur.
float DEW_float;                                      //float var used to hold the float value of the dew point.
  
  sensorstring.toCharArray(sensorstring_array, 30);   //convert the string to a char array 
  HUM = strtok(sensorstring_array, ",");              //let's pars the array at each comma
  TMP = strtok(NULL, ",");                            //let's pars the array at each comma
  NUL = strtok(NULL, ",");                            //let's pars the array at each comma (the sensor outputs the word "DEW" in the string, we dont need it)
  DEW = strtok(NULL, ",");                            //let's pars the array at each comma

  //Serial.println();                                   //this just makes the output easier to read by adding an extra blank line. 
 
  //Serial.print("HUM:");                               //we now print each value we parsed separately.
  //Serial.println(HUM);                                //this is the humidity value.

  //Serial.print("Air TMP:");                           //we now print each value we parsed separately.
  //Serial.println(TMP);                                //this is the air temperatur value.

  //Serial.print("DEW:");                               //we now print each value we parsed separately.
  //Serial.println(DEW);                                //this is the dew point.
  Serial.print(millis());
  Serial.print(",");
  Serial.print(HUM);       
  Serial.print(",");                           //this just makes the output easier to read by adding an extra blank line. 
  Serial.print(TMP);   
  Serial.print(",");   
  Serial.print(DEW);   
  Serial.print("\n");
  //uncomment this section if you want to take the values and convert them into floating point number.
  
    HUM_float=atof(HUM);
    TMP_float=atof(TMP);
    DEW_float=atof(DEW);

}
