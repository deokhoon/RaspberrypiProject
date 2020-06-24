////////////////////////////MAIN

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
char auth[] ="lWjkc85U_speEQ9uQSo4kRYbAXF-Y3eX";
const char * ssid ="inan";
const char * password ="dlsks12345";
char ssid2[] ="inan";
char pass2[] ="dlsks12345";
int led =1; 
WiFiServer server(80);
DHT dht(DHTPIN, DHTTYPE);
float temp, humi;
String webString ="";
unsigned long previousMillis =0;
const long interval =2000;
BH1750FVI::eDeviceMode_t DEVICEMODE = BH1750FVI::k_DevModeContHighRes;
BH1750FVI LightSensor(DEVICEMODE );
void gettemphumi() { // 온습도 함수
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) { // 온습도를 받기 위한 조건문
        previousMillis = currentMillis;
        humi = dht.readHumidity(); // 습도를 받는 변수
        temp = dht.readTemperature(); // 온도를 받는 변수
        if (isnan(humi) || isnan(temp)) { // 오류 
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
        String currentLine ="";
        webString ="";
        while (client.connected()) {
            if (client.available()) {
                char c = client.read();
               // Serial.write(c);
                if (c =='\n') {
                    if (currentLine.length() ==0) {
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:text/json");
                        client.println();
                        client.println(webString);
                        client.println();
                        break;
                    } else {
                        currentLine ="";
                    }
                } else if (c !='\r') {
                    currentLine += c;
                }
                if (currentLine.endsWith("GET /events")) { // 온습도 정보 웹페이지 출력
                    gettemphumi();
					// 온습도 정보 출력
                    webString ="{\"temperature\": \""+String(temp) +"\", \"humidity\": \""+ String(humi) +"\" }";
                    Serial.println(webString);
                    
                }
                //현재 빛량을 가져오기
                uint16_t lux = LightSensor.GetLightIntensity();
                //출력 
                Serial.print("Light: ");
                Serial.println(lux);
                // 0.25초후 대기
                delay(250);
                if (lux >=10){
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

///////////////////////// 웹 동작 소스
import requests
import json
from flask import Flask, render_template
try:
	from urllib.request import urlopen #python 3
	from urllib.error import HTTPError, URLError
except ImportError:
	from urllib2 import urlopen #python 2
	from urllib2 import HTTPError, URLError
#import json
deviceIp ="192.168.0.108"
portnum ="80"
base_url ="http://"+ deviceIp +":"+ portnum
events_url = base_url +"/events"
app = Flask(__name__, template_folder=".")
KAKAO_TOKEN ="bk5R_q9H-PHuV8LGr-LrPCS76KTrCJkd2rRMmgo9dRkAAAFyxogY7g"# 카카오톡 토큰 
def send_to_kakao(text): # 내 카카오톡 서버와 연동하여 온습도 정보를 보내는 함수 
    header = {"Authorization": 'Bearer '+ KAKAO_TOKEN}
    url ="https://kapi.kakao.com/v2/api/talk/memo/default/send"
    post = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://developers.kakao.com",
            "mobile_web_url": "https://developers.kakao.com"
        },
    }
    data2 = {"template_object": json.dumps(post)}
    return requests.post(url, headers=header, data=data2)
@app.route('/events')
def getevents():
	u = urlopen(events_url)
	data =""
	count =0
	try:
		#data = u.readlines()
		data = u.read()
		print(data)
	
		count = count +1
		send_to_kakao(data)
		if count % 10 ==0:
			send_to_kakao("ttt test 10seconds" )
			count =0
	except HTTPError as e:
		print("HTTP error: %d" % e.code)
	except URLError as e:
		print("Network error: %s" % e.reason.args[1])
	return data
@app.route('/')
def dht22chart():
	return render_template("dhtchart.html")
if __name__ =='__main__':
	app.run(host="192.168.0.107", port='5001')

