#include "StepperMotor.h"

  StepperMotor::StepperMotor(char _pin_A, char _pin_notA, char _pin_B, char _pin_notB) {
    pin_A = _pin_A;
    pin_notA = _pin_notA;
    pin_B = _pin_B;
    pin_notB = _pin_notB;
  }

  void StepperMotor::stp() {
    pinMode(pin_A, OUTPUT);
    pinMode(pin_notA, OUTPUT);
    pinMode(pin_B, OUTPUT);
    pinMode(pin_notB, OUTPUT);
  }

  unsigned char step;
  
  void StepperMotor::startupFS(int steps, int delay) {
    for(int i = 0; i <= abs(steps); i++) {
      unsigned long time_now = micros();

      if(steps < 0){
        step = i % 4 + 1;
      }
      else if (steps > 0) {
        step = i % 4;
        step = 4 - step;
      }
      else {
        break;
      }
        
      switch (step) {
        case 1:   //step 1
        digitalWrite(pin_A, LOW);
        delayMicroseconds(10);
        digitalWrite(pin_notA, HIGH);
        digitalWrite(pin_B, LOW);
        delayMicroseconds(10);
        digitalWrite(pin_notB, HIGH);
        
        break;
  
        case 2:   //step2
        digitalWrite(pin_A, LOW);
        delayMicroseconds(10);
        digitalWrite(pin_notA, HIGH);
        delayMicroseconds(10);
        digitalWrite(pin_B, HIGH);
        digitalWrite(pin_notB, LOW);
        
        break;
  
        case 3:   //step3
        delayMicroseconds(10);
        digitalWrite(pin_A, HIGH);
        digitalWrite(pin_notA, LOW);
        delayMicroseconds(10);
        digitalWrite(pin_B, HIGH);
        digitalWrite(pin_notB, LOW);
        
        break;
  
        case 4:   //step4
        delayMicroseconds(10);
        digitalWrite(pin_A, HIGH);
        digitalWrite(pin_notA, LOW);
        digitalWrite(pin_B, LOW);
        digitalWrite(pin_notB, HIGH);
        delayMicroseconds(10);
        
        break;
      }

      while(micros() < (time_now + delay)) {
      }
    }
  }

  void StepperMotor::startupHS(int steps, int delay) {
    for(int i = 0; i <= abs(steps); i++) {
      unsigned long time_now = micros();
      
      if(steps < 0){
        step = i % 8 + 1;
      }
      else if (steps > 0) {
        step = i % 8;
        step = 8 - step;
      }
      else {
        break;
      }
  
      switch (step) {
        case 1:   //step 1
        delayMicroseconds(100);
        digitalWrite(pin_A, HIGH);
        delayMicroseconds(100);
        digitalWrite(pin_notA, HIGH);
        delayMicroseconds(100);
        digitalWrite(pin_B, HIGH);
        digitalWrite(pin_notB, LOW);
        
        break;
        
        case 2:   //step 2
        delayMicroseconds(100);
        digitalWrite(pin_A, HIGH);
        digitalWrite(pin_notA, LOW);
        delayMicroseconds(100);
        digitalWrite(pin_B, HIGH);
        digitalWrite(pin_notB, LOW);
        
        break;
  
        case 3:   //step 3
        delayMicroseconds(100);
        digitalWrite(pin_A, HIGH);
        digitalWrite(pin_notA, LOW);
        delayMicroseconds(100);
        digitalWrite(pin_B, HIGH);
        delayMicroseconds(100);
        digitalWrite(pin_notB, HIGH);
        
        break;
  
        case 4:   //step 4
        delayMicroseconds(100);
        digitalWrite(pin_A, HIGH);
        digitalWrite(pin_notA, LOW);
        digitalWrite(pin_B, LOW);
        delayMicroseconds(100);
        digitalWrite(pin_notB, HIGH);
        
        break;
  
        case 5:   //step 5
        delayMicroseconds(100);
        digitalWrite(pin_A, HIGH);
        delayMicroseconds(100);
        digitalWrite(pin_notA, HIGH);
        digitalWrite(pin_B, LOW);
        digitalWrite(pin_notB, HIGH);
        delayMicroseconds(100);
        
        break;
  
        case 6:   //step 6
        digitalWrite(pin_A, LOW);
        delayMicroseconds(100);
        digitalWrite(pin_notA, HIGH);
        digitalWrite(pin_B, LOW);
        delayMicroseconds(100);
        digitalWrite(pin_notB, HIGH);
        
        break;
  
        case 7:   //step 7
        digitalWrite(pin_A, LOW);
        delayMicroseconds(100);
        digitalWrite(pin_notA, HIGH);
        delayMicroseconds(100);
        digitalWrite(pin_B, HIGH);
        delayMicroseconds(100);
        digitalWrite(pin_notB, HIGH);
        
        break;
        
        case 8:   //step 8
        digitalWrite(pin_A, LOW);
        delayMicroseconds(100);
        digitalWrite(pin_notA, HIGH);
        delayMicroseconds(100);
        digitalWrite(pin_B, HIGH);
        digitalWrite(pin_notB, LOW);
        
        break;
      }

      while(micros() < (time_now + delay)) {
      }
    }
  }

  void StepperMotor::startupMS(int steps, int delay, unsigned short scaler) {    
    unsigned short step_count = 1;
    
    for(unsigned short i = 0; i < scaler; i++) {
      step_count *= 2;
    }
    
    step_count *= 4;

    short sin_PWM, cos_PWM;
    uint8_t PWM_A, PWM_notA, PWM_B, PWM_notB;
    
    for(int i = 1; i <= abs(steps) + 1; i++) {
      unsigned long time_now = micros();
      
      sin_PWM = short (255 * sin((i % step_count - 1) * 2 * PI / step_count));
      cos_PWM = short (255 * cos((i % step_count - 1) * 2 * PI / step_count));

      if(cos_PWM > 0) {
        PWM_A = cos_PWM;
        PWM_notA = 0;
      }
      else if (cos_PWM < 0) {
        PWM_A = 0;
        PWM_notA = abs(cos_PWM);
      }
      else {
        PWM_A = 0;
        PWM_notA = 0;
      }

      if(sin_PWM > 0) {
        PWM_B = sin_PWM;
        PWM_notB = 0;
      }
      else if (sin_PWM < 0) {
        PWM_B = 0;
        PWM_notB = abs(sin_PWM);
      }
      else {
        PWM_B = 0;
        PWM_notB = 0;
      }

      if(steps < 0) {
        uint8_t helper_PWM_A = PWM_A;
        uint8_t helper_PWM_notA = PWM_notA;

        PWM_A = PWM_B;
        PWM_notA = PWM_notB;
        PWM_B = helper_PWM_A;
        PWM_notB = helper_PWM_notA;
      }
      
      analogWrite(pin_A, 255 - PWM_A);
      analogWrite(pin_notA, 255 - PWM_notA);
      analogWrite(pin_B, 255 - PWM_B);
      analogWrite(pin_notB, 255 - PWM_notB);
  
      while(micros() < (time_now + delay)) {
      }
    }
  }
