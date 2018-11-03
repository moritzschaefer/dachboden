/*
  Knock Sensor

  This sketch reads a piezo element to detect a knocking sound.
  It reads an analog pin and compares the result to a set THRESHOLD.
  If the result is greater than the THRESHOLD, it writes "knock" to the serial
  port, and toggles the LED on pin 13.

  The circuit:
    - positive connection of the piezo attached to analog in 0
    - negative connection of the piezo attached to ground
    - 1 megohm resistor attached from analog in 0 to ground

*/

#include <FastLED.h>

#define LED_VERT          6
#define LED_HOR           5
#define LED_TOTAL         LED_HOR*LED_VERT      // Just 30 for the fist pad

#define DATA_PIN          5

#define BRIGHTNESS        100     // maximum is 255 not good for permament use
#define LED_TYPE          WS2812B
#define COLOR_ORDER       GRB


// constants
const int knockSensor  = A5; // the piezo is connected to analog pin 0
const int knockSensor2 = A4; // the piezo is connected to analog pin 1
const int THRESHOLD = 150;  // THRESHOLD value to decide when the detected sound is a knock or not
const int MAX_TRY = 5;

// variables
int sensorReading  = 0;      // variable to store the value read from the sensor pin
int sensorReading2 = 0;      // variable to store the value read from the sensor pin

int points1 = 0;
int points2 = 0;

// try management for showing an old pattern
int currentTry = 0;
int trys = 0;

int animationSpeed = 70;
bool animation = true;


CRGB buffer_output_right[2 * LED_TOTAL];

CRGB buffer_output[2 * LED_TOTAL];
CRGB buffer_frame[LED_HOR][LED_VERT];
CRGB buffer_frame_A[LED_HOR][LED_VERT];
CRGB buffer_frame_B[LED_HOR][LED_VERT];

void remap() {            // hadrdcoded just for 2*(5x6) identical matrices
  for (int i = 0; i < 6; i++) {
    //platte 1
    buffer_output[i]         = buffer_frame[0][i];
    buffer_output[11 - i]    = buffer_frame[1][i];
    buffer_output[i + 12]    = buffer_frame[2][i];
    buffer_output[23 - i]    = buffer_frame[3][i];
    buffer_output[i + 24]    = buffer_frame[4][i];
    //platte 2
    buffer_output[30 + i]    = buffer_frame[4][5-i];
    buffer_output[41 - i]    = buffer_frame[3][5-i];
    buffer_output[42 + i]    = buffer_frame[2][5-i];
    buffer_output[53 - i]    = buffer_frame[1][5-i];
    buffer_output[54 + i]    = buffer_frame[0][5-i];
  }
  FastLED.show();
}

// hardcoded for 2*(5x6) different matrices
void remap2() {
  for (int i = 0; i < 6; i++) {
    buffer_output[i]         = buffer_frame_A[0][i];
    buffer_output[11 - i]    = buffer_frame_A[1][i];
    buffer_output[i + 12]    = buffer_frame_A[2][i];
    buffer_output[23 - i]    = buffer_frame_A[3][i];
    buffer_output[i + 24]    = buffer_frame_A[4][i];
    buffer_output[54 + i]    = buffer_frame_B[4][i];  // reverse correction (eine der Platten ist falschrum montiert)
    buffer_output[53 - i]    = buffer_frame_B[3][i];
    buffer_output[42 + i]    = buffer_frame_B[2][i];
    buffer_output[41 - i]    = buffer_frame_B[1][i];
    buffer_output[30 + i]    = buffer_frame_B[0][i];
  }
  FastLED.show();
}

void setup() {
  delay(300); // 3 second delay for recovery; don't know why

  // tell FastLED about the LED strip configuration
  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(buffer_output, 2 * LED_TOTAL).setCorrection(TypicalLEDStrip);
  //FastLED.addLeds<LED_TYPE,DATA_PIN,CLK_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);

  // set master brightness control
  FastLED.setBrightness(BRIGHTNESS);

  Serial.begin(9600);
}

/*
  Main function

  1     wait for players both must tip
  2     create random pattern and save and show it
  3     show patterns
  4     when hit
  4.1   if right, get a point
  4.2   if false, opponent get a point
  5     show ponts
  GO TO (2) until Player has 10 Points
  6.    show ponts with huge delay
  GO TO (1)

*/

