<div align="center">

# 🪶 Omenizator

**Humanizer de text în limba moldovenească · lexic inactiv**

Curăță tiparele de scriere AI și ajustează ritmul. Inventarul lexical rămâne inactiv până la aprobarea independentă pe sens.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](CHANGELOG.md)
[![Lexicon](https://img.shields.io/badge/inventar-154%20r%C3%A2nduri-orange.svg)](references/lexicon-subset.md)
[![Skill](https://img.shields.io/badge/type-Agent%20Skill-purple.svg)](SKILL.md)

**Zero forțare** · **Audit obligatoriu**

</div>

---

## Ce face

Primește un text care „miroase a AI” și îl întoarce uman: fără fluff, cu subiect explicit, cu atenție la ritm și registru.

| Înainte (AI) | După (omenizat) |
|---|---|
| „Este important de menționat că soluția oferă o serie de beneficii.” | „Soluția are mai multe avantaje.” |
| „În cadrul acestui proces vom proceda la analiza…” | „Vom analiza…” |

**Inventar:** Master Index v3.1.0 are 154 de rânduri. Zero perechi termen–sens sunt aprobate pentru substituție. **BREAKING în 2.0.0:** substituțiile cer aprobarea independentă și potrivire de registru.

---

## Instalare

Suport oficial: Claude Code. Alți agenți rămân netestați. Dacă `~/.claude/skills/omenizator` există deja, mută-l întâi. Vezi [documentația despre skills](https://code.claude.com/docs/en/skills).

```bash
git clone --branch v2.1.0 https://github.com/icsaoc/humanizatoreal.git "$HOME/.claude/skills/omenizator"
```

## Utilizare

```bash
/omenizator                 # mod literar implicit
```

Dacă ceri `stil=admin`, skill-ul explică indisponibilitatea stratului înainte de a oferi curățarea de bază. Pentru a reproduce evaluarea, vezi [rularea benchmarkului](benchmark/README.md). Consultă [proveniența lexicală](references/provenienta-lexicala.md), [corpusul de control](references/corpus-contemporan.md) și [benchmarkul pilot](references/evaluare.md).

**Procedură fixă:**  
1. Citește textul (+ mostră de glas, dacă există)  
2. Detectează tiparele AI (29 semne)  
3. Rescrie păstrând sensul și registrul
4. Livrează **tabel de audit obligatoriu**

---

## Moduri

| Mod | Comportament actual | Intrări lexicale eligibile |
|---|---|---|
| Literar implicit sau istoric la cerere | Curățarea tiparelor și ritm adaptat | 0 |
| Stradal (`--argou`) | Inactiv. Compilație de internet fără intrări aprobate | 0 |
| Administrativ (`stil=admin`) | Inactiv. Anunță indisponibilitatea înainte de a oferi curățarea de bază | 0 reformulări administrative active |

**Densitate lexicală:** max. ~1 termen MD la 150 cuvinte.  
Pragul se aplică după activarea unei perechi. În starea actuală nu se aplică substituții.

---

## Structura repo-ului

```
humanizatoreal/
├─ SKILL.md                 # procedura + YAML frontmatter (v2.1.0)
├─ README.md
├─ LICENSE · NOTICE · AUTHORS · CITATION.cff
├─ CHANGELOG.md · CONTRIBUTING.md
├─ .github/workflows/check.yml
├─ scripts/
│  └─ check_release.py      # poarta de coerență înainte de release
├─ benchmark/               # pregătire și scor A/B
│  ├─ README.md
│  ├─ evaluate.py
│  └─ perechi-sens.md       # regresie pentru modalitate
├─ tests/
│  ├─ test_evaluate.py
│  └─ test_check_release.py
├─ references/
│  ├─ tipare.md             # 29 tipare AI
│  ├─ lexicon-subset.md     # Master Index v3.1.0 (canonic)
│  ├─ glosar-dmr.md         # pointer → lexicon-subset.md
│  ├─ argou-chisinau.md     # inventar stradal inactiv
│  ├─ corpus-glas.md        # mostre de ritm (Neculce / Creangă)
│  ├─ admin-stil.md
│  ├─ provenienta-lexicala.md
│  ├─ corpus-contemporan.md
│  ├─ evaluare.md
│  └─ surse.md
└─ examples/
   ├─ exemplu-dmr.md
   ├─ exemplu-administrativ.md
   └─ exemplu-tehnic.md
```

---

## Referințe rapide

- [Tipare AI (1–29)](references/tipare.md)
- [Lexicon DMR (RO → MD)](references/lexicon-subset.md)
- [Corpus de glas](references/corpus-glas.md) · [Surse](references/surse.md)
- [Changelog](CHANGELOG.md)

---

## Autor & originalitate

**Omenizator** este un concept original al **XAOC** (2026) — humanizer moldovenesc care elimină tiparele AI și păstrează lexicul DMR / Vasile Stati ca inventar inactiv.

- Autor: **XAOC** · iam@xaoc.bio  
- Repo: https://github.com/icsaoc/humanizatoreal

Dacă folosești sau construiești pe această idee, citează-o (vezi [CITATION.cff](CITATION.cff)).

---

## Licențiere

| Componentă | Licență |
|---|---|
| Cod & logică (`SKILL.md`) | [MIT](LICENSE) |
| Date de referință & documentație (`references/`, README) | CC BY-SA 4.0 pentru contribuțiile proprii, inclusiv uz comercial în condițiile licenței |
| Surse lexicale terțe (Stati etc.) | Drepturile rămân ale autorilor originali — vezi [surse.md](references/surse.md) |

---

<div align="center">

**Fă textul să sune a om, nu a model.**

</div>
