# Vex-Desk-Defence-System

This project is a programmable rubber band launching turret using the VEX EXP kit and Python (VEXcode EXP). There are two versions accessible in this repo to view. The VEXbrain folder will display the content for the remote control version, and the raspberry pi folder will display the content for the facial tracking version.

The rubberband launcher can rotate left/right on the X-axis and up/down on the Y-axis using the VEX controller joysticks. Pressing the A button on the controller activates the firing motor to release a rubber band.

---

## Hardware Requirements

- VEX EXP Brain  
- VEX EXP Controller  
- 3 Motors  
  - X-axis rotation (horizontal)
  - Y-axis rotation (vertical)
  - Firing mechanism
- Rubber band firing mechanism using a tension gear system  
- Battery and USB cable

---

## Software Requirements

- [VEXcode EXP]
- VEX EXP configured and paired with controller

---

## Project Setup

1. Open **VEXcode EXP**.
2. Create a new **Python project**.
3. Replace the default code with the provided `firing controller.exppython` content.
4. Make sure your motors are connected to these ports:
   - **X-axis motor** → Port 3  
   - **Y-axis motor** → Port 5  
   - **Firing motor** → Port 1
5. Save and **download** the program to the brain via USB.
6. Disconnect USB and power on the brain.

---

## Controls

| Control              | Action                          |
|----------------------|---------------------------------|
| Left Joystick (X)    | Move turret left/right (X-axis) |
| Right Joystick (Y)   | Move turret up/down (Y-axis)    |
| A Button             | Fire rubber band                |

*The motors have slow response scaling for precision aiming and built-in error boundaries to prevent over-rotation.*

---

## Notes

- Motor boundaries are limited to avoid over-rotation:
- You can adjust these boundaries in the code (`X_MIN`, `X_MAX`, `Y_MIN`, `Y_MAX`).
- Holding the A button spins the firing gear slowly. You can tweak speed or duration in the `fire_control()` function.
- By holding down the A button, you can continuosly fire bands if you have loaded multiple onto the gear system.
