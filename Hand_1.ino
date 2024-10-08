#include <Servo.h>

Servo servo1, servo2, servo3, servo4, servo5;
const int numServos = 5;
Servo servos[numServos] = {servo1, servo2, servo3, servo4, servo5};
const int servoPins[numServos] = {8, 9, 10, 11, 12};

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numServos; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(90);  // Initialize to open position
  }
}

void loop() {
  if (Serial.available() >= numServos) {
    for (int i = 0; i < numServos; i++) {
      char fingerState = Serial.read();
      if (fingerState == '0') {
        servos[i].write(0);  // Close position
      } else if (fingerState == '1') {
        servos[i].write(100);  // Open position
      }
    }
  }
}