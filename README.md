# Moja Filmoteka

Desktop aplikacija za vođenje lične kolekcije filmova, napisana u Python-u sa grafičkim korisničkim interfejsom (Tkinter) i CSV fajlom kao bazom podataka. Aplikacija podržava sve četiri osnovne CRUD operacije: **dodavanje, čitanje, ažuriranje i brisanje** filmova.

---

## Sadržaj

1. [Opis aplikacije](#opis-aplikacije)
2. [Funkcionalnosti](#funkcionalnosti)
3. [Tehnologije](#tehnologije)
4. [Pokretanje](#pokretanje)
5. [Struktura projekta](#struktura-projekta)
6. [Koraci izrade aplikacije](#koraci-izrade-aplikacije)
7. [Dobre prakse korišćene u projektu](#dobre-prakse-korišćene-u-projektu)
8. [GitHub repozitorijum](#github-repozitorijum)

---

## Opis aplikacije

Aplikacija **Filmoteka** omogućava korisniku da na jednostavan način vodi evidenciju o filmovima koje je gledao ili planira gledati. Za svaki film se bilježe sljedeći podaci:

- **Naziv filma**
- **Žanr**
- **Godina izdanja**
- **Ocjena** (1–10, prikazana zvjezdicama)

Svi unosi se trajno čuvaju u CSV fajlu `filmovi.csv`, tako da podaci ostaju sačuvani i nakon zatvaranja aplikacije.

---

## Funkcionalnosti

| Operacija | Opis |
|-----------|------|
| **Dodavanje** | Unos novog filma kroz formu na vrhu prozora |
| **Prikaz (čitanje)** | Tabelarni pregled svih filmova iz CSV fajla |
| **Ažuriranje** | Izmjena postojećeg filma kroz poseban *popup* prozor |
| **Brisanje** | Brisanje odabranog filma uz potvrdu korisnika (ili tipkom `Delete`) |
| **Validacija unosa** | Provjera obaveznih polja, tipova podataka i opsega ocjene |
| **Vizuelni prikaz ocjene** | Precizno crtanje popunjenih zvjezdica pomoću `Canvas` elementa |

---

## Tehnologije

- **Python 3** — programski jezik
- **Tkinter / ttk** — GUI biblioteka (standardna u Python-u)
- **csv** — modul za rad sa CSV fajlovima
- **os**, **math** — pomoćni standardni moduli

Grafički interfejs je u potpunosti izgrađen pomoću **`grid`** menadžera za raspored elemenata, u skladu sa zahtjevom zadatka.

---

## Pokretanje

### Preduslovi
- Instaliran Python 3.8 ili noviji

### Koraci

```bash
# 1. Kloniraj repozitorijum
git clone <link-do-repozitorijuma>
cd filmoteka

# 2. Pokreni aplikaciju
python main.py
```

Aplikacija ne zahtijeva dodatne biblioteke — koristi isključivo module iz standardne Python distribucije.

---

## Struktura projekta

```
filmoteka/
├── main.py          # Glavna aplikacija (Filmoteka)
├── filmovi.csv      # CSV baza filmova (automatski se kreira)
├── README.md        # Ovaj izvještaj
└── .gitignore
```

### Glavne klase i funkcije u `main.py`

| Element | Uloga |
|---------|-------|
| `StarRating` | Canvas widget koji precizno crta popunjene zvjezdice (podržava i djelimične ocjene, npr. 7.5) |
| `FilmTable` | Custom scroll-abilna tabela za prikaz filmova |
| `RoundedEntry` | Zaobljeno polje za unos teksta |
| `RoundedButton` | Zaobljeno dugme sa hover efektom |
| `Filmoteka` | Glavna klasa aplikacije (GUI + CRUD logika) |
| `_load_csv` / `_save_csv` | Učitavanje i snimanje podataka iz/u CSV |
| `dodaj_film` / `izmijeni_film` / `obrisi_film` | CRUD operacije |

---

## Koraci izrade aplikacije

### 1. Analiza zahtjeva
Prvi korak bio je detaljno razumijevanje zadatka:
- aplikacija u Python-u sa **Tkinter GUI-jem**,
- **CSV** kao baza podataka,
- podrška za sve **CRUD** operacije,
- obavezno korišćenje **grid** rasporeda,
- primjena dobrih praksi sa kursa (čist kod, razdvajanje odgovornosti, validacija).

### 2. Dizajn modela podataka
Definisan je jednostavan model reda u CSV-u:
```
naziv, zanr, godina, ocjena
```
CSV fajl sadrži header u prvom redu, a svi ostali redovi predstavljaju filmove.

### 3. Izrada osnovnog GUI-ja
Napravljen je osnovni prozor sa **grid** rasporedom:
- **Header** — naslov aplikacije
- **Forma za unos** — polja za naziv, žanr, godinu i ocjenu + dugme *„+ Dodaj film"*
- **Tabela** — prikaz svih filmova sa zaglavljem i scroll-om
- **Dugmad na dnu** — *„Uredi odabrani"* i *„Obriši odabrani"*

Svi elementi su raspoređeni pomoću `grid()` sa `columnconfigure` i `rowconfigure` kako bi se postiglo prilagodljivo skaliranje prozora.

### 4. Implementacija CSV perzistencije
Implementirane su dvije ključne metode:
- **`_load_csv()`** — učitava podatke prilikom pokretanja aplikacije; preskače header, validira da svaki red ima tačno 4 kolone i gracefully rukuje greškama.
- **`_save_csv()`** — automatski se poziva nakon svake izmjene (dodavanja, ažuriranja, brisanja), čime se obezbjeđuje konzistentnost podataka.

### 5. CRUD operacije
- **Create** — `dodaj_film()` čita vrijednosti iz polja, validira ih i dodaje novi film u listu.
- **Read** — `_refresh_table()` prikazuje sadržaj liste `self.filmovi` u tabeli.
- **Update** — `izmijeni_film()` otvara *popup* prozor u kome korisnik mijenja podatke postojećeg filma.
- **Delete** — `obrisi_film()` briše film uz potvrdu korisnika (dialog "Da/Ne"); dostupan i preko tastera `Delete`.

### 6. Validacija korisničkog unosa
Zajednička metoda `_validate()` provjerava:
- da li su sva polja popunjena,
- da je **godina** cijeli broj,
- da je **ocjena** realan broj u opsegu **1–10**.

U slučaju greške prikazuje se `messagebox` sa jasnim opisom problema.

### 7. Napredni vizuelni elementi
Kako bi aplikacija bila vizuelno privlačnija, dodatno su implementirani:
- **StarRating** — prilagođeni widget koji precizno crta popunjene zvjezdice (uključujući i djelimično popunjene koristeći **Sutherland-Hodgman** algoritam za clipping poligona).
- **Zaobljena polja i dugmad** (`RoundedEntry`, `RoundedButton`) — crtana kombinacijom `create_arc` i `create_rectangle` metoda na `Canvas` platnu.
- **Tamna paleta boja** i alterniranje boja redova u tabeli radi bolje čitljivosti.

### 8. Interaktivnost tabele
- Klikom na red, red se vizuelno obilježava (teal boja).
- Dupli klik na red, kao i odabir + dugme *„Uredi odabrani"*, otvaraju *popup* za ažuriranje.
- Taster `Delete` briše odabrani red.
- `MouseWheel` omogućava scroll kroz listu.

### 9. Testiranje
Aplikacija je testirana manuelno kroz sve CRUD scenarije:
- dodavanje filma (valjan i nevaljan unos),
- izmjena postojećeg filma,
- brisanje uz potvrdu i uz taster `Delete`,
- ponovno učitavanje iz CSV-a poslije restarta.

### 10. Objavljivanje na GitHub-u
Na kraju, projekat je postavljen na javni GitHub repozitorijum (vidi sekciju ispod).

---

## Dobre prakse korišćene u projektu

✅ **Razdvajanje odgovornosti** — UI komponente (`StarRating`, `FilmTable`, `RoundedEntry`, `RoundedButton`) su izdvojene u posebne klase, a glavna logika je u klasi `Filmoteka`.

✅ **Enkapsulacija** — interne metode su prefiksirane sa `_` (npr. `_load_csv`, `_validate`, `_refresh_table`).

✅ **Grid raspored** — svi widgeti su raspoređeni pomoću `grid()`, uz `columnconfigure`/`rowconfigure` za responzivnost.

✅ **Centralizovana validacija** — jedinstvena `_validate()` metoda se koristi i za dodavanje i za izmjenu filma.

✅ **Bezbjedan rad sa fajlovima** — korišćenje `with open(...)` bloka, UTF-8 kodiranja i `try/except` obrade grešaka.

✅ **Konstante na vrhu fajla** — sve boje i putanje (`BG_DARK`, `TEAL`, `CSV_PATH`) su definisane kao konstante radi lakšeg održavanja.

✅ **Korisnički orijentisane poruke** — greške i potvrde se prikazuju kroz `messagebox` na maternjem jeziku korisnika.

✅ **Keyboard shortcuts** — podržan taster `Delete` za brzo brisanje.

✅ **Automatsko snimanje** — svaka promjena se odmah upisuje u CSV, nema rizika od gubitka podataka.

✅ **Parametrizovano crtanje zvjezdica** — koristi se matematički pristup (trigonometrija + algoritam za clipping) umjesto slika, što garantuje da izgled ostaje isti na svim rezolucijama.

---

## GitHub repozitorijum

🔗 **Link do repozitorijuma:** `https://github.com/<vase-ime>/filmoteka`

> Napomena: Prije predaje, zamijeniti link sa stvarnim URL-om javnog GitHub repozitorijuma.

### Kako postaviti projekat na GitHub (ukratko)

```bash
# Inicijalizacija i prvi commit
git init
git add .
git commit -m "Inicijalna verzija Filmoteke"

# Povezivanje sa remote repozitorijumom
git branch -M main
git remote add origin https://github.com/<vase-ime>/filmoteka.git
git push -u origin main
```

Detaljan kratki kurs za GitHub dostupan je u materijalima sa kursa.

---

## Autor

Izradio: **Petar Simonović**
Predmet: **Algoritmi i strukture podataka**
Godina: **2026.**