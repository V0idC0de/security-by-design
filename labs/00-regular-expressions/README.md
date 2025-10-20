# 00 Regular Expressions

## Einleitung

Dieses Lab nutzt keine extra Software, sondern die Website [regex101.com](https://regex101.com),
um reguläre Ausdrücke zu behandeln.

Jede der folgenden Teilaufgaben enthält einen Link zu **[regex101.com](https://regex101.com)**,
wo Testdaten für die jeweilige Aufgabe bereits ausgefüllt sind.

Entwickle einen regulären Ausdruck, der die jeweilige Teilaufgabe erfüllt,
sodass die Positiv-Beispiele gematcht werden, während es in den Negativ-Beispielen,
die unter der Zeile `⛔ SHOULD NOT MATCH ⛔` stehen, keine Matches erkennt.

## Teil 1 - Verschiedene Formate

Für dieses Lab nehmen wir an, dass eine Telefonnummer aus **3 bis 5 Ziffern** einer Vorwahl besteht,
sowie **zwischen 4 und 10 Ziffern** für den hinteren Teil der Nummer.
Zwischen diesen Komponenten befindet sich manchmal ein `/`, `-` - manchmal ist dies aber auch nicht der Fall.

Schreibe im folgenden **RegEx 101**-Lab einen regulären Ausdruck, der ...

1. alle Test-Strings matcht UND
2. **keinen** der Negativ-Beispiele matcht

> [!NOTE]
> Denk daran, dass manche Zeichen mit `\` escaped werden müssen,
> weil sie in regulären Ausdrücken sonst eine Bedeutung haben und interpretiert werden!
> RegEx101 markiert fehlerhafte Zeichen **rot**.

> [!NOTE]
> Nutzt die Ankerzeichen `^` und `$`, um zu fordern, dass euer Match am Anfang/Ende der Zeile anliegt.
> So können Matches innerhalb der Zeile vermieden werden.

**RegEx 101:** 🔗 <https://regex101.com/r/91qjBF/1>

## Teil 2 - Ländervorwahl

Die Telefonnummern müssen nun eine gültige erste Ziffer haben.
Entweder ist das erste Zeichen ein `+` oder eine `0`, für Auslands- bzw. Inlandsnummern.
Dieses `+`/`0` zählt für diese Aufgaben **NICHT als Teil der Vorwahl**

**RegEx 101:** 🔗 <https://regex101.com/r/tNx9pV/1>

## Teil 3 - Toleriere Leerzeichen

Manche Benutzer schreiben die Telefonnummern mit einem oder mehreren Leerzeichen
um den `/` oder `-` oder trennen Vorwahl und Hauptteil damit.

**RegEx 101:** 🔗 <https://regex101.com/r/wZIs9y/1>

## (Bonus) Teil 4 - Extraktion aus Texten

Die Telefonnummern sind nun Teil eines Fließtextes aus einer Nachricht.
Stelle sicher, dass **in den Zeilen der Negativ-Beispiele** keine Matches auftreten.

> [!NOTE]
> Für diese Aufgabe ist es in Ordnung, mehr als die Telefonnummer zu matchen,
> um die Negativ-Beispiele von den Positiv-Beispielen zu unterscheiden.

**RegEx 101:** 🔗 <https://regex101.com/r/SQDJdS/1>

### (Bonus Bonus) Teil 4.1 - Extrahierung mit Capture Group

Teile eines regulären Ausdrucks können mit runden Klammern `()` eingeschlossen werden,
um sie zu **extrahieren**. Diese **Capture Groups** können genutzt werden,
um beispielsweise die **Vorwahl** (mit oder ohne Landerkennung) und die **hintere Nummer**
ohne Leer- oder Trennzeichen zu erhalten.

**Setze dies im Fenster von [Teil 4](#bonus-teil-4---extraktion-aus-texten) um.**
