## Arcade-Kicker

We have build RGB-LED strips on both sides of the field to light the game. An ESP8266 microchip can controll the color and intensity of every single light, individually. 
This allows a wide range of modes. 

In its current setting, a green Pong is moving like a pong from one end to the other. When it reaches a side one of several different modes are executed:

# Sparles:
A number of random positioned lights shine on the field. They either change all at once or with FOFO (First on first out ;) ). 

# Ongoing lights:
Starting from a complete dark field, the lights turn on sequentially until the field is fully lighted. 

# Moving areas:
A number of bars (with random colors) are moving like the pong. On overlap, their colorvalues are added. 

# Strobo:
Fast switching on and off. Currently disabled as it was impossible to play while this mode is on.


## TODOS:

- [ ] There should be several buttons connected to the ESP to toggle arcade mode on/off, activate effects, etc...

- [ ] A WLAN connection to the Kickercam such that the board can interact with the game play. (modes are triggerd after a goal, lights following the ball, etc... ) 

