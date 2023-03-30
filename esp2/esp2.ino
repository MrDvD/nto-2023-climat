#include <WiFi.h>
#include <WiFiClient.h>
#include <iostream>
#include <string>
#include <ArduinoJson.h>
#include <regex>
#include <ESP32Servo.h>

#define SSTR(x) static_cast< std::ostringstream & >( \
                  (std::ostringstream() << std::dec << x)) \
                  .str()
#define pin 34

int a0 = 0;
int a1;

float temp;
int window = 0;
const char ssdi[] = "smartpark";
const char pass[] = "15873903";
const char *ip = "10.0.20.21";
int port = 7001;

std::regex pattern("\r\n\r\n(.+)");

std::string str;

Servo myservo;

void setup() {
  Serial.begin(115200);
  analogReadResolution(10);

  myservo.attach(25);

  ledcSetup(0, 16, 4);
  ledcAttachPin(26, 0);
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

DynamicJsonDocument response_doc(64);
int windk = 0;
int vent = 0;
int win;
void loop() {
  // put your main code here, to run repeatedly:
  WiFiClient client;
  client.connect(ip, port);
  a1 = analogRead(pin);

  String sd = (SSTR(a1)).c_str();
  client.print("i" + sd);
  Serial.println(a1);

  String response = client.readString();
  Serial.println(response);
  // a1 = a0;



  std::string data = response.c_str();
  deserializeJson(response_doc, data);
  String window = response_doc["window"];
  String pwm = response_doc["pwm"];
  Serial.println(pwm);
  vent = atoi(pwm.c_str());
  ledcWrite(0, atoi(pwm.c_str()));
  win = atoi(window.c_str());
  Serial.printf("win: %d, windk, %d\n", win, windk);
  if ((win == 1) && (windk == 0)) {
    for (int pos = 0; pos <= 180; pos += 1) {
      myservo.write(pos);
      delay(15);
      Serial.print("1IF: ");
      Serial.print(pos);
    }
    windk = 1;
  }
  if ((win == 0) && (windk == 1)) {
    for (int pos = 180; pos >= 0; pos -= 1) {
      myservo.write(pos);
      delay(15);
      Serial.print("2IF: ");
      Serial.print(pos);
    }
    windk = 0;
  }


  client.stop();
  delay(100);
}
