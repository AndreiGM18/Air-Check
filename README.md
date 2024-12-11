# Air Check - Sistem IoT de Monitorizare a Calității Aerului în Timp Real

## Descriere

**Air Check** este un sistem IoT care monitorizează calitatea aerului în timp real, colectând date de la **senzori MQ-135** conectați la plăci **Arduino**. Aceste date sunt transmise prin **modulul ESP-01** folosind protocolul **MQTT** către un **laptop server**. Datele colectate sunt vizualizate într-o aplicație Python, iar utilizatorii pot urmări în timp real evoluția indicelui de calitate a aerului.

### Obiectivele Proiectului:
- **Monitorizarea în timp real** a calității aerului folosind senzori.
- **Transmiterea datelor** de la senzori la server prin Wi-Fi (ESP-01).
- **Vizualizarea datelor** într-un grafic pe aplicația web.
- **Alerte automate** pentru valori periculoase ale poluanților.

---

## Structura Codului

Proiectul este structurat pe 3 părți principale:

1. **Codul pentru ESP-01 și Arduino**: gestionează citirea senzorilor și trimiterea datelor la server.
2. **Aplicația server (Python)**: gestionează și vizualizează datele pe un dashboard interactiv.
3. **Comunicarea prin MQTT**: transmite datele între dispozitive.

Configurare Hardware
1. **Senzori MQ-135**: Conectați la plăcile **Arduino**.
2. **ESP-01**: Conectat modulul la Arduino pentru comunicație wireless prin Wi-Fi.
3. **Actuatori**: LED-uri sau module de alarmă conectate la Arduino.
