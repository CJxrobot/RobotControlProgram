#include <Arduino.h>
#include "RobotConstants.h"

void setup() { Robot_Init(); }

void loop() {
  // STEP 1
  while(Check(S_TIMER, '>', 0)){
    UpdateSensors();
    move_along('Y', 69.0, 40);
    UpdateRotation(R_DEGREE, 0, 30);
    if(true) break;
  }

  Stop_Robot(); while(1);
}
