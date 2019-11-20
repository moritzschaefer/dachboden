#include <SPIFFS.h>
#include <ESPAsyncE131.h>
#include <WiFiManager.h>

// OTA
#include <ArduinoOTA.h>

#define UNIVERSE_COUNT 1

int g_dmx_universe = 5;
int g_dmx_channel_offset = 140;
uint8_t g_brightness = 0;
float g_blinkfreq = 0;
uint8_t g_blinktime = 0;
uint8_t g_random_range = 0;
uint8_t g_blinktime_real = 0;
unsigned long g_blink_begin_time = 0;
unsigned long g_last_dmx_received = 0;
bool g_strip_dirty = false;

unsigned long g_cur_time = 0;

// the number of the LED pin
const int led1Pin = 17;  // 17 corresponds to GPIO17

// setting PWM properties
const int freq = 217;
const int led1Channel = 0;
const int resolution = 8;
const int max_brightness = 255;

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
 
  ledcSetup(led1Channel, freq, resolution);
  ledcAttachPin(led1Pin, led1Channel);

  ledcWrite(led1Channel, 0);

  init_spiffs();

  WiFiManager wifiManager;
  wifiManager.setConfigPortalTimeout(180);
  // wifiManager.setSaveConfigCallback(saveConfigCallback);
  // wifiManager.setSaveParamsCallback(saveConfigCallback);

  if (!wifiManager.autoConnect("UVStrobe", "incubator"))
  {
    ESP.restart();
  }
    
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

  g_blink_begin_time = millis();
  g_last_dmx_received = millis();
  
  WiFi.setSleep(false);
  /* Set up OTA updates. */
  // Port defaults to 8266
  // ArduinoOTA.setPort(8266);

  // Hostname defaults to esp8266-[ChipID]
  ArduinoOTA.setHostname("UVStrobe");

  // No authentication by default
  ArduinoOTA.setPassword("incubator");

  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else { // U_SPIFFS
      type = "filesystem";
    }
    SPIFFS.end();

    // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
    Serial.println("Start updating " + type);
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    }
  });
  ArduinoOTA.begin();
  Serial.println("UVStrobe ready to party!");
}

void blink(int count)
{
  for (int i = 0; i < count; i++)
  {
    ledcWrite(led1Channel, 10);
    delay(200);
    ledcWrite(led1Channel, 0);
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
    
    return true;
  }
  return false;
}

void update_leds()
{
  uint8_t brightness = g_brightness;

  if (g_blinkfreq > 0)
  {
    if (g_cur_time - g_blink_begin_time > g_blinktime_real)
    /* if ((g_cur_time - g_blink_begin_time) > g_blinktime_real) */
    {
      brightness = 0;
    }
    if (g_cur_time - g_blink_begin_time > (1000.0f / g_blinkfreq))
    /* if ((g_cur_time - g_blink_begin_time) > (1000.0f / g_blinkfreq)) */
    {
      g_blink_begin_time = g_cur_time;
      g_blinktime_real = g_blinktime + (int) random(g_random_range);
      brightness = g_brightness;
    }
  }
  ledcWrite(led1Channel, brightness);
}

void loop()
{
  ArduinoOTA.handle();

  g_cur_time = millis();

  // if nothing is received in DMX mode, switch off
  bool received  = process_next_packet();
  if (received)
  {
    g_last_dmx_received = g_cur_time;
  } 
  else
  {
    // Switch eyes off, if there was no packet for some time
    if (g_cur_time - g_last_dmx_received > 60000)
    {
      Serial.println("Restarting because we did not receive a DMX Packet in some time.");
      ESP.restart();
    }
  }
  update_leds();
}
