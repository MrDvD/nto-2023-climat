#include <WiFi.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

const char ssid[] = "POTENC_PHYS";
const char pass[] = "111111110";
const char *ip = "10.42.0.1";
int port = 7001;
int pos = 0;

Servo myservo;
DynamicJsonDocument response_doc(64);

boolean is_avg(int ADC[3]) {
  static int count = 0;
  if (count == 3) {
    count = 0;
    return true;
  }
  ADC[count] = analogReadMilliVolts(34);

  ++count;
  return false;
}

void setup() {
  Serial.begin(115200);

  // PINS
  analogReadResolution(10);
  // analogSetAttenuation(ADC_11db);
  // analogSetVRefPin(25);  // ...этой строчкой (1)
  // pinMode(26, OUTPUT);
  ledcSetup(5, 256, 8);
  ledcAttachPin(26, 5);

  // myservo.setPeriodHertz(50);  // на всякий случай
  myservo.attach(25);  // пин нужно было принудительно перевести в аналоговый режим... (1)

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
  //  if (value == 0) {
  //     digitalWrite(pin, LOW);
  //  } else {
  //     digitalWrite(pin, HIGH);
  //  }
  ledcWrite(5, value);
}

void loop() {
  if (!is_avg(ADC)) {
    return;
  }
  int avg_temp = (ADC[0] + ADC[1] + ADC[2]) / 3;
  Serial.printf("avg_temp: %d\n", avg_temp);

  WiFiClient client;
  client.connect(ip, port);
  client.printf("i%d", avg_temp);

  String response = client.readString();
  if (response == "") {
    return;
  }
  Serial.printf("response: %s\n", response.c_str());
  client.stop();

  std::string response_str = response.c_str();
  deserializeJson(response_doc, response_str);

  String window = response_doc["window"];
  int win_curr = atoi(window.c_str());
  Serial.printf("win_curr: %d, win_prev: %d\n", win_curr, win_prev);

  String pwm = response_doc["pwm"];
  Serial.printf("pwm: %s\n", pwm.c_str());
  int pwm_int = atoi(pwm.c_str());
  fan_set(26, pwm_int);

  // вентиляторы с подключением меньше четырёх проводов не работают на pwm:
  // для них нужно искать собственный модуль для контроля, либо вручную имитировать pwm.
  // shorturl.at/lxEIQ

  // у нас может быть сервопривод непрерывного вращения:
  // if (win_curr == 1 && win_prev == 0) {
  //   myservo.write(180);
  //   delay(50);
  //   myservo.write(90);
  //   win_prev = win_curr;
  // }
  // if (win_curr == 0 && win_prev == 1) {
  //   myservo.write(0);
  //   delay(50);
  //   myservo.write(90);
  //   win_prev = win_curr;
  // }
  if (win_curr == 1 && win_prev != win_curr) {
    win_prev = win_curr;
    Serial.print("1IF: ");
    for (pos = 0; pos <= 90; pos += 1) {  // goes from 0 degrees to 180 degrees
      // in steps of 1 degree
      myservo.write(pos);  // tell servo to go to position in variable 'pos'
      delay(15);           // waits 15ms for the servo to reach the position
    }
    Serial.print('\n');
  }
  if (win_curr == 0 && win_prev != win_curr) {
    win_prev = win_curr;
    Serial.print("2IF: ");
    for (pos = 90; pos >= 0; --pos) {
      myservo.write(pos);
      Serial.print(pos);
      delay(15);
    }
    Serial.print('\n');
  }
  delay(150);
}