CRGB red = CRGB::Red;

void loop() {
  // (1) start new game
  //  while (sensorReading <= THRESHOLD && sensorReading2 <= THRESHOLD) {;};

  Serial.println("gl hf");

  // max amount of wrong pattern

  points1 = 0;
  points2 = 0;

  Serial.println("start game!");

  // Game ends with 10 points
  while (points1 < 3 && points2 < 3) {

    // (2) create first pattern
    Serial.println("Create first pattern");
    animation = true;
    patternRandomSquare(CRGB::Yellow);
    saveArray();

    delay(1500);  // keep pattern in mind

    // confuse
    patternLines ();

    // old pattern shuld load
    trys = random(0, MAX_TRY);
    int patterndelay = 110;

     // wait for knock muss überarbeitet werden und mittel interrupt realisiert werden
    do {
      // (3) create new pattern
      //Serial.print("random square:");
      animation = false;
      patternRandom();
      //delay(patterndelay);
      waitForKnock();
      patterndelay += 5;
    } while (sensorReading <= THRESHOLD && sensorReading2 <= THRESHOLD);

    // (4) If a player makes a hit
    Serial.println("check points");
    checkNgivePoints();
  }

  //showWinner();
  delay(1500);

  // reset sendor readings
  /*delay(100);
    Serial.print("reset knocker");
    sensorReading   = 0;
    sensorReading2  = 0;*/
}

/*
void showWinner () {
  for (int x = 0; x < LED_HOR; x++) {
    for (int y = 0; y < LED_VERT; y++) {
      delay(50);
      if (boolFrameWinner[x][y]) {
        if (points1 >= points2) {
          buffer_frame_A[x][y] = CRGB::Green;
        }
        else {
          buffer_frame_B[x][y] = CRGB::Green;
        }
      }
      if (boolFrameLoser[x][y]) {
        if (points1 >= points2) {
          buffer_frame_B[x][y] = CRGB::Red;

        }
        else {
          buffer_frame_A[x][y] = CRGB::Red;
        }
      }
    }
  }
  remap2();
}*/

// Punktevergabe
void checkNgivePoints() {
  if (sensorReading >= THRESHOLD || sensorReading2 >= THRESHOLD) {
    if (sensorReading >= sensorReading2) {
      // right: give points
      if (sameArray()) {
        points2++;
        player1_winner(true);
        // false: give opponent points
      }
      else {
        points1++;
        player1_winner(false);
      }
    }
    if (sensorReading2 >= sensorReading) {
      if (sameArray()) {
        points1++;
        player1_winner(false);
        // false: give opponent points
      }
      else {
        points2++;
        player1_winner(true);
      }
    }

    // make new try counter
    currentTry = 0;
    trys = random(0, MAX_TRY);

    // show sensorReadings
    Serial.print("SR1: ");
    Serial.println(sensorReading, DEC);
    Serial.print("SR2: ");
    Serial.println(sensorReading2, DEC);


    showPoints();

    //reset knock sensor
    delay(1000);
    sensorReading   = analogRead(knockSensor);
    sensorReading2  = analogRead(knockSensor2);
  }
}

// TODO better: timer
void waitForKnock () {
  int waiter = 0;   // wait breaker seconds to continue
  int breaker = 60;
  while (sensorReading <= THRESHOLD && sensorReading2 <= THRESHOLD && waiter <= breaker) {
    // read the sensors and store it in the variable sensorReading:
    sensorReading   = analogRead(knockSensor);
    sensorReading2  = analogRead(knockSensor2);
    delay(4);
    waiter++;
    //Serial.print(".");
  }
  //Serial.print("\n");
}

// create random patterns
void patternRandom () {
  //Serial.print("current:");
  //Serial.print("("); Serial.print(currentTry, DEC); Serial.print("/"); Serial.print(trys, DEC); Serial.print(")");
  if (currentTry >= trys) {
    for (int i = 0; i < 2 * LED_TOTAL; i++) {
      buffer_output[i] = buffer_output_right[i];
    }
    FastLED.show();
    //Serial.println("same array here");
    currentTry = 0;
    trys = random(0, MAX_TRY);
  }
  else {
    patternRandomSquare(CRGB::Yellow);
    currentTry ++;
  }
}


