#include <WiFi.h>
#include <WiFiServer.h>
#include <WiFiClient.h>
#include <DHT.h>
#include <Wire.h>
#include <BH1750FVI.h>
#include <BlynkSimpleEsp32.h>
#include <Adafruit_BMP085.h>

#define BLYNK_PRINT Serial
#define DHTTYPE DHT22
#define DHTPIN 4
char auth[] = "lWjkc85U_speEQ9uQSo4kRYbAXF-Y3eX";
const char * ssid = "inan";
const char * password = "dlsks12345";
char ssid2[] = "inan";
char pass2[] = "dlsks12345";

int led = 1; 

WiFiServer server(80);

DHT dht(DHTPIN, DHTTYPE);
float temp, humi;
String webString = "";
unsigned long previousMillis = 0;
const long interval = 2000;

BH1750FVI::eDeviceMode_t DEVICEMODE = BH1750FVI::k_DevModeContHighRes;
BH1750FVI LightSensor(DEVICEMODE );

void gettemphumi() {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        humi = dht.readHumidity();
        temp = dht.readTemperature();
        if (isnan(humi) || isnan(temp)) {
            Serial.println("Failed to read dht sensor.");
            return;
        }
    }
}
void setup(){
  
    Blynk.begin(auth, ssid2, pass2);
    pinMode(led, OUTPUT);
    
    Serial.begin(115200);
    //빛센서(BH1750) 시작
    LightSensor.begin();  
    Serial.println("Running...");
    pinMode(15, OUTPUT);
    Serial.begin(115200);
    delay(10);
    dht.begin();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi connected");
    server.begin();
    Serial.println(WiFi.localIP());
}


void loop() {
    // listen for incoming clients
    WiFiClient client = server.available();
    if (client) {
        //Serial.println("New client");
        String currentLine = "";
        webString = "";
        while (client.connected()) {
            if (client.available()) {
                char c = client.read();
               // Serial.write(c);
                if (c == '\n') {
                    if (currentLine.length() == 0) {
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:text/json");
                        client.println();
                        client.println(webString);
                        client.println();
                        break;
                    } else {
                        currentLine = "";
                    }
                } else if (c != '\r') {
                    currentLine += c;
                }
                if (currentLine.endsWith("GET /events")) {
                    gettemphumi();
                    webString = "{\"temperature\": \"" +String(temp) + "\", \"humidity\": \"" + String(humi) +"\" }";
                    Serial.println(webString);
                    

                }
                //현재 빛량을 가져오기
                uint16_t lux = LightSensor.GetLightIntensity();
                //출력 
                Serial.print("Light: ");
                Serial.println(lux);
                // 0.25초후 대기
                delay(250);
                if (lux >= 10){
                    digitalWrite(15, LOW);   // turn the LED on (HIGH is the voltage level)   
                }
                else{
                    digitalWrite(15, HIGH);   // turn the LED on (HIGH is the voltage level)
                }
                
                Blynk.run();
            }
        }                        
        delay(1);
        client.stop();
        //Serial.println("client disconnected"); 
    }
    
}
