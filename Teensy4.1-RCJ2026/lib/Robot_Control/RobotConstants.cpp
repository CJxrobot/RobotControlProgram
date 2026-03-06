#include "RobotConstants.h"

RobotState S; // Define the global state

void UpdateSensors() {
    // TODO: Write code here to read your actual sensors
    // Example: S.ball.dist = analogRead(A0);
}

bool Check(SensorType type, char op, float threshold) {
    float val = 0;
    switch(type) {
        case S_BALL_DIST:   val = S.ball.dist; break;
        case S_BLUE_DIST:   val = S.blue.dist; break;
        case S_YELLOW_DIST: val = S.yellow.dist; break;
        case S_TIMER:       val = millis(); break;
        case S_LINE_EXIST:  val = S.line_exist ? 1.0 : 0.0; break;
        case S_LINE_STATE:  val = (float)S.line_state; break;
        case S_NONE:        return true; 
    }

    if (op == '>') return val > threshold;
    if (op == '<') return val < threshold;
    if (op == '=') return val == threshold;
    if (op == '!') return val != threshold;
    return false;
}

void ExecuteMove(MoveStyle style, MoveType target, int speed, float x, float y) {
    // TODO: Implement your PID or motor drive logic here
    Serial.print("Moving to: "); Serial.println(x);
}

void UpdateRotation(RotationMode mode, int value) {
    // TODO: Implement gyro/rotation logic
}

void Stop_Robot() {
    // TODO: Set all motor PWM to 0
}