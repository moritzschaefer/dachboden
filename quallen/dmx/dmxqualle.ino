#include <FS.h>

#ifdef ESP32
#include <SPIFFS.h>
#endif

#include <NeoPixelBus.h>
#include <ESPAsyncE131.h>
#include <ArduinoJson.h>
#include <WiFiManager.h>

#define MAX_JELLIES 5
#define CHANNELS_PER_JELLY 6
#define UNIVERSE_COUNT 1    // Total number of Universes to listen for, starting at UNIVERSE
#define LED_PIN    5
#define CONFIG_TRIGGER_PIN 4

struct Jelly
{
    int num_leds = 0;
    uint8_t brightness = 0;
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t blinkfreq = 0;
    uint8_t blinktime = 0;
    unsigned long blink_begin_time = 0;
    RgbColor dimmedColor;
};

String g_name = "JellyControl";
String g_password = "topsecret";

int g_num_jellies = 0;
int g_num_leds = 0;
Jelly jellies[MAX_JELLIES];

int g_dmx_universe = 1;
int g_dmx_channel_offset = 0;

RgbColor red(255, 0, 0);
RgbColor green(0, 255, 0);
RgbColor blue(0, 0, 255);
RgbColor white(255);
RgbColor black(0);

NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> *strip;

// ESPAsyncE131 instance with UNIVERSE_COUNT buffer slots
ESPAsyncE131 g_e131(UNIVERSE_COUNT);

bool shouldSaveConfig = false;

void saveConfigCallback () {
    Serial.println("Should save config");
    shouldSaveConfig = true;
}

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

bool loadConfig() {
    File configFile = SPIFFS.open("/config.json", "r");
    if (!configFile) {
        Serial.println("Failed to open config file");
        return false;
    }

    size_t size = configFile.size();
    if (size > 1024) {
        Serial.println("Config file size is too large");
        return false;
    }

    // Allocate a buffer to store contents of the file.
    std::unique_ptr<char[]> buf(new char[size]);

    configFile.readBytes(buf.get(), size);

    StaticJsonBuffer<200> jsonBuffer;
    JsonObject& json = jsonBuffer.parseObject(buf.get());

    if (!json.success()) {
        Serial.println("Failed to parse config file");
        return false;
    }

    g_name = json["name"].as<String>();
    g_password = json["password"].as<String>();
    g_dmx_universe = json["dmx_universe"];
    g_dmx_channel_offset = json["dmx_channel_offset"];
    jellies[0].num_leds = json["num_leds0"];
    jellies[1].num_leds = json["num_leds1"];
    jellies[2].num_leds = json["num_leds2"];
    jellies[3].num_leds = json["num_leds3"];
    jellies[4].num_leds = json["num_leds4"];

    Serial.println("Successfully loaded config from SPIFFS");

    return true;
}

bool saveConfig() 
{
    StaticJsonBuffer<200> jsonBuffer;
    JsonObject& json = jsonBuffer.createObject();

    json["name"] = g_name;
    json["password"] = g_password;
    json["dmx_universe"] = g_dmx_universe;
    json["dmx_channel_offset"] = g_dmx_channel_offset;
    json["num_leds0"] = jellies[0].num_leds;
    json["num_leds1"] = jellies[1].num_leds;
    json["num_leds2"] = jellies[2].num_leds;
    json["num_leds3"] = jellies[3].num_leds;
    json["num_leds4"] = jellies[4].num_leds;

    File configFile = SPIFFS.open("/config.json", "w");
    if (!configFile) {
        Serial.println("Failed to open config file for writing");
        return false;
    }

    json.printTo(configFile);
    Serial.println("Saved config to SPIFFS");
    return true;
}

