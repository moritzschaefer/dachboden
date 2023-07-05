#include <ArtnetWiFi.h> // library to receive ArtNet DMX data
#include <Arduino.h>

// ArtNet settings
#define UNIVERSE_RCV 5U // DMX universe to listen for RPM data
#define RCV_CHANNEL_START 0U // first DMX channel to read RPM values from

uint16_t g_rpm1 = 0;
uint16_t g_rpm2 = 0;

const int pin1 = 2;  // GPIO pin 2
const int pin2 = 12; // GPIO pin 12

unsigned long delay1 = -1;
unsigned long delay2 = -1;

bool send_strobo = 0;

unsigned long previousStroboTime1 = 0;
unsigned long previousStroboTime2 = 0;
unsigned long currentMillis = 0;
unsigned long g_last_packet_time = 0;


// Wifi Setting

//Wifi settings
const char* ssid = "UhrControl";
const char* password = "zeitreise12";


// connect to wifi – returns true if successful or false if not
bool ConnectWifi(void)
{
  bool state = true;
  int i = 0;

  WiFi.begin(ssid, password);
  Serial.println("");
  Serial.println("Connecting to WiFi");
  
  // Wait for connection
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (i > 20){
      state = false;
      break;
    }
    i++;
  }
  if (state){
    Serial.println("");
    Serial.print("Connected to ");
    Serial.println(ssid);
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("Connection failed.");
  }
  
  return state;
}



// Artnet settings
ArtnetWiFi artnet;


void receive_artnet(const uint8_t* data, const uint16_t size)
{
  /* Serial.printf("Received ArtNet package.\n"); */
  g_last_packet_time = millis(); // remember when we last received a packet

  /* RPM is a 16 bit value split to two 8 bit channels */
  g_rpm1 = (data[RCV_CHANNEL_START + 4]) << 8;
  g_rpm1 = g_rpm1 | (data[RCV_CHANNEL_START + 5]); 

  g_rpm2 = (data[RCV_CHANNEL_START + 6]) << 8;
  g_rpm2 = g_rpm2 | (data[RCV_CHANNEL_START + 7]); 

}

void setup()
{
  Serial.begin(115200); // enable serial output for debug
  Serial.println(); // ensure we start at the beginning of the line
  ConnectWifi();
  artnet.begin();
  artnet.subscribe(UNIVERSE_RCV, receive_artnet);
  Serial.println(F("listening for ArtNet data."));
  
  
  // Initialize GPIO pins as outputs
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);

}

void loop()
{
    artnet.parse(); // must be called everly loop
    send_to_strobo();
}


void send_to_strobo()
{
    if( g_rpm1 > 0){
      delay1 = 60000 / g_rpm1;
    } else{
      delay1 = -1;
    }
    if( g_rpm2 > 0){
      delay2 = 60000 / g_rpm2;
    } else{
      delay2 = -1;
    }
    
    currentMillis = millis();
    

    if (currentMillis - previousStroboTime1 >= delay1) {
      // Send a signal on pin1
      digitalWrite(pin1, HIGH);
      previousStroboTime1 = currentMillis;
      send_strobo = 1;
    }  
    if (currentMillis - previousStroboTime2 >= delay2) {
      // Send a signal on pin1
      digitalWrite(pin2, HIGH);
      previousStroboTime2 = currentMillis;
      send_strobo = 1;
    }  
    if(send_strobo) {
      
      // delayMicroseconds(5);
      delay(20);
    }
    if ( !send_strobo || (currentMillis % 1000 <= 100)) {
      // We print not to often
      Serial.printf("RPM %u %u Delay %lu %lu Time %lu Strobo %d \n",  g_rpm1, g_rpm2, delay1, delay2, currentMillis, send_strobo);
    }
      digitalWrite(pin1, LOW);
      digitalWrite(pin2, LOW);
      send_strobo = 0;
}


