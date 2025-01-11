# Memory-2

## TODO

- LEDService umschreiben in ein LedOutput.py (Klassen name sollte auf jeden Fall nicht ---Sensor sein)
- Main.py erweitern mit der eigentlichen Logik
    - Auswerten von den Sensor Daten
    - Ansprechen der Output Devices wie LED und Bildschirm
- Bild Output Klasse erstellen, um das Bild anzuzeigen über OpenCV
- Bild Logik implementieren
    - Schwar Weiß Filter
    - Helligkeit
    - Gaussian Blur o.ä.
    - Die Filter sollten über eine Funktion ansprechbar sein
    - Jeder Filtertyp hat Bedingungen
        - Bspw. Helligkeit filter darf nicht angewendet werden, wenn es noch nicht ganz blurry ist
    