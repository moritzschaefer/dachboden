#include <FastLED.h>

#define DATA_PIN          5
#define BRIGHTNESS        100     // maximum is 255 not good for permament use
#define LED_TYPE          WS2812B
#define COLOR_ORDER       GRB

int const COUNT_OF_LEDS = 95;

CRGB buffer_output[COUNT_OF_LEDS];

void setup() {
  // put your setup code here, to run once:
  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(buffer_output, COUNT_OF_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  Serial.begin(9600);

  for(int j=0; j<5; j++) {
      for(int i=0; i<COUNT_OF_LEDS; i++) {
        buffer_output[i] = CRGB::Yellow;
        delay(10);
        FastLED.show();
      }
      
      for(int i=0; i<COUNT_OF_LEDS; i++) {
        buffer_output[i] = CRGB::Blue;
        delay(10);
        FastLED.show();
      }
    }
    FastLED.show();

    for(int i=BRIGHTNESS; i>0; i--) {
      FastLED.setBrightness(BRIGHTNESS-i);
      for(int i=0; i<COUNT_OF_LEDS; i++) {
        if (i > COUNT_OF_LEDS/2){
        buffer_output[i] = CRGB::Green;
        }
        else {
          buffer_output[i] = CRGB::Red;
      }
      FastLED.show();
      }
    }
  FastLED.show();
}

void loop() {
  // put your main code here, to run repeatedly:

}
