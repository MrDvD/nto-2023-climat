SemaphoreHandle_t binsem1;
TaskHandle_t fan_handle;

void fan_control(int pin) {
   static int prev_duty;
   if (prev_duty != DUTY) {
      digitalWrite(pin, HIGH);
      delay(DUTY);
      digitalWrite(pin, LOW);
      delay(6000 - DUTY);
      prev_duty = DUTY;
   }
}

boolean is_avg(int ADC[3]) {
   static count = 0;
   if (count == 3) {
      return true;
   }
   ADC[count] = analogRead(34);
   ++count;
   return false;
}

void setup() {
   xTaskCreatePinnedToCore(fan_control,
                           "Fan control",
                           10000,
                           NULL,
                           2,
                           &fan_handle,
                           0);
}

void loop() {
   value = 100 // 0-255 ~ 0-3.3 V
   dacWrite(26, value);
}