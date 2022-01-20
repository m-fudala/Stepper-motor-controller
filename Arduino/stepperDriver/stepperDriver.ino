#include "StepperMotor.h"
#include "SerialTransfer.h"

////// LED setup
#define connection_LED_pin 4
#define work_LED_pin 5

////// motor setup
#define pin_A 6
#define pin_notA 9
#define pin_B 10
#define pin_notB 11

StepperMotor motor(pin_A, pin_notA, pin_B, pin_notB);

volatile bool motor_moving = false;

////// encoder setup
#define encoder_pin_A 2
#define encoder_pin_B 3
#define encoder_pin_Z 7

volatile bool previous_state;
volatile bool current_state;
volatile bool current_stateB;
volatile bool previous_stateZ;
volatile bool current_stateZ;

volatile long counter = 0;
volatile int rot_counter = 0;

bool encoder_used = false;
bool channel_z_used = false;

////// communication setup
char connected[1];
char message[15];
char ok[3] = {'o', 'k'};
char mode;
SerialTransfer myTransfer;
/////////

volatile bool flash_LED = false;

void setup() {
  Serial.begin(1000000);
  myTransfer.begin(Serial);
  
  pinMode(connection_LED_pin, OUTPUT);
  pinMode(work_LED_pin, OUTPUT);  

  while(myTransfer.available() == 0) {
  }
  
  myTransfer.rxObj(connected);

  myTransfer.txObj(ok);
  myTransfer.sendDatum(ok);
  
  if(connected[0] == '1') {
    digitalWrite(connection_LED_pin, HIGH);
  } 

  motor.stp();

  cli();
  pinMode(encoder_pin_A, INPUT_PULLUP);
  pinMode(encoder_pin_B, INPUT_PULLUP);
  pinMode(encoder_pin_Z, INPUT_PULLUP);

  current_state = digitalRead(encoder_pin_A);
  current_stateB = digitalRead(encoder_pin_B);
  current_stateZ = digitalRead(encoder_pin_Z);

  // przerwania na enkoderze ustawienia
  //INT1 - pin 2, INT0 - pin 3
  EICRA = 0;
  EICRB = 0;
  EIMSK = 0;
  
  EICRA |= (1 << ISC10) | (1 << ISC00);
  EICRA &= ~(1 << ISC11) | ~(1 << ISC01);
  
  //INT6 - pin 7
  EICRB |= (1 << ISC60);
  EICRB &= ~(1 << ISC61);
  
  // watch dog
  WDTCSR &= ~(1 << WDIE);
  WDTCSR &= ~(1 << WDE);
  
  // timer 3
  TCCR3A = 0;
  TCCR3B = 0;
  
  TCCR3A |= (1 << COM3B1);    // clear on compare match  
  TCCR3B |= (1 << WGM32);     // CTC mode
  TCCR3B |= (1 << CS32);      // prescaler 256
  OCR3A = 16250;              // TOP
  sei();  
}

void loop() {
  if (myTransfer.available()) {
    
    myTransfer.rxObj(message);
    
    mode = message[0];

    switch(mode) {
      case 'r':
        WDTCSR |= (1 << WDE);
        WDTCSR &= ~(1 << WDP0) | ~(1 << WDP1) | ~(1 << WDP2) | ~(1 << WDP3);
    
        for(;;);

        break;
      
      case 'e':
        if(message[1] == '0') {
          EIMSK &= ~(1 << INT1) | ~(1 << INT0);
          encoder_used = false;
        }

        else {
          EIMSK |= (1 << INT1) | (1 << INT0);
          encoder_used = true;
        }

        myTransfer.txObj(ok);
        myTransfer.sendDatum(ok);

        break;

      case 'z':
        if(message[1] == '0') {
          EIMSK &= ~(1 << INT6);
          channel_z_used = false;
        }

        else {
          EIMSK |= (1 << INT6);
          channel_z_used = true;
        }

        myTransfer.txObj(ok);
        myTransfer.sendDatum(ok);
        
        break;

      case '1':
      case '2':
      case '3':
        myTransfer.txObj(ok);
        myTransfer.sendDatum(ok);
      
        start_movement();

        break;
    }
  }
}

void start_movement() {
  TIMSK3 |= (1 << OCIE3B);
  
  int steps, delay;
  
  steps = int(message[1] - '0')*10000 + int((message[2] - '0')*1000 + int(message[3] - '0')*100 + int(message[4] - '0')*10 + (message[5] - '0'));
      
  if(int(message[6] - '0') == 0)
    steps = -steps;
  
  delay = int(message[7] - '0')*10000 + int((message[8] - '0')*1000 + int(message[9] - '0')*100 + int(message[10] - '0')*10 + int(message[11] - '0'));    
  
  switch (mode) {
    case '1':
      message[0] = (char)0;
      
      motor.startupFS(steps, delay);
      
      break;
      
    case '2':
      message[0] = (char)0;
      
      motor.startupHS(steps, delay);
      
      break;
      
    case '3':        
      unsigned short scaler =  int(message[12] - '0')*10 + int(message[13] - '0');
  
      message[0] = (char)0;
      
      motor.startupMS(steps, delay, scaler);
      
      break;
    }
        
    digitalWrite(pin_A, LOW);
    digitalWrite(pin_notA, LOW);
    digitalWrite(pin_B, LOW);
    digitalWrite(pin_notB, LOW);

    if(encoder_used) {
      char encoder_ticks[11];
      
      if(channel_z_used) {
        sprintf(encoder_ticks, "%07ld%03d", counter, rot_counter);
      }
      else {      
        sprintf(encoder_ticks, "%07ld000", counter);
      }
      
      myTransfer.txObj(encoder_ticks);
      myTransfer.sendDatum(encoder_ticks);
    }

    TIMSK3 &= ~(1 << OCIE3B);
    flash_LED = LOW;
    digitalWrite(work_LED_pin, flash_LED);
}

// ISRs
// encoder (pin change) ISR
ISR(INT1_vect) {  
  current_state = digitalRead(encoder_pin_A);
  
  if (current_state != previous_state) {
    if (current_state == current_stateB) {
      counter--;
    }
    else {
      counter++;
    }
  }
    
    previous_state = current_state; 
}

ISR(INT0_vect) {
  current_stateB = digitalRead(encoder_pin_B);
}

ISR(INT6_vect) {
  current_stateZ = digitalRead(encoder_pin_Z);
  
  if (current_stateZ == HIGH && previous_stateZ == LOW) {
    rot_counter++;
  }
    
  previous_stateZ = current_stateZ;
}

// timer 3 ISR
ISR(TIMER3_COMPB_vect) {
  flash_LED = !flash_LED;
  digitalWrite(work_LED_pin, flash_LED);
}
