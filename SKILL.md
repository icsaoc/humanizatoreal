---
name: omenizator
description: >-
  Humanizer moldovenesc cu lexic inactiv. Curăță tiparele de scriere AI.
  Folosește când utilizatorul cere omenizarea textului sau un ton moldovenesc;
  livrează curățare stilistică de bază, fără adaptare regională validată.
  Opțiunile --argou și stil=admin sunt inactive.
license: MIT
version: 2.0.0
author: XAOC
contact: iam@xaoc.bio
repository: https://github.com/icsaoc/humanizatoreal
created: 2026
---

# Omenizator — Humanizer Moldovenesc

**Procedura obligatorie:**

1. **Citește textul de input.** Dacă utilizatorul oferă o mostră de scris, folosește-o ca reper de stil. Altfel, lucrează cu textul primit. Referințele contemporane documentează un singur termen.
2. **Detectează tiparele de scriere AI** (`references/tipare.md`, 29 semne) — numerotează fiecare tipar găsit.
3. **Rescrie:**
   - elimină tiparele găsite; transformă construcțiile pasive/vagi în active cu subiect explicit („cine face acțiunea?").
   - **Substituții lexicale (niciuna activă în 2.0.0):** după aprobarea independentă pe sens, caută **declanșatoarele RO comune** din `references/lexicon-subset.md` (Master Index v3.1.0). Aplică filtrul de dovezi din `references/provenienta-lexicala.md`. Dacă ID-ul este activ în registru și există potrivire naturală de sens și registru → înlocuiește cu termenul md — **doar** respectând Pragul de densitate de mai jos.
   - dacă **niciun** declanșator nu se potrivește → **nu inventa** termeni DMR și **nu forța** cei existenți pe sensuri nepotrivite. Continuă doar cu eliminarea tiparelor AI + ritm natural.
   - păstrează sensul original 100% — nu inventa, nu adăuga fapte noi, nu exagera.
   - ton: direct, concis, fără fluff, fără hedging.
   - ritm natural: propoziții de lungimi variate.
4. **Aplică modul** — vezi Moduri mai jos.
5. **Verifică și livrează obligatoriu tabelul de audit**.

**Reguli dure (nu le încălca niciodată):**
- Păstrează sensul intact.
- Nu inventa surse, cifre sau citate.
- Nu atinge nume proprii, citate exacte, cod, unități de măsură sau terminologie tehnică fixă.
- Nu adăuga emoji, bold mecanic, liste simetrice forțate.
- Nu încheia cu „Succes!", „Sper că te ajută" sau platitudini.
- Dacă textul nu are tipare AI detectabile, nu forța rescrierea — raportează „zero tipare găsite" și lasă textul neatins.

## Prag de densitate (după activarea unei perechi)
- Pragul se aplică doar după activarea independentă a unei perechi. În 2.0.0 nu se aplică substituții.
- Prag orientativ: max. 1 termen DMR la ~150 cuvinte de output.
- Dacă niciun termen din `lexicon-subset.md` nu are potrivire naturală, nu injecta nimic — rezultat valid.

## Livrabil obligatoriu
La finalul fiecărei rescrieri, output-ul include un tabel de audit:

| # tipar (versiune catalog) | remediu aplicat | termen / reformulare și ID dovadă (dacă există) |
|---|---|---|

- Dacă zero tipare și zero lexic: „text deja curat, neatins".
- Tabelul nu e opțional.

## Moduri
- **Literar** (implicit): curățarea tiparelor și ajustarea ritmului. Zero intrări lexicale active, inclusiv pentru registrul literar istoric.
- **Stradal** (`--argou`): opțiune inactivă. Inventarul are zero intrări aprobate. Dacă utilizatorul o cere, explică indisponibilitatea înainte de a oferi curățarea stilistică de bază.
- **Administrativ** (`stil=admin`): opțiune inactivă. Dacă utilizatorul o cere, explică indisponibilitatea înainte de a oferi curățarea stilistică de bază.

## Referințe (încărcare la cerere)
- tipare → `read_file references/tipare.md`
- lexicon DMR (Master Index v3.1.0) → `read_file references/lexicon-subset.md`
- inventar administrativ (inactiv) → `read_file references/admin-stil.md`
- inventar stradal (inactiv) → `read_file references/argou-chisinau.md`
- corpus de glas → `read_file references/corpus-glas.md`
- proveniență lexicală → `read_file references/provenienta-lexicala.md`
- corpus contemporan → `read_file references/corpus-contemporan.md`
- protocol de evaluare → `read_file references/evaluare.md`
- surse → `read_file references/surse.md`

## Trigger phrases
- „omenește textul ăsta"
- „/omenizator"
- „elimină semnele de AI din textul următor"
- „stil=admin" / „în stil administrativ moldovenesc"

După rescriere, poți întreba utilizatorul dacă vrea ajustări — tabelul de audit rămâne obligatoriu.