void setup() {
    Serial.begin(115200);
    delay(10);

#ifdef ESP32
    Serial.println("Running on Core " + String(xPortGetCoreID()));
#endif

    /* SPIFFS.format(); // TODO: automatically on first run, for now uncomment - upload - comment */

    /* if (!SPIFFS.begin())  */
    /* { */
        /* Serial.println("Failed to mount FS"); */
        /* return; */
    /* } */
    init_spiffs();

    //   pinMode(CONFIG_TRIGGER_PIN, INPUT);
    pinMode(CONFIG_TRIGGER_PIN, INPUT_PULLUP);

    loadConfig();

    WiFiManager wifiManager;

    wifiManager.setSaveConfigCallback(saveConfigCallback);
    wifiManager.setSaveParamsCallback(saveConfigCallback);

    char buf[20];
    char buf2[20];

    String(g_name).toCharArray(buf, 20);
    WiFiManagerParameter cfg_name("name", "Name", buf, 20);
    String(g_password).toCharArray(buf, 20);
    WiFiManagerParameter cfg_password("password", "Password", buf, 20);
    String(g_dmx_universe).toCharArray(buf, 4);
    WiFiManagerParameter cfg_dmx_universe("dmx_universe", "DMX Universe", buf, 4);
    String(g_dmx_channel_offset).toCharArray(buf, 4);
    WiFiManagerParameter cfg_dmx_channel_offset("dmx_channel_offset", "Channel Offset", buf, 4);
    String(jellies[0].num_leds).toCharArray(buf, 4);
    WiFiManagerParameter cfg_num_leds0("num_leds0", "Num LEDs Jelly 0", buf, 4);
    String(jellies[1].num_leds).toCharArray(buf, 4);
    WiFiManagerParameter cfg_num_leds1("num_leds1", "Num LEDs Jelly 1", buf, 4);
    String(jellies[2].num_leds).toCharArray(buf, 4);
    WiFiManagerParameter cfg_num_leds2("num_leds2", "Num LEDs Jelly 2", buf, 4);
    String(jellies[3].num_leds).toCharArray(buf, 4);
    WiFiManagerParameter cfg_num_leds3("num_leds3", "Num LEDs Jelly 3", buf, 4);
    String(jellies[4].num_leds).toCharArray(buf, 4);
    WiFiManagerParameter cfg_num_leds4("num_leds4", "Num LEDs Jelly 4", buf, 4);

    //  wifiManager.setAPCallback(configModeCallback);
    wifiManager.addParameter(&cfg_name);
    wifiManager.addParameter(&cfg_password);
    wifiManager.addParameter(&cfg_dmx_universe);
    wifiManager.addParameter(&cfg_dmx_channel_offset);
    wifiManager.addParameter(&cfg_num_leds0);
    wifiManager.addParameter(&cfg_num_leds1);
    wifiManager.addParameter(&cfg_num_leds2);
    wifiManager.addParameter(&cfg_num_leds3);
    wifiManager.addParameter(&cfg_num_leds4);

    String(g_name).toCharArray(buf, 20);
    String(g_password).toCharArray(buf2, 20);

    //wifiManager.resetSettings();

    if ( digitalRead(CONFIG_TRIGGER_PIN) == LOW ) 
    {
        Serial.println("WiFi Configuration Button triggered");

        wifiManager.startConfigPortal(buf, buf2);
        Serial.println("WiFi Configuration Portal exited");
    }
    else
    {
        Serial.println("using WiFiManager AutoConnect");
        wifiManager.autoConnect(buf, buf2);
    }

    g_name               = String(cfg_name.getValue());
    g_password           = String(cfg_password.getValue());
    g_dmx_universe       = String(cfg_dmx_universe.getValue()).toInt();
    g_dmx_channel_offset = String(cfg_dmx_channel_offset.getValue()).toInt();
    jellies[0].num_leds  = String(cfg_num_leds0.getValue()).toInt();
    jellies[1].num_leds  = String(cfg_num_leds1.getValue()).toInt();
    jellies[2].num_leds  = String(cfg_num_leds2.getValue()).toInt();
    jellies[3].num_leds  = String(cfg_num_leds3.getValue()).toInt();
    jellies[4].num_leds  = String(cfg_num_leds4.getValue()).toInt();

    if (shouldSaveConfig) {
        saveConfig();
    }

    Serial.println("Setings:");
    Serial.println("name: "               + String(g_name));
    Serial.println("password: "           + String(g_password));
    Serial.println("DMX universe: "       + String(g_dmx_universe));
    Serial.println("DMX channel offset: " + String(g_dmx_channel_offset));
    Serial.println("jelly 0 num_leds: "   + String(jellies[0].num_leds));
    Serial.println("jelly 1 num_leds: "   + String(jellies[1].num_leds));
    Serial.println("jelly 2 num_leds: "   + String(jellies[2].num_leds));
    Serial.println("jelly 3 num_leds: "   + String(jellies[3].num_leds));
    Serial.println("jelly 4 num_leds: "   + String(jellies[4].num_leds));

    // count jellies and calculate total num leds
    for (int i = 0; i < MAX_JELLIES; i++)
    {
        if (jellies[i].num_leds < 1)
        {
            break;
        }
        g_num_leds += jellies[i].num_leds;
        g_num_jellies++;
    }

    Serial.println("Using " + String(g_num_jellies) + " jellies with " +
            String(g_num_leds) + " total LEDS");

#ifdef ESP32
    strip = new NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod>(g_num_leds, LED_PIN);
#endif

#ifdef ESP8266
    strip = new NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod>(g_num_leds, LED_PIN);
#endif

    strip->Begin();
    strip->Show();

    for (uint16_t pixel = 0; pixel < g_num_leds; pixel++)
    {
        strip->SetPixelColor(pixel, red);
    }
    strip->Show();

    Serial.print(F("Connected with IP: "));
    Serial.println(WiFi.localIP());

    // Choose one to begin listening for E1.31 data
    //if (g_e131.begin(E131_UNICAST))                               // Listen via Unicast
    if (g_e131.begin(E131_MULTICAST, g_dmx_universe, UNIVERSE_COUNT))   // Listen via Multicast
        Serial.println("DMX: Listening for E.131 DMX data in Universe " + String(g_dmx_universe));
    else
        Serial.println("DMX: [ERROR] g_e131.begin failed ");

#ifdef ESP32
    // Turon of wifi power saving for better latency
    WiFi.setSleep(false);
#endif
}

