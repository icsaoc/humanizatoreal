# Rulare benchmark

Necesită Python 3.10+ și un agent cu Omenizator. Folosește o conversație nouă
pentru fiecare caz. Furnizează numai inputul și registrul cerut.
Pentru cazurile administrative, rulează curățarea de bază fără `stil=admin`,
deoarece stratul administrativ este inactiv. Salvează separat
răspunsul complet, inclusiv auditul. Pune numai textul livrat în candidates.

Fișierul run.json are câmpurile model, skill, catalog, parameters și candidates.
Ultimul mapează fiecare ID din references/evaluare.md la textul candidat.
Nu substitui exemplele de referință pentru outputul măsurat.

    python benchmark/evaluate.py prepare run.json review --seed 104
    python benchmark/evaluate.py score review

Distribuie fiecărui evaluator numai fișierul review-N.csv. Cheile și fișierul
fidelity.csv rămân la coordonator. În coloanele naturalness și register_fit
se completează A, B sau tie. Revizorul completează fidelity cu pass sau fail
și numără aparițiile tiparelor înainte și după. Scorul raportează separat
fidelitatea, controalele curate, voturile și reducerea tiparelor. Nu transforma
o rulare pilot într-o afirmație generală despre registru sau despre autorat AI.
Controalele curate nu apar în review-N.csv. Scorul le raportează prin
clean_controls și clean_controls_unchanged. Perechile pentru modalitate sunt în
[perechi-sens.md](perechi-sens.md).

CSV-urile folosesc UTF-8 cu BOM. La salvare în Excel alege CSV UTF-8.
Sunt acceptate virgula și punctul și virgula. Cazurile respinse sunt raportate
separat și sunt excluse din voturile agregate și reducerea tiparelor.

    python -m unittest discover -s tests -v
