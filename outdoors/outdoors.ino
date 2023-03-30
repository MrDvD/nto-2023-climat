#include <WiFi.h>
#include <WiFiClient.h>
#include <sstream>
#include <driver/adc.h> // IDF

const char ssid[] = "smartpark";
const char pass[] = "15873903";
const char *ip = "10.0.20.21";
int port = 7001;

boolean is_avg(int ADC[3]) {
   static int count = 0;
   if (count == 3) {
      count = 0;
      return true;
   }
   ADC[count] = analogRead(34);
   ++count;
   return false;
}

void setup() {
   Serial.begin(115200);
   
   // PINS
   analogReadResolution(10);
   analogSetAttenuation(ADC_11db);

   WiFi.mode(WIFI_STA);
   WiFi.begin(ssid, pass);
   if (WiFi.waitForConnectResult() != WL_CONNECTED) {
      Serial.println("[WIFI_FAIL]");
      ESP.restart();
   } else {
      Serial.println("[WIFI_SUCCESS]");
      Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
   }
}

int prev_temp = 0;
int ADC[3];

void loop() {
   // IDF
    if (!is_avg(ADC)) {
     return;
  }
  int avg_temp = (ADC[0] + ADC[1] + ADC[2]) / 3;
  Serial.printf("avg_temp: %d\n", avg_temp);


  if (avg_temp != prev_temp){
    prev_temp = avg_temp;
    Serial.println(avg_temp);
    
    WiFiClient client;
    client.connect(ip, port);
    client.printf("o%d", avg_temp);
    client.stop();
    
  }
  delay (1000);
}