bool process_next_packet()
{
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


        for (int i = 0; i < g_num_jellies; i++)
        {
            int offset = g_dmx_channel_offset + (i * CHANNELS_PER_JELLY);
            jellies[i].brightness = packet.property_values[offset + 1];
            jellies[i].r = packet.property_values[offset + 2];
            jellies[i].g = packet.property_values[offset + 4];
            jellies[i].b = packet.property_values[offset + 3];
            /* jellies[i].color = RgbColor(packet.property_values[offset + 2], packet.property_values[offset + 4], packet.property_values[offset + 3u]); */
            jellies[i].blinkfreq = packet.property_values[offset + 5] / 10;  
            jellies[i].blinktime = packet.property_values[offset + 6];
            float intensity = jellies[i].brightness / 255.0f;
            /* jellies[i].dimmedColor = RgbColor((int) (jellies[i].color.R * intensity), (int) (jellies[i].color.G * intensity), (int) (jellies[i].color.B * intensity)); */
            jellies[i].dimmedColor = RgbColor((int) (jellies[i].r * intensity), (int) (jellies[i].g * intensity), (int) (jellies[i].b * intensity));
        }
        return true;
    }
    return false;
}

void update_strip()
{
    unsigned long cur_time = millis();
    int cur_led = 0;

    Jelly jelly;
    RgbColor color;

    for (int i = 0; i < g_num_jellies; i++)
    {
        jelly = jellies[i];
        color = jelly.dimmedColor;

        if (jelly.blinkfreq > 0)
        {
            if (jelly.blink_begin_time + jelly.blinktime < cur_time)
            {
                color = black;
            }

            if (jelly.blink_begin_time + (1000 / jelly.blinkfreq) < cur_time)
            {
                jellies[i].blink_begin_time = cur_time;
            }
        }
        //Serial.println("Jelly " + String(i) + " r value 1 " + currentColor.R + " intensity " + intensity + " r value 2 " + color.R);

        for(int j = cur_led; j < cur_led + jelly.num_leds; j++) 
        {
            strip->SetPixelColor(j, color);         //  Set pixel's color (in RAM)
        }

        cur_led = cur_led + jelly.num_leds;
    }
    strip->Show();
}

void loop()
{
    bool received  = process_next_packet();

    update_strip();

    if (!received)
        delay(1);
}
