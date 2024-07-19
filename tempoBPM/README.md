
# Project
## Idea
For the control panel project of MitDir2024. 
The user has to tap a button with the tempo of the live music. When the right tempo is tapped during 15sec, then the tasks is valided. 

Interesting python librairies for the project:
- [librosa](https://pypi.org/project/librosa/)
- [taptempo](https://pypi.org/project/taptempo/)
- [aubio](https://aubio.org/) used also for the [dachboden quallen](https://github.com/moritzschaefer/dachboden/tree/master/quallen/steuersoftware). Tempo and beat tracking as feature.

## Hardware
- Arcade button
- ~~Rasberry Pi?~~ zu overkill
- ESP 
- Mini Segment display to show the actual taped BPM?
- Mic to get the music as input? 

## Tasks
1. Beat Erkennung 
    - [x] Library finden: 
        [aubio](https://aubio.org/) ; 
        -> Probleme mit pip (dep. veraltet)
        [librosa](https://pypi.org/project/librosa/)
    1.1 Song-Erkennung
    - [x] mit Songs (mp3 files)
        - siehe: "beatdetect.py"
    1.2 von laufender Musik
    - [ ] Sound Aufnahme / Signalverarbeitung lösen
    - [ ] Library anpassen:
        - [ ] realtime sound analyse
        - [ ] Optimierung
    - [ ] Bauteile/Schaltung finden/ausdenken
        - piezo (hohe lautstärke, mikro empfindlich)
2. Beat Berechnung (Tap)- 
    - [x] Testskript
        - Script getbpm.py 
    //- eventuell Portierung C++ je nach HW Entscheidung
    - Bauteile/Schaltung finden/ausdenken
        - z.B. 7-Segment display
3. Matching Algorithmus Berechnung/Erkennung
4. Integration des Rätsels in CP

Ask ChatGPT to write an algorithm, see here: https://chat.openai.com/share/ad60b325-c608-4745-8155-205fedea27d4

# Notizen
- Model: Raspberry Pi 3 Model B Rev 1.2
- sich zu dem Raspberrz Pi zu verbinden: ssh tempo
- Hostname aendern: cat .ssh/config 
- Raspberry Pi Pin header: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
- Python Library: https://pypi.org/project/RPi.GPIO/
- Der - geht auf ground
- Shutdown: sudo shutdown 0

Ground to negative
Power to positive

LED 22
+ to the GPIO (22)
- to ground 
Button 18
com to ground
no to gpio

