

#include "stdio.h"
#undef F_CPU
#define F_CPU 16000000UL // Clock frequency in Hz ~ 16 Mhz
// pin definitions
const uint8_t led_pin = 13;
const uint8_t echo = 10;
const uint8_t trig = 9;

// end of pin definitions

// func def 
double getDistanceFromSensor();
void readIncomingSignalFromMaster();
// end of func def


void setup(){

  // perform the init setup
  Serial.begin(9600);
  pinMode(led_pin, OUTPUT);
  pinMode(echo, INPUT); 
  pinMode(trig, OUTPUT); digitalWrite(trig, LOW); 
  pinMode(A0, OUTPUT);


  // end of init setup
}

void loop(){
  readIncomingSignalFromMaster(); // reads signal from main program 
  /*
    digitalWrite(LED_PIN, HIGH);
    Serial.println(LED_PIN);
    delayMicroseconds(5000);
    digitalWrite(LED_PIN, LOW);
    Serial.println(LED_PIN);
    delayMicroseconds(5000);
    */
    double distance; 
    distance = getDistanceFromSensor();
    if(distance == 0.0) { loop();} // if reads an invalid value due to timeout, skip the iteration
    Serial.print(distance); Serial.println(" cm");
    if (getDistanceFromSensor() < 50) {
      //if distance is less than 50 cm 
      digitalWrite(led_pin, HIGH);
    } else {
      digitalWrite(led_pin, LOW);
    }
    //delayMicroseconds(10000);
  }



  double getDistanceFromSensor(){
  double dist;
  long pulse_duration;
  //long startTime, stopTime;
  digitalWrite(trig, HIGH); // send the 10Khz sound pulse
  delayMicroseconds(10);  
  digitalWrite(trig, LOW);
  pulse_duration =  pulseIn(echo, HIGH, 38000);// how long it takes to take back the pulse
  //distance = (pulse_duration * 0.0343) / 2;
  dist = pulse_duration / 58; // returns distance in cm;
  return dist; // 
}


void readIncomingSignalFromMaster(){
  // Check if data is available on the serial port
  if (Serial.available() > 0) {
    // Read the incoming data
    char incomingData = Serial.read();

    // If the data is '1', turn on the LED
    if (incomingData == '1') {
      digitalWrite(A0, HIGH);
    }
    // If the data is '0', turn off the LED
    else if (incomingData == '0') {
      digitalWrite(A0, LOW);
    }
    else{
      Serial.println("Incoming data is invalid!");
    }
  }
}
