#include <FS.h>

#ifdef ESP32
#include <SPIFFS.h>
#endif

#include <ESPAsyncE131.h>
#include <WiFiManager.h>

// OTA
#include <ArduinoOTA.h>

#define UNIVERSE_COUNT 1
#define NAME "EDM"
#define PASSWORD "topsecret"

int g_dmx_universe = 5;
int g_dmx_channel_offset = 180;

uint16_t g_brightness = 0;
float   g_blinkfreq = 0;
uint8_t g_blinktime = 0;
uint8_t g_random_range = 0;
uint8_t g_red = 0;
uint8_t g_green = 0;
uint8_t g_blue = 0;
uint8_t g_white = 0;

uint8_t g_blinktime_real = 0;
unsigned long g_blink_begin_time = 0;
unsigned long g_last_dmx_received = 0;

unsigned long g_cur_time = 0;

const int g_red_pin = 5; 
const int g_green_pin = 17; 
const int g_blue_pin = 16; 
const int g_white_pin = 4; 

// setting PWM properties
const int freq = 5000;

const int g_led_red_channel = 0;
const int g_led_green_channel = 1;
const int g_led_blue_channel = 2;
const int g_led_white_channel = 3;

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

  ledcSetup(g_led_red_channel, freq, resolution);
  ledcAttachPin(g_red_pin, g_led_red_channel);
  ledcWrite(g_led_red_channel, 0);

  ledcSetup(g_led_green_channel, freq, resolution);
  ledcAttachPin(g_green_pin, g_led_green_channel);
  ledcWrite(g_led_green_channel, 0);

  ledcSetup(g_led_blue_channel, freq, resolution);
  ledcAttachPin(g_blue_pin, g_led_blue_channel);
  ledcWrite(g_led_blue_channel, 0);
  
  ledcSetup(g_led_white_channel, freq, resolution);
  ledcAttachPin(g_white_pin, g_led_white_channel);
  ledcWrite(g_led_white_channel, 0);

  init_spiffs();

  WiFiManager wifiManager;
  wifiManager.setConfigPortalTimeout(180);
  // wifiManager.setSaveConfigCallback(saveConfigCallback);
  // wifiManager.setSaveParamsCallback(saveConfigCallback);

  if (!wifiManager.autoConnect(NAME, PASSWORD))
  {
    Serial.println("Restarting because we could not connect to WiFi.");
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

#ifdef ESP32
  WiFi.setSleep(false);
#endif
  /* Set up OTA updates. */
  // Port defaults to 8266
  // ArduinoOTA.setPort(8266);

  // Hostname defaults to esp8266-[ChipID]
  ArduinoOTA.setHostname(NAME);

  // No authentication by default
  ArduinoOTA.setPassword(PASSWORD);

  // Password can be set with it's md5 value as well
  // MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
  // ArduinoOTA.setPasswordHash("21232f297a57a5a743894a0e4a801fc3");
  
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
  Serial.println(NAME " ready to party!");
}

void blink(int count)
{
  for (int i = 0; i < count; i++)
  {
    ledcWrite(g_led_red_channel, 255);
    delay(200);
    ledcWrite(g_led_red_channel, 0);
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
    g_red = packet.property_values[offset + 5];
    g_green = packet.property_values[offset + 6];
    g_blue = packet.property_values[offset + 7];
    g_white = packet.property_values[offset + 8];
    
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
    {
      brightness = 0;
    }
    if (g_cur_time - g_blink_begin_time > (1000.0f / g_blinkfreq))
    {
      g_blink_begin_time = g_cur_time;
      g_blinktime_real = g_blinktime + (int) random(g_random_range);
      brightness = g_brightness;
    }
  }

  ledcWrite(g_led_red_channel, (int) (g_red * brightness / 255.0f));
  ledcWrite(g_led_green_channel, (int) (g_green * brightness / 255.0f));
  ledcWrite(g_led_blue_channel, (int) (g_blue * brightness / 255.0f));
  ledcWrite(g_led_white_channel, (int) (g_white * brightness / 255.0f));
}

void loop() 
{
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
      Serial.println("Restarting because of DMX inactivity.");                                                                                                                   
      ESP.restart();
    }
  }
  update_leds();
}
