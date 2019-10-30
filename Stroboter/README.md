# Der mächtige Stroboter

![Picture of the mighty Stroboter](https://raw.githubusercontent.com/moritzschaefer/dachboden/master/Stroboter/Stroboter1.jpg)

Der mächtige Stroboter ist eine Blechkiste, die Strobo macht. Sie basiert
auf einem ESP32 Mikrocontroller, der mit E1.31 DMX Daten gefüttert werden möchte.
Die Augen sind jeweils 100 Watt LED-Module, der Mund ein 3x3 Muster aus 10 Watt Modulen.
Als LED-Treiber fungieren drei Meanwell LDD-1500H Module, die über die PWM-Ausgänge des 
ESP32 gedimmt werden. Zusätzlich sind die Augenbrauen als WS2812-LED-Strip ebenfalls
an den ESP angeschlossen und über DMX dimmbar. Weitere Details folgen.
