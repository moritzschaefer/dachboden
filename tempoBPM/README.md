
# Project
## Idea
For the control panel project of MitDir2024. 
The user has to tap a button with the tempo of the live music. When the right tempo is tapped during 15sec, then the tasks is valided. 


- [librosa](https://pypi.org/project/librosa/)
- [taptempo](https://pypi.org/project/taptempo/)

## Hardware
- Arcade button
- ~~Rasberry Pi?~~ zu overkill
- ESP 
- Mini Segment display to show the actual taped BPM?
- Mic to get the music as input? 

## Tasks
1. Beat Erkennung (von laufender Musik)
    - Librarie finden: Milan/Dachgit ; [librosa](https://pypi.org/project/librosa/)
    - Librarie anpassen
    - Bauteile/Schaltung finden/ausdenken
        - piezo (hohe lautstärke, mikro empfindlich)
    - Sound Aufnahme / Signalverarbeitung lösen
2. Beat Berechnung (Tap)- Script getbpm.py 
    - eventuell Portierung C++ je nach HW Entscheidung
    - Bauteile/Schaltung finden/ausdenken
        - z.B. 7-Segment display
3. Matching Algorithmus Berechnung/Erkennung
4. Integration des Rätsels in CP