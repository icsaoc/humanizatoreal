# Inventar de reformulări administrative — inactiv în 2.0.0

> Nu sunt documentate dovezi de uz pentru reformulările de mai jos. Activarea cere dovezi pe sens și aprobarea unui revizor independent, la același standard ca lexicul.
> La cererea `stil=admin`, explică indisponibilitatea înainte de a oferi curățarea stilistică de bază.

## Reformulări candidate

| declanșator (RO birocratic) | reformulare (MD admin) | notă |
|---|---|---|
| plasarea unei actualizări | punerea în producție / lansarea actualizării | "plasarea" e calchiat |
| funcționalului aferent | funcționalitatea care ține de... / partea care se ocupă de... | "aferent" abuzat |
| vă informăm | vă anunțăm | mai direct, uz MD |
| întru executarea | pentru executarea / ca să executăm | arhaic |
| întru asigurarea | ca să asigurăm / pentru a asigura | arhaic |
| se va purcede la | vom trece la / începem | pasiv inutil |
| se va efectua | vom face / se face | pasiv |
| în vederea | pentru / ca să | fluff AI + birocratic |
| în scopul de a | ca să / pentru a | fluff |
| de către | de — sau subiect explicit | pasiv: "de către bancă" → "banca" |
| aferent / aferentă | care ține de / legat de | evitat |
| derularea / desfășurarea | — (șterge) / organizarea | "derularea procesului" → "procesul" |
| survenirea | apariția | |
| parvenirea | primirea | |
| demers | solicitare / adresare | "demers" abuzat în MD birocratic |
| invocăm | menționăm / spunem | |
| prezenta notificare | notificarea asta / notificarea de față | |
| în contextul | în legătura cu / legat de | |
| cu referire la | referitor la / despre | |
| vizavi de | despre / în legătură cu | rusism birocratic |
| la moment | acum / în prezent | rusism: "на данный момент" |
| de la bun început | din start / de la început | |
| pe parcursul | în timpul / cât | |
| în comun cu | împreună cu | |
| de comun acord | am căzut de acord / am agreat | |
| a fost efectuată actualizarea | am actualizat / am pus în producție | subiect explicit |
| funcționalitate de emitere certificat | emiterea certificatelor / cum se emit certificatele | substantivizare excesivă |

## Exemple istorice ale inventarului inactiv

**Înainte (birocratic + AI):**
> În vederea asigurării funcționalului aferent emiterii certificatelor, se va purcede la plasarea unei actualizări în SIA CCDE.

**După (tehnic-curat + admin MD):**
> Ca să asigure emiterea certificatelor, echipa pune în producție o actualizare în SIA CCDE.

**Înainte:**
> Vă informăm că funcționalitatea aferentă tipului resident_type va fi disponibilă.

**După:**
> Vă anunțăm că partea care ține de resident_type va fi disponibilă.

## Reguli aplicare
1. Activarea cere dovezi și aprobare independentă.
2. Niciodată nu amesteca cu DMR (nu pune `păpușoi` în text despre IBAN)
3. Păstrează termenii tehnici exacți: JSON, IBAN, SIA, CCDE, resident_type, endpoint — nu-i traduce
4. Scurtează propozițiile >22 cuvinte
5. Subiect explicit: cine face ce (echipa, banca, SIA)

## Când NU aplici
- Inventarul rămâne inactiv în 2.0.0, inclusiv la cererea `stil=admin`.
