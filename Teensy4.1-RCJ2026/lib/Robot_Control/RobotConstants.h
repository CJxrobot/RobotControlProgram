#ifndef ROBOT_CONSTANTS_H
#define ROBOT_CONSTANTS_H

#include <Arduino.h>

enum MoveStyle { STYLE_LINEAR, STYLE_CURVED, STYLE_STAY };
enum MoveType { M_POS_XY, M_AXIS_X, M_AXIS_Y, M_BALL, M_BLUE_GOAL, M_YELLOW_GOAL, M_STAY };
enum SensorType { S_NONE, S_BALL_DIST, S_BLUE_DIST, S_YELLOW_DIST, S_TIMER, S_LINE_EXIST, S_LINE_STATE };
enum RotationMode { R_FACE_BALL, R_FACE_BLUE, R_FACE_YELLOW, R_DEGREE, R_SPIN };

struct RobotState {
    struct Obj { bool exist; float x, y, dist; } blue, yellow, ball;
    float yaw;
    uint32_t line_state;
    bool line_exist;
};

extern RobotState S;

// Prototypes (The promise that these functions exist somewhere)
void UpdateSensors();
bool Check(SensorType type, char op, float threshold);
void ExecuteMove(MoveStyle style, MoveType target, int speed, float x = 0, float y = 0);
void UpdateRotation(RotationMode mode, int value);
void Stop_Robot();

#endif