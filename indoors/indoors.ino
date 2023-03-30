#include <WiFi.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

const char ssid[] = "smartpark";
const char pass[] = "15873903";
const char *ip = "10.0.20.21";
int port = 7001;

Servo win_obj;
DynamicJsonDocument response_doc(64);

void setup() {
  Serial.begin(115200);

  // PINS
  analogReadResolution(10);
  analogSetVRefPin(25);  // ...этой строчкой (1)
  pinMode(26, OUTPUT);
  // ledcSetup(0, 256, 8);
  // ledcAttachPin(26, 0);

  // win_obj.setPeriodHertz(50);  // на всякий случай
  win_obj.attach(25);          // пин нужно было принудительно перевести в аналоговый режим... (1)

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

int win_prev;
int ADC[3];

void fan_set(int pin, int value) {
   // dacWrite(26, atoi(pwm.c_str()));
   // не забыть убрать pinMode, если меняем
   if (value == 0) {
      digitalWrite(pin, LOW);
   } else {
      digitalWrite(pin, HIGH);
   }
}

void loop() {
  if (!is_avg(ADC)) {
     continue;
  }
  int avg_temp = (ADC[0] + ADC[1] + ADC[2]) / 3;
  Serial.printf("avg_temp: %d\n", avg_temp);

  WiFiClient client;
  client.connect(ip, port);
  client.printf("i%d", temp_volt);

  String response = client.readString();
  Serial.printf("response: %s\n", response.c_str());
  client.stop();

  std::string response_str = response.c_str();
  deserializeJson(response_doc, response_str);

  String window = response_doc["window"];
  int win_curr = atoi(window.c_str());
  Serial.printf("win_curr: %d, win_prev: %d\n", win_curr, win_prev);

  String pwm = response_doc["pwm"];
  Serial.printf("pwm: %d\n", pwm);
  int pwm_int = atoi(pwm.c_str());
  fan_set(26, pwm_int);

  // вентиляторы с подключением меньше четырёх проводов не работают на pwm:
  // для них нужно искать собственный модуль для контроля, либо вручную имитировать pwm.
  // shorturl.at/lxEIQ

  // у нас может быть сервопривод непрерывного вращения:
  // if (win_curr == 1 && win_prev == 0) {
  //   win_obj.write(180);
  //   delay(50);
  //   win_obj.write(90);
  //   win_prev = win_curr;
  // }
  // if (win_curr == 0 && win_prev == 1) {
  //   win_obj.write(0);
  //   delay(50);
  //   win_obj.write(90);
  //   win_prev = win_curr;
  // }
  if (win_curr == 1 && win_prev != win_curr) {
     win_prev = win_curr;
     Serial.print("1IF: ");
     for (int pos = 0; pos <= 180; ++pos) {
        win_obj.write(pos);
        Serial.print(pos);
        delay(15);
     }
     Serial.print('\n');
  }
  if (win_curr == 0 && win_prev != win_curr) {
     win_prev = win_curr;
     Serial.print("2IF: ");
     for (int pos = 180; pos >= 0; --pos) {
        win_obj.write(pos);
        Serial.print(pos);
        delay(15);
     }
     Serial.print('\n');
  }
  delay(150);
}