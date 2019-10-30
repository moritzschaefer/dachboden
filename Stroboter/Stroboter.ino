#include <SPIFFS.h>
#include <ESPAsyncE131.h>
#include <WiFiManager.h>
#include <NeoPixelBus.h>

#define UNIVERSE_COUNT 1

int g_dmx_universe = 5;
int g_dmx_channel_offset = 150;
uint8_t g_brightness = 0;
float g_blinkfreq = 0;
uint8_t g_blinktime = 0;
uint8_t g_random_range = 0;
uint8_t g_blinktime_real = 0;
unsigned long g_blink_begin_time = 0;
unsigned long g_last_dmx_received = 0;
bool g_strip_dirty = false;
bool g_instastrobe_disabled = false;
bool g_instastrobe_pressed = false;

unsigned long g_cur_time = 0;

// the number of the LED pin
const int led1Pin = 16;  // 16 corresponds to GPIO16
const int led2Pin = 4;   // 4 corresponds to GPIO4
const int led3Pin = 17;  // 17 corresponds to GPIO17

const int g_strip_pin = 5;
const int g_mode_pin = 2;
bool      g_standalone = false;

const int g_instastrobe_pin = 0;


// setting PWM properties
const int freq = 500;
const int led1Channel = 0;
const int led2Channel = 1;
const int led3Channel = 2;
const int resolution = 8;
const int max_brightness = 255;
int g_num_strip_leds = 8;
RgbColor g_strip_color;
RgbColor red(255, 0, 0);
RgbColor green(0, 255, 0);
RgbColor blue(0, 0, 255);
RgbColor off(0,0,0);

NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> *g_strip;
ESPAsyncE131 g_e131(UNIVERSE_COUNT);

boolean init_spiffs() {
  bool initok = false;
  initok = SPIFFS.begin();
  if (!(initok))
  {
    Serial.println("SPIFFS formatted");
    SPIFFS.format();
    initok = SPIFFS.begin();
  }
  if (!(initok)) // Try 2
  {
    SPIFFS.format();
    initok = SPIFFS.begin();
  }
  if (initok)
  {
    Serial.println("SPIFFS mounted");
  }
  else
  {
    Serial.println("could not mount SPIFFS");
  }
  return initok;
}

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println("setup");
  
  pinMode(g_mode_pin, INPUT_PULLUP);
  pinMode(g_instastrobe_pin, INPUT_PULLUP);

  ledcSetup(led1Channel, freq, resolution);
  ledcAttachPin(led1Pin, led1Channel);

  // ledcSetup(led2Channel, freq, resolution);
  ledcAttachPin(led2Pin, led1Channel);

  //  ledcSetup(led3Channel, freq, resolution);
  ledcAttachPin(led3Pin, led1Channel);

  ledcWrite(led1Channel, 0);

  init_spiffs();

  WiFiManager wifiManager;
  wifiManager.setConfigPortalTimeout(60);
  // wifiManager.setSaveConfigCallback(saveConfigCallback);
  // wifiManager.setSaveParamsCallback(saveConfigCallback);

  wifiManager.autoConnect("Stroboter", "incubator");

  g_strip = new NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod>(g_num_strip_leds, g_strip_pin);

  g_strip->Begin();

  for (uint16_t pixel = 0; pixel < g_num_strip_leds; pixel++)
  {
      g_strip->SetPixelColor(pixel, green);
  }

  g_strip->Show();

  if (g_e131.begin(E131_MULTICAST, g_dmx_universe, UNIVERSE_COUNT))   // Listen via Multicast
  {
    Serial.println("DMX: Listening for E.131 DMX data in Universe " + String(g_dmx_universe));
    blink(3);
  }

  else
  {
    Serial.println("DMX: [ERROR] g_e131.begin failed ");
    blink(6);
  }
  
  g_last_dmx_received = millis();
  g_blink_begin_time = millis();
  
  WiFi.setSleep(false);
}

void blink(int count)
{
  for (int i = 0; i < count; i++)
  {
    for (uint16_t pixel = 0; pixel < g_num_strip_leds; pixel++)
    {
      g_strip->SetPixelColor(pixel, green);
    }
    g_strip->Show();

    // ledcWrite(led1Channel, 10);
    delay(200);

    for (uint16_t pixel = 0; pixel < g_num_strip_leds; pixel++)
    {
      g_strip->SetPixelColor(pixel, off);
    }
    g_strip->Show();

  // ledcWrite(led1Channel, 0);
    delay(200);
  }
}

