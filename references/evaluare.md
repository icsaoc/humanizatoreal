# Benchmark pilot

Perechi sintetice de referință. Rulează skill-ul pe coloana Înainte și salvează
modelul, parametrii, versiunea catalogului și outputul brut.

| ID | Registru | Înainte | După | Invariant |
|---|---|---|---|---|
| A1 | Administrativ | În cadrul acestui proces, operatorul va proceda la transmiterea cererii până la 15 mai. | Operatorul va transmite cererea până la 15 mai. | Actor și termen |
| A2 | Administrativ | Este important de menționat că instituția poate respinge cererea. | Instituția poate respinge cererea. | Posibilitate |
| A3 | Administrativ | Secretariatul primește dosarele până la ora 16. | Secretariatul primește dosarele până la ora 16. | Control curat |
| L1 | Literar | Este important de menționat că Ana a rămas la poartă după ce ploaia s-a oprit. | După ce ploaia s-a oprit, Ana a rămas la poartă. | Ordine temporală |
| L2 | Literar | „Nu plec”, a spus Mara. În concluzie, Mara a rămas în casă. | „Nu plec”, a spus Mara. A rămas în casă. | Citat și loc |
| L3 | Literar | N-a tras zăvorul. Îl aștepta pe frate-său. | N-a tras zăvorul. Îl aștepta pe frate-său. | Control curat |

Trei cititori locali independenți văd originalul și candidatul în ordine
randomizată, fără etichete. Notează preferința de naturalețe (A/B/egal)
și separat potrivirea de registru. Controalele curate nu intră în pachetele de
vot și se măsoară prin egalitate textuală. Un revizor verifică fidelitatea cu sursa.
Un fapt nou, o omisiune materială sau alterarea unui citat respinge cazul.

Pe registru, raportează numărul cazurilor, fidelitatea, voturile și egalitățile.
Un evaluator numără aparițiile ID-urilor înainte și după. Reducerea tiparelor
este (înainte − după) / înainte, cu numitor pozitiv. Perplexitatea și variația
lungimii propozițiilor sunt diagnostice exploratorii. Rezultatele detectorilor
se raportează separat, cu model fix și controale umane.

Stare: șase perechi. Evaluarea umană și rularea pe outputuri rămân de făcut.

Pregătirea pachetelor oarbe și agregarea sunt documentate în [benchmark](../benchmark/README.md).
