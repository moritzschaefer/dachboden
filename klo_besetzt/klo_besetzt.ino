// firmware to show if the Dachboden bathroom is free or occupied
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

// switch for door lock is connected between D3 and D4
#define SWITCH_OUT_PIN 3
#define SWITCH_IN_PIN 4
// SK2812 LEDs DI is connected to D2 pin
#define LEDS_PIN 2
// number of SK2812 LEDs
#define LEDS_NUM 32
// time (in milliseconds) to pause between satus update
#define DELAYVAL 500 
// object to contorl the SK2812 LEDs
Adafruit_NeoPixel leds(LEDS_NUM, LEDS_PIN, NEO_GRBW + NEO_KHZ800);

/* update the LEDs according to betsetzt status:
 * - false: light the 16 first LEDs green
 * - true: light the 16 last LEDs red
 */
void update_light(bool besetzt) {
  // set all pixel colors to 'off'
  leds.clear();
  // update LEDs according to status
  if (besetzt) {
    // light the 16 first LEDs green
    for (uint8_t i = 0; i < 16 && i < LEDS_NUM; i++) {
      leds.setPixelColor(i, leds.Color(0, 128, 0, 0));
    }
  } else {
    // light the 16 last LEDs red
    for (uint8_t i = 16; i < LEDS_NUM; i++) {
      leds.setPixelColor(i, leds.Color(128, 0, 0, 0));
    }
  }
  // send data to LEDs
  leds.show();
}

void setup() {
  pinMode(SWITCH_OUT_PIN, OUTPUT);
  digitalWrite(SWITCH_OUT_PIN, LOW);
  pinMode(SWITCH_IN_PIN, INPUT_PULLUP);
  
  leds.begin(); // initialize NeoPixel strip object (REQUIRED)
}

void loop() {
  // update the LEDs
  update_light(digitalRead(SWITCH_IN_PIN));
  /* periodically update the LEDs
   * don't just do it when the switch state change
   * this allow the state to be corrected even if we missed the state change
   * plus this is the only thing we need to do
   */
  delay(DELAYVAL);
}
