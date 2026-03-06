#ifndef ROBOT_CONSTANTS_H
#define ROBOT_CONSTANTS_H

#include <Arduino.h>

// --- ENUMS: These must match the Python dictionary keys exactly ---

// Movement Styles
enum MoveStyle { 
    STYLE_LINEAR, 
    STYLE_CURVED, 
    STYLE_STAY 
};

// Target Types
enum MoveType { 
    M_POS_XY, 
    M_AXIS_X, 
    M_AXIS_Y, 
    M_BALL, 
    M_BLUE_GOAL, 
    M_YELLOW_GOAL, 
    M_STAY 
};

// Sensor Types for Logic Conditions
enum SensorType { 
    S_NONE, 
    S_BALL_DIST, 
    S_BLUE_DIST, 
    S_YELLOW_DIST, 
    S_TIMER, 
    S_LINE_EXIST, 
    S_LINE_STATE 
};

// Rotation Modes
enum RotationMode { 
    R_FACE_BALL, 
    R_FACE_BLUE, 
    R_FACE_YELLOW, 
    R_DEGREE, 
    R_SPIN 
};

// --- DATA STRUCTURES ---

// A snapshot of the robot's world
struct RobotState {
    struct Obj { 
        bool exist; 
        float x; 
        float y; 
        float dist; 
    } blue, yellow, ball;

    float yaw;           // Current Gyro heading
    uint32_t line_state; // 32-bit line sensor array
    bool line_exist;     // True if any line sensor triggers
};

// Global instance of the robot state
extern RobotState S;

// --- REQUIRED FUNCTION PROTOTYPES ---
// You must implement these in your .cpp or .ino file

/** Refreshes all values in the RobotState S struct from hardware */
void UpdateSensors();

/** Compares a sensor value against a threshold using an operator ('>', '<', '=', '!') */
bool Check(SensorType type, char op, float threshold);

/** Executes motor movement based on style and target coordinates */
void ExecuteMove(MoveStyle style, MoveType target, int speed, float x = 0, float y = 0);

/** Adjusts the robot's heading based on the selected mode */
void UpdateRotation(RotationMode mode, int value);

/** Initializes sensors and motor drivers */
void Robot_Init();

/** Immediate stop of all motors */
void Stop();

bool Check(SensorType type, char op, float threshold) {
    if (type == S_NONE) return true;
    float val = 0;
    switch(type) {
        case S_BALL_DIST:   val = S.ball.dist; break;
        case S_TIMER:       val = millis();    break; // or a custom step timer
        case S_LINE_EXIST:  val = S.line_exist; break;
        // ... add other cases ...
    }
    if (op == '>') return val > threshold;
    if (op == '<') return val < threshold;
    if (op == '=') return val == threshold;
    if (op == '!') return val != threshold;
    return false;
}

#endif
