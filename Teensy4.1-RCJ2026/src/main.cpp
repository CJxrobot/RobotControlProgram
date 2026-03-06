#include <Robot.h>
#include "RobotConstants.h"

void setup() {
  Robot_Init();
}

void loop() {
  // STEP 1
  while(Check(S_BLUE_DIST, '>', 0)){
    UpdateSensors();
    ExecuteMove(STYLE_LINEAR, M_POS_XY, 60, -17.5, 70.0);
    UpdateRotation(R_FACE_BALL, 0);
    if(Check(S_LINE_EXIST, '==', 1)) break;
  }

  Stop_Robot();
  while(1);
}
