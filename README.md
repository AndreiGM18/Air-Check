# Air Check - Sistem IoT de Monitorizare a Calității Aerului în Timp Real

## Descriere

**Air Check** este un sistem IoT dedicat monitorizării calității aerului în timp real. Sistemul colectează date de la senzori **MQ-135**, conectați la plăci **ESP8266**. Datele sunt transmise prin protocolul **MQTT** către un server local, iar utilizatorii pot vizualiza în timp real evoluția indicelui de calitate a aerului pe o aplicație web. Acest sistem permite monitorizarea calității aerului și acționarea automată a unor alerte sau dispozitive (LED-uri) în funcție de valorile senzorilor.

### Obiectivele Proiectului:
- **Monitorizarea în timp real** a calității aerului folosind senzori.
- **Transmiterea datelor** de la senzori la server prin Wi-Fi (ESP8266).
- **Vizualizarea datelor** într-un grafic pe aplicația web.
- **Controlul LED-urilor** în funcție de valoarea calității aerului.
- **Alerte automate** pentru valori periculoase ale poluanților.

---

## Structura Codului

Proiectul este structurat pe 3 părți principale:

1. **Codul pentru ESP8266**: Acesta gestionează citirea datelor de la senzorul MQ-135 și trimiterea acestora către server prin protocolul MQTT.
2. **Aplicația server (Python)**: Serverul Python primește datele de la dispozitivele IoT și le vizualizează pe un dashboard interactiv.
3. **Comunicarea prin MQTT**: Sistemul utilizează protocolul MQTT pentru a transmite datele de la ESP8266 la server.

---

## Configurare Hardware

1. **Senzori MQ-135**: Aceștia sunt conectați la plăcile **ESP8266** pentru a monitoriza calitatea aerului.
2. **ESP8266**: Modificarea datelor de la senzorul MQ-135 și trimiterea acestora prin rețeaua Wi-Fi locală.
3. **LED sau Actuatori**: Aceste dispozitive sunt conectate la ESP8266 pentru a indica starea calității aerului (aprinderea unui LED dacă nivelul poluării este prea mare).
4. **Server MQTT**: Se folosește pentru gestionarea comunicației între ESP8266 și aplicația de vizualizare.

---

## Pași pentru Configurare

### 1. **Conectarea Hardware**
   - Conectează senzorul MQ-135 la pinul analogic al plăcii **ESP8266**.
   - Conectează un **LED** la un pin digital al plăcii ESP8266 pentru a acționa ca indicator vizual pentru calitatea aerului.
   - Asigură-te că **ESP8266** este conectat corect la rețeaua ta Wi-Fi pentru a putea transmite datele către serverul MQTT.

### 2. **Configurare Software**
   - Instalează librăriile necesare în Arduino IDE:
     - `ESP8266WiFi`
     - `PubSubClient`
   
   - În Arduino IDE, folosește codul pus la dispozitie in esp.ino pentru a configura placa ESP8266 pentru a trimite datele la un server MQTT.

### 3. **Aplicatia Server (Python)**

Pe server, folosește Python și aplicația MQTT pentru a primi și vizualiza datele transmise de ESP8266. Fișierele template HTML se află în folderul templates/.

### 4. **Mosquitto**

Folosește mosquitto cu această configurare în fișierul mosquitto.conf:
  - listener 1883
  - allow_anonymous true

## Concluzie

**Air Check** este un sistem complet de monitorizare a calității aerului care folosește tehnologia IoT pentru a colecta și vizualiza datele în timp real. Utilizând **MQTT** pentru comunicare și **Wi-Fi** pentru conectivitate, datele sunt trimise de la senzorii conectați la ESP8266 către un server pentru procesare și vizualizare.
