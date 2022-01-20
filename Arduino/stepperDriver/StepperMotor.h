#ifndef StepperMotor_h
#define StepperMotor_h

#include "Arduino.h"

class StepperMotor {
  private:
    int pin_A;
    int pin_notA;
    int pin_B;
    int pin_notB;
  
  public:

    StepperMotor(char _pin_A, char _pin_notA, char _pin_B, char _pin_notB);
    void stp();
    void startupFS(int steps, int delay);               // full step
    void startupHS(int steps, int delay);               // half step
    void startupMS(int steps, int delay, unsigned short scaler);   // micro step
};

#endif
