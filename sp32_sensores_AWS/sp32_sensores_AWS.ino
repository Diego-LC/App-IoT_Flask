#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

#include "Light_VEML7700.h"     ////http://librarymanager/All#Light_veml7700
#include "RAK12033-IIM42652.h"
IIM42652 IMU;

Light_VEML7700 VMEL = Light_VEML7700();

const char* ssid = "Android-S21U";  //"TEST2";
const char* password = "qwerty123"; //"Testing_2K23";
String serverUrl = "http://34.239.209.214:8085";
int ledGreenPin = LED_GREEN;
int ledBluePin = LED_BLUE;
const char* nodeName = "nodo1";

// Configuración del cliente NTP
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -14400; // GMT-4 (invierno)
const int daylightOffset_sec = -10800; // GMT-3 (verano)
WiFiUDP udp;
NTPClient timeClient(udp, ntpServer, gmtOffset_sec, daylightOffset_sec);

const char* udpServerIp = "34.239.209.214";
const int udpServerPort = 5002;

float valorTemperatura;
float acc_x ,acc_y ,acc_z;
int valorLuz;
const float fuerzaGiro = 0.6;
time_t timeout = millis();
bool estaLucesAutom = false;
bool encenderLuces = false;
bool estaCalefaccionAutom = false;
bool encenderCalefaccion = false;

void setup() {
  pinMode(ledGreenPin, OUTPUT);
  pinMode(ledBluePin, OUTPUT);
  Serial.begin(115200);
  //udp.begin(1234);
  initSensorLuz();
  setupAcel();
  // Conectarse a la red WiFi
  conectarWifi();
  // Inicializar el cliente NTP y sincronizar la hora
  //sincNTP();
}

void loop() {
  apagadoEncendidoLuces();
  apagadoEncendidoClimatizador();
  time_t now = timeClient.getEpochTime();
  String dateTime = getDateTime(now);
  digitalWrite(ledGreenPin, LOW); // Enciende el LED verde
  String placaGirada = "False";

  // Obtener la hora actual en formato Unix
  unsigned long horaUnix = timeClient.getEpochTime();
  
  if (acelSensorData()){
    placaGirada = "True";
    alertarPuertaAbierta();
    digitalWrite(ledGreenPin, HIGH); // Enciende el LED azul
    delay(80);
  }

  if (millis() - timeout > 800){ // Envia datos cada 1 seg
  
    manejarLuces_Climatizador();
    delay(100);
    timeout = millis();
    // Crea un objeto JSON y almacena los datos
    String jsonString = crearJson(now, placaGirada);
    
    // Realiza una solicitud POST al servidor Flask
    HTTPClient http;
    http.begin(serverUrl + "/api/data");
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonString);

    if (httpResponseCode > 0) {
      Serial.println("Datos enviados, codigo respuesta: " + String(httpResponseCode));
    } else {
      // Aquí puedes manejar el error de manera adecuada
    }

    // Envía los datos por UDP:
    udp.beginPacket(udpServerIp, udpServerPort);
    udp.print(jsonString);
    udp.endPacket();

    imprimirDatos(now);
    http.end();
  }

  //digitalWrite(ledGreenPin, HIGH); // Apaga el LED verde  
  digitalWrite(ledGreenPin, LOW); // Apaga el LED azul
  //delay(500);
}

void alertarPuertaAbierta(){
  StaticJsonDocument<200> jsonData;
  jsonData["puertaAbierta"] = "True";
  // Convierte el JSON en una cadena
  String jsonString;
  serializeJson(jsonData, jsonString);

  HTTPClient http;
  http.begin(serverUrl + "/api/alertarPuertaAbierta");
  http.addHeader("Content-Type", "application/json");
  int httpResponseCode = http.POST(jsonString);
  Serial.println("-----------------------");
  Serial.println("Código de respuesta alerta : " + String(httpResponseCode));
  Serial.println("-----------------------");
}

