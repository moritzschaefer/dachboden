# Der mächtige Stroboter

![Picture of the mighty Stroboter](https://raw.githubusercontent.com/moritzschaefer/dachboden/master/Stroboter/Stroboter1.jpg)

Der mächtige Stroboter ist eine Blechkiste, die Strobo macht. Sie basiert
auf einem ESP32 Mikrocontroller, der mit E1.31 DMX Daten gefüttert werden möchte.
Die Augen sind jeweils 100 Watt LED-Module, der Mund ein 3x3 Muster aus 10 Watt Modulen.
Als LED-Treiber fungieren drei Meanwell LDD-1500H Module, die über die PWM-Ausgänge des 
ESP32 gedimmt werden. Zusätzlich sind die Augenbrauen als WS2812-LED-Strip ebenfalls
an den ESP angeschlossen und über DMX dimmbar. Der Stroboter verfügt über 
einen Schalter, der ihn als 100 Watt Dauerarbeitslicht schalten kann. Außerdem
gibt es einen großen roten Knopf, den sog. Instastrobe-Button, der in dringenden
Stroboskopmangelsitutationen betätigt werden kann. Die Stromversorgung erfolgt
über ein 48 Volt Netzteil, das im Gehäuse für die Versorgung von Lüftern,
LEDs und Controller durch Step-Down-Wandler bzw. LED-Treiber auf 5, 12 und 36 Volt
angepasst wird. Die maximale Leistung mit voller Helligkeit ist an der Steckdose 
ca. 170 Watt.

## DMX-Kanäle

Der Stroboter lauscht im Universe 5 auf den Kanälen 151 bis 158. Die einzelnen Kanäle sind:

| Kanal         | Funktion      |
| ------------- |:-------------:|
| 151           | Gesamthelligkeit |
| 152           | Strobo Frequenz 0.0 - 25.5 Hz |
| 153           | Strobo Leuchtdauer 0 - 255 ms |
| 154           | Strobo Zufallswert, der auf die Leuchtdauer addiert wird 0 - 255 ms |
| 155           | Augenbrauen Rot |
| 156           | Augenbrauen Grün |
| 157           | Augenbrauen Blau|
| 158           | Wenn <= 127, ist der Instastrobebutton aktiv, sonst nicht |