bool process_next_packet()
{
  uint8_t r,g,b;

  if (!g_e131.isEmpty())
  {
    e131_packet_t packet;
    g_e131.pull(&packet);     // Pull packet from ring buffer

    /*
      Serial.printf("Universe %u / %u Channels | Packet#: %u / Errors: %u \n",
            htons(packet.universe),                 // The Universe for this packet
            htons(packet.property_value_count) - 1, // Start code is ignored, we're interested in dimmer data
            g_e131.stats.num_packets,               // Packet counter
            g_e131.stats.packet_errors              // Packet error counter
            );
    */

    int offset = g_dmx_channel_offset;
    g_brightness = packet.property_values[offset + 1];
    g_blinkfreq = packet.property_values[offset + 2] / 10.0f;
    g_blinktime = packet.property_values[offset + 3];
    g_random_range = packet.property_values[offset + 4];
    if (g_blinktime + g_random_range > 255)
    {
      g_random_range = 255 - g_blinktime;
    }
    r = packet.property_values[offset + 5];
    g = packet.property_values[offset + 6];
    b = packet.property_values[offset + 7];

    RgbColor strip_color_new = RgbColor(r,g,b);
    if (g_strip_color != strip_color_new)
    {
      g_strip_color = strip_color_new;
      g_strip_dirty = true;
    }

    if (packet.property_values[offset + 8] > 127)
      g_instastrobe_disabled = true;
    else
      g_instastrobe_disabled = false;

    return true;
  }
  return false;
}

void update_leds()
{
  uint8_t brightness = g_brightness;

  if (g_blinkfreq > 0)
  {
    if (g_cur_time % g_blink_begin_time > g_blinktime_real)
    /* if ((g_cur_time - g_blink_begin_time) > g_blinktime_real) */
    {
      brightness = 0;
    }
    Serial.println("strobing");
    if (g_cur_time % g_blink_begin_time > (1000.0f / g_blinkfreq))
    /* if ((g_cur_time - g_blink_begin_time) > (1000.0f / g_blinkfreq)) */
    {
      g_blink_begin_time = g_cur_time;
      g_blinktime_real = g_blinktime + (int) random(g_random_range);
      brightness = g_brightness;
    }
  }
  ledcWrite(led1Channel, brightness);

  if (g_strip_dirty)
  {
    for (uint16_t pixel = 0; pixel < g_num_strip_leds; pixel++)
    {
        g_strip->SetPixelColor(pixel, g_strip_color);
    }

    g_strip->Show();
    g_strip_dirty = false;
  }
}

void loop() 
{
  g_cur_time = millis();

  // Handle instant strobe push button first ...
  if (!g_instastrobe_disabled && digitalRead(g_instastrobe_pin) == LOW)
  {
    g_strip_color = red;
    g_brightness = 255;
    g_blinkfreq = 12.0f;
    g_blinktime = 20;
    g_random_range = 10;
    g_instastrobe_pressed = true;
    update_leds();
    return;
  }

  if (g_instastrobe_pressed)
  {
    g_strip_color = off;
    g_brightness = 0;
    g_blinkfreq = 0.0f;
    g_blinktime = 0; 
    g_random_range = 0;
    g_instastrobe_pressed = false;
  }

  // ... then handle standalone mode switch ...
  if (digitalRead(g_mode_pin) == HIGH)
  {
    // we are in standalone mode, only set pwm once
    if (!g_standalone)
    {
      Serial.println("Switching to standalone mode.");
      g_standalone = true;
    }

    g_strip_color = blue;
    g_brightness = 150;
    g_blinkfreq = 0.0f;
    g_blinktime = 0;
    update_leds();
    delay(100);
    return;
  }

  // ... then handle DMX last.
  if (g_standalone)
  {
    Serial.println("Switching to DMX mode.");
    g_standalone = false;
    g_strip_color = green;
    g_brightness = 0;
    g_blinkfreq = 0.0f;
    g_blinktime = 0;
  }    

  // if nothing is received in DMX mode, switch off
  bool received  = process_next_packet();
  if (received)
  {
    g_last_dmx_received = g_cur_time;
  }
  else
  {
    /* In DMX mode we should receive packets regularly. If we don't, 
       there could be connectivity issues, so we restart */
    if (g_cur_time % g_last_dmx_received > 60000)
    {
      Serial.println("Restarting because we did not receive a DMX Packet in some time.");
      ESP.restart();

      /* g_strip_color = green;
      g_brightness = 0;
      g_blinkfreq = 0.0f;
      g_blinktime = 0; */
    }
  }
  update_leds();
}