void manejarLuces_Climatizador(){
  HTTPClient http;
  http.begin(serverUrl + "/api/manejoLucesYtemp");
  http.addHeader("Content-Type", "application/json");
  int codigoRespuesta = http.GET();
  String respuesta;
  DynamicJsonDocument doc(1024);
  if (codigoRespuesta > 0){
    respuesta = http.getString();
    deserializeJson(doc, respuesta);
    datosRecibidos(doc);
  }
  Serial.println("\n///////////////////");
  Serial.println("Código de respuesta: " + doc["apagarLuces"].as<String>());
  Serial.println("/////////////////////////");
}

void datosRecibidos(DynamicJsonDocument doc){
  encenderLuces = stringTobool(doc["encenderLuces"].as<String>());
  encenderCalefaccion = stringTobool(doc["encenderCalefaccion"].as<String>());
  estaLucesAutom = stringTobool(doc["lucesAutom"].as<String>());
  estaCalefaccionAutom = stringTobool(doc["climatizadorAutom"].as<String>());
}

bool stringTobool(String valor){
  if (valor == "0"){
    return true;
  } else {
    return false;
  }
}
void apagadoEncendidoLuces(){
  if (estaLucesAutom){
    if (valorLuz < 100){
      encenderLuces = true;
    } else if (valorLuz > 200){
      encenderLuces = false;
    }
  }
  if (encenderLuces){
    digitalWrite(ledBluePin, HIGH); // Enciende el LED azul
    Serial.println("Encendiendo luces");
  } else {
    digitalWrite(ledBluePin, LOW); // Apaga el LED azul
    Serial.println("Apagando luces");
  }
}

void apagadoEncendidoClimatizador(){
  if (estaCalefaccionAutom){
    if (valorTemperatura < 20){
      encenderCalefaccion = true;
    } else if (valorTemperatura > 25){
      encenderCalefaccion = false;
    }
  }
  if (encenderCalefaccion){
    digitalWrite(ledBluePin, HIGH); // Enciende el LED azul
    Serial.println("Encendiendo climatizador");
  }else {
    digitalWrite(ledBluePin, LOW); // Apaga el LED azul
    Serial.println("Apagando climatizador");
  }
}

String getDateTime(time_t t) {
  struct tm *tm_info;
  char buffer[30];

  tm_info = localtime(&t);

  // Formato de fecha y hora: DD/MM/YYYY hh:mm:ss
  strftime(buffer, 30, "%d/%m/%Y %H:%M:%S", tm_info);
  return String(buffer);
}

void setupAcel() {
  time_t timeout = millis();
  // Initialize Serial for debug output.
  while (!Serial)
  {
    if ((millis() - timeout) < 5000)
    {
      delay(100);
    }
    else
    {
      break;
    }
  }
  Serial.println("RAK12033 Basic Reading example.");

  Wire.begin();
  if (IMU.begin() == false) 
  {
    while (1) 
    {
      Serial.println("IIM-42652 is not connected.");
      delay(4000);
    }
  }
}

boolean acelSensorData() {
  
  IIM42652_axis_t  accel_data;
  IIM42652_axis_t  gyro_data;
  boolean placaGirada = false;
  IMU.ex_idle();
  IMU.accelerometer_enable();
  IMU.temperature_enable();

  delay(100);
  
  IMU.get_accel_data(&accel_data );
  IMU.get_temperature(&valorTemperatura );

  acc_x = ((float)accel_data.x / 2048)*9.81;
  acc_y = ((float)accel_data.y / 2048)*9.81;
  acc_z = ((float)accel_data.z / 2048)*9.81;

  Serial.println("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++");

  Serial.print("Accel X: " + String(acc_x) + "[g]  \nY: " + String(acc_y) + "[g]  \nZ: " + String(acc_z) + "[g]");
  Serial.println("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++");

    // Verificar si la placa ha sido girada en base a la inclinación
  if (abs(acc_z) > fuerzaGiro || abs(acc_y) > fuerzaGiro)
  {
    Serial.println("La placa ha sido girada.");
    placaGirada = true;
  }

  IMU.accelerometer_disable();
  IMU.temperature_disable();
  IMU.idle();
  return placaGirada;
}


