#include <WiFi.h>

#include <WiFiClient.h>
#include <iostream>
#include <string.h>




int a0 = 0;
int a1;
float temp; 

const char ssdi[] = "smartpark";
const char pass[] = "15873903";
const char *ip = "10.0.20.21";
int port = 7000;

std::string str;

void setup() {
   Serial.begin(115200);
  analogReadResolution(10);
  analogSetAttenuation(ADC_2_5db);

   WiFi.mode(WIFI_STA);
   WiFi.begin(ssdi, pass);
   if (WiFi.waitForConnectResult() != WL_CONNECTED) {
      Serial.println("[WIFI_FAIL]");
      ESP.restart();
   } else {
      Serial.println("[WIFI_SUCCESS]");
      Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
   }
}

void loop() {
  a1 = analogRead(34);
  
  if (a1 !=a0){
    Serial.println(a1);
    WiFiClient client;
    client.connect(ip, port);
    client.print("o"+a1);
    client.stop();
  }
}