//Some pattern functions
void patternRandomSquare(CRGB background_col) {
  // Serial.println("create random square");
  patternFill(background_col);

  // create points for a rectangle:
  int x1 = round(random(0, LED_HOR - 1));
  int x2 = round(random(x1 + 1, LED_HOR - 0));
  int y1 = round(random(0, LED_VERT - 1));
  int y2 = round(random(y1 + 1, LED_VERT - 0));



  for (int x = x1; x <= x2; x++) {
    buffer_frame[x][y1] = CRGB::Red;
    if (animation) {
      remap();
      delay(animationSpeed);
    }
  }
  for (int x = x1; x <= x2; x++) {
    buffer_frame[x][y2] = CRGB::Red;
    if (animation) {
      remap();
      delay(animationSpeed);
    }
  }
  for (int y = y1; y <= y2; y++) {
    buffer_frame[x1][y] = CRGB::Red;
    if (animation) {
      remap();
      delay(animationSpeed);
    }
  }
  for (int y = y1; y <= y2; y++) {
    buffer_frame[x2][y] = CRGB::Red;
    if (animation) {
      remap();
      delay(animationSpeed);
    }
  }

  remap();      // convert frame to buffer_output
  FastLED.show();
  delay(100);   // delay to avoid overloading the serial port buffer
}

void patternCross(byte col, byte background_col) {
  Serial.println("create cross");
  for (int i = 0; i < LED_TOTAL; i++) {
    buffer_output[i] = background_col;
  }

  for (int x = 0; x < 5; x++) {
    for (int y = 0; y < 6; y++) {
      if (x == y) {
        buffer_frame[x][y] = col;
      }
      else {
        buffer_frame[x][y] = background_col;
      }
    }
  }
  remap();      // convert frame to output
  FastLED.show();
  delay(200);
}

void patternFill(CRGB col) {
  //Serial.println("fill the field");
  for (int i = 0; i < LED_HOR; i++) {
    for (int j = 0; j < LED_VERT; j++) {
      buffer_frame[i][j] = col;
    }
  }
  remap();
}

/*void patternFillWithoutRemap(CRGB col) {
  for (int i = 0; i < 2 * LED_TOTAL; i++) {
    buffer_output[i] = col;
  }
  FastLED.show();
  delay(30);
  }*/

void patternFillAsynchrone(CRGB col_A, CRGB col_B) {
  //Serial.println("fill asynchrone");
  for (int x = 0; x < 5; x++) {
    for (int y = 0; y < 6; y++) {
      buffer_frame_A[x][y] = col_A;
    }
  }
  for (int x = 0; x < 5; x++) {
    for (int y = 0; y < 6; y++) {
      buffer_frame_B[x][y] = col_B;
    }
  }
  remap2();
  FastLED.show();
}

/*
    ================================
    ================================
    SOME BASIC FUNCTIONS
    ================================
    ================================
*/

// True is player 1; false is player 2
void player1_winner(bool winner) {
  Serial.println("show winner");
  if (winner) {
    patternFillAsynchrone(CRGB::Green, CRGB::Red);
  }
  else {
    patternFillAsynchrone(CRGB::Red, CRGB::Green);
  }
  remap2();      // convert frame to output
  FastLED.show();
  delay(1000);
}

// write buffer_output to rightPattern
void saveArray () {
  for (int i = 0; i < 2 * LED_TOTAL; i++) {
    buffer_output_right[i] = buffer_output[i];
  }
}

bool sameArray () {
  for (int i = 0; i < 2 * LED_TOTAL; i++) {
    if (buffer_output_right[i] != buffer_output[i]) {
      return false;
    }
  }
  return true;
}

void patternLines () {
  Serial.println("confusing lines");
  for (int row = 0; row <= 6; row++) {
    //unsigned int row = 0;
    for (int x = 0; x < 5; x++) {
      for (int y = 0; y < 6; y++) {
        if (x == row) {
          buffer_frame[x][y] = CRGB::White;
        }
        if (x < row && row < 6) {
          buffer_frame[x][y] = CRGB::Black;
        }
        delay(10);
      }
    }
    //row++;
    //row %= 5;
    remap();
  }
}

bool boolFrame0[LED_HOR][LED_VERT] = {
  {0, 0, 0, 0, 0, 0},
  {0, 1, 1, 1, 1, 0},
  {0, 1, 0, 0, 1, 0},
  {0, 1, 1, 1, 1, 0},
  {0, 0, 0, 0, 0, 0}
};
bool boolFrame1[LED_HOR][LED_VERT] = {
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 1, 1, 1, 1, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0}
};
bool boolFrame2[LED_HOR][LED_VERT] = {
  {0, 0, 0, 0, 0, 0},
  {0, 1, 1, 1, 1, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 1, 1, 1, 1, 0},
  {0, 0, 0, 0, 0, 0}
};
bool boolFrame3[LED_HOR][LED_VERT] = {
  {0, 1, 1, 1, 1, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 1, 1, 1, 1, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 1, 1, 1, 1, 0}
};
bool boolFrameWinner[LED_HOR][LED_VERT] = {
  {0, 0, 1, 1, 1, 0},
  {0, 1, 0, 0, 0, 0},
  {0, 0, 1, 1, 0, 0},
  {0, 1, 0, 0, 0, 0},
  {0, 0, 1, 1, 1, 0}
};
bool boolFrameLoser[LED_HOR][LED_VERT] = {
  {0, 0, 0, 0, 0, 0},
  {0, 1, 0, 0, 0, 0},
  {0, 1, 0, 0, 0, 0},
  {0, 1, 1, 1, 1, 0},
  {0, 0, 0, 0, 0, 0}
};

void boolFrameToBufferFrame(CRGB col, bool player, bool boolFrame[LED_HOR][LED_VERT]) {
  for (int x = 0; x < LED_HOR; x++) {
    for (int y = 0; y < LED_VERT; y++) {
      if (boolFrame[x][y]) {
        if (player) {
          buffer_frame_A[x][y] = col;
        }
        else {
          buffer_frame_B[x][y] = col;
        }
      }
    }
  }
  remap2();
}

void showWinner(int winner) {
  if (winner==1) {
    boolFrameToBufferFrame(CRGB::LightSteelBlue, false, boolFrameWinner);
    boolFrameToBufferFrame(CRGB::LightSteelBlue, true, boolFrameLoser); 
  }
  else {
    boolFrameToBufferFrame(CRGB::LightSteelBlue, true, boolFrameWinner);
    boolFrameToBufferFrame(CRGB::LightSteelBlue, false, boolFrameLoser); 
  }
}

void showPoints() {
  for (int x = 0; x < LED_HOR; x++) {
    for (int y = 0; y < LED_VERT; y++) {
      buffer_frame_A[x][y] = CRGB::Black; // buffer_frame[x][y];
      buffer_frame_B[x][y] = CRGB::Black; // buffer_frame[x][y];
    }
  }
  switch (points1) {
    case 0: {
        boolFrameToBufferFrame(CRGB::LightSteelBlue, false, boolFrame0); break;
      }
    case 1: {
        boolFrameToBufferFrame(CRGB::LightSteelBlue, false, boolFrame1); break;
      }
    case 2: {
        boolFrameToBufferFrame(CRGB::LightSteelBlue, false, boolFrame2); break;
      }
    case 3: {
        //boolFrameToBufferFrame(CRGB::LightSteelBlue, false, boolFrame3); 
        showWinner(1);
        break;
      }
    default: {
        Serial.println("ERROR: no match");
      }
  }

  switch (points2) {
    case 0: {
        boolFrameToBufferFrame(CRGB::LightSteelBlue, true, boolFrame0); break;
      }
    case 1: {
        boolFrameToBufferFrame(CRGB::LightSteelBlue, true, boolFrame1); break;
      }
    case 2: {
        boolFrameToBufferFrame(CRGB::LightSteelBlue, true, boolFrame2); break;
      }
    case 3: {
        //boolFrameToBufferFrame(CRGB::LightSteelBlue, true, boolFrame3); 
        showWinner(2);
        break;
      }
    default: {
        Serial.println("ERROR: no match");
      }
  }
  Serial.print("Points P1: "); Serial.println(points1, DEC);
  Serial.print("Points P2: "); Serial.println(points2, DEC);
  remap2();
  delay(1500);
}