void initSensorLuz() {
  // Initialize Serial for debug output

  pinMode(WB_IO2, OUTPUT);
  digitalWrite(WB_IO2, HIGH);
  delay(300);
  time_t timeout = millis();
  if ((millis() - timeout) < 5000)
  {
    delay(100);
  }
  if (!VMEL.begin())
  {
    Serial.println("Sensor not found");
  }

  VMEL.setGain(VEML7700_GAIN_1);
  VMEL.setIntegrationTime(VEML7700_IT_800MS);

  Serial.print(F("Gain: "));
  switch (VMEL.getGain())
  {
    case VEML7700_GAIN_1: Serial.println("1"); break;
    case VEML7700_GAIN_2: Serial.println("2"); break;
    case VEML7700_GAIN_1_4: Serial.println("1/4"); break;
    case VEML7700_GAIN_1_8: Serial.println("1/8"); break;
  }

  Serial.print(F("Integration Time (ms): "));
  switch (VMEL.getIntegrationTime())
  {
    case VEML7700_IT_25MS: Serial.println("25"); break;
    case VEML7700_IT_50MS: Serial.println("50"); break;
    case VEML7700_IT_100MS: Serial.println("100"); break;
    case VEML7700_IT_200MS: Serial.println("200"); break;
    case VEML7700_IT_400MS: Serial.println("400"); break;
    case VEML7700_IT_800MS: Serial.println("800"); break;
  }

  //veml.powerSaveEnable(true);
  //veml.setPowerSaveMode(VEML7700_POWERSAVE_MODE4);

  VMEL.setLowThreshold(10000);
  VMEL.setHighThreshold(20000);
  VMEL.interruptEnable(true);
}

void conectarWifi() {
    WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Conectando a la red WiFi...");
  }
  Serial.println("Conexión WiFi exitosa.");
}

void sincNTP() {
    timeClient.begin();
  while (!timeClient.update()) {
    timeClient.forceUpdate();
  }
  Serial.println(timeClient.getFormattedTime());
}

String crearJson(time_t now, String placaG) {
  int valorLuz = VMEL.readLux();
  StaticJsonDocument<200> jsonData;
  jsonData["time"] = getDateTime(now); // Guarda el tiempo en formato legible
  jsonData["medicionLuz"] = valorLuz;
  //jsonData["medicionAcelerometro"] = "X: "+ String(acc_x) + "[g], Y: "+ String(acc_y) + "[g], Z: "+ String(acc_z);
  jsonData["medicionTemperatura"] = valorTemperatura;
  jsonData["estaPuertaAbierta"] = placaG;
  jsonData["estaLucesAutom"] = estaLucesAutom;
  jsonData["estaCalefaccionAutom"] = estaCalefaccionAutom;
  jsonData["encenderLuces"] = encenderLuces;
  jsonData["encenderCalefaccion"] = encenderCalefaccion;
  jsonData["nombrenodo"] = nodeName;

  // Convierte el JSON en una cadena
  String jsonString;
  serializeJson(jsonData, jsonString);
  Serial.println("Serializado "+ jsonString);

  return jsonString;
}

void imprimirDatos(time_t now){
      
  //Serial.println("Datos enviados.");
  Serial.println("Datos a enviar: time: " + getDateTime(now) + ", medición luz: " + String(valorLuz) + 
  "\ntemperatura: " + String(valorTemperatura) + "[g]\npuerta abierta: " + String("False") + 
  "\nluces autom: " + String(estaLucesAutom) + "\nclimatizador autom: " + String(estaCalefaccionAutom) + 
  "\nencender luces: " + String(encenderLuces) + "\nencender climatizador: " + String(encenderCalefaccion) + 
  "\nnombre nodo: " + nodeName + "\n----------------\n");
  
 /* Serial.print("Accel X: ");
  Serial.print(acc_x);
  Serial.print("[g]  Y: ");
  Serial.print(acc_y);
  Serial.print("[g]  Z: ");
  Serial.print(acc_z);
  Serial.println("[g]");

  Serial.print("Temper : ");
  Serial.print(valorTemperatura);
  Serial.println("[ºC]");

  //Serial.print("Error en la solicitud. Código de respuesta: ");
  //Serial.println(httpResponseCode);*/

}