#include <WiFi.h>
#include <WiFiClient.h>
#include <sstream>
#include <driver/adc.h> // IDF

const char ssid[] = "smartpark";
const char pass[] = "15873903";
const char *ip = "10.0.20.21";
int port = 7001;

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

void loop() {
   // IDF
   adc1_config_width(ADC_WIDTH_BIT_10); // ширина выбрана случайно, нужно изучить
   int curr_temp = adc1_get_raw(ADC1_CHANNEL_6);
   // int curr_temp = analogRead(34);
   // https://tinyurl.com/2p9396c8 ADC CALIBRATION

   if (curr_temp != prev_temp){
      prev_temp = curr_temp;
      Serial.println(curr_temp);
      
      WiFiClient client;
      client.connect(ip, port);
      client.printf("o%d", curr_temp);
      client.stop();
   }
}