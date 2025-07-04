
# TSP_Branch_and_bound_algoritmus

Tento repozitář obsahuje jednoduchý Python program, který byl vytvořen v rámci bakalářské práce pro výpočet nejkratší možné okružní dopravní trasy pomocí metody Branch and Bound (metoda větví a mezí). Tento problém se označuje též jako problém obchodního cestujícího nebo Travelling salesman problem (TSP).

## Teoretické základy a implementační metodologie

### Problém obchodního cestujícího (TSP)

Problém obchodního cestujícího patří mezi klasické optimalizační úlohy, které se řadí do kategorie NP-úplných problémů. Jeho podstatou je nalezení nejkratší možné trasy, která prochází všemi zadanými body právě jednou a vrací se do výchozího bodu. V teorii grafů je tento problém reprezentován jako hledání minimální Hamiltonovské kružnice v úplném grafu, kde vrcholy představují navštěvovaná místa a hrany reprezentují cesty mezi nimi ohodnocené vzdáleností.

### Metoda větví a mezí (Branch and Bound)

Implementovaný algoritmus využívá metodu větví a mezí, která systematicky prohledává prostor všech možných řešení. Princip metody spočívá v:

- Rozdělení problému na podproblémy (větvení)
- Výpočtu dolní meze pro každý podproblém
- Postupném vyřazování podproblémů, které nemohou vést k optimálnímu řešení

Matematická formulace implementovaného modelu využívá celočíselné lineární programování s následující účelovou funkcí:

$$
\min \sum_{i=1}^{n} \sum_{j=1}^{n} c_{ij}\, x_{ij}
$$

kde:
- $$c_{ij}$$ jsou vzdálenosti mezi místy
- $$x_{ij}$$ jsou binární proměnné (1 pokud je hrana použita)

Při dodržení omezujících podmínek:
- Každý uzel je navštíven právě jednou
- Z každého uzlu vede právě jedna cesta
- Není přípustné vytvoření dílčích podcyklů

## Zdůvodnění implementačního přístupu

Pro implementaci byl zvolen jazyk Python s knihovnou PuLP, která poskytuje rozhraní pro řešení problémů lineárního programování. Tento přístup byl vybrán z následujících důvodů:

- Možnost efektivního řešení i pro rozsáhlejší instance problému
- Eliminace problému s přetečením algoritmu, který se vyskytuje u jiných implementací
- Využití moderních algoritmů pro řešení celočíselného lineárního programování
- Snadná integrace s dalšími nástroji pro zpracování dat (pandas, Excel)

Implementace programu je koncipována jako modulární systém funkcí, který zajišťuje:

- Načtení vstupních dat z matice vzdáleností
- Formulaci a řešení matematického modelu
- Identifikaci a vyhodnocení alternativních řešení
- Prezentaci výsledků v přehledné formě

## Návod k použití

### Požadavky na vstupní soubor

- Vstupní matice musí být v Excelovém vstupním souboru umístěna úplně vlevo nahoře.
- Ve vstupní matici se počítá s tím, že každý vrchol je pojmenovaný (lze pojmenovat i fiktivním názvem).
- Ve vstupní matici musí být nastaveny extrémně nevýhodné (vysoké) sazby pro shodné dvojice míst, aby bylo zajištěno, že si je program nezvolí.

  **Příklad:** hodnoty na diagonále matice by měly být řádově vyšší než ostatní hodnoty.

### Názvy souborů a umístění

- **Vstupní soubor:** `input.xlsx` (název lze změnit v kódu)
- **Výstupní soubor:** `output_metoda_branch_and_bound.xlsx` (generuje se automaticky)
- **Umístění souborů:** Vstupní Excelový soubor musí být ve stejném adresáři jako Python program

### Výstupní soubor

Program vygeneruje Excel s následujícími listy:

- **Matice_optimum** – výsledná matice s tučně zvýrazněnými vybranými trasami
- **Soucet_vzdalenosti** – celková délka optimální trasy
- **Posloupnost_mist** – pořadí míst v optimální trase
- **Alternativni_okruhy** – další nalezené možné okruhy a jejich délky

### Instalace závislostí

Spusťte v příkazovém řádku:

```
pip install pandas pulp openpyxl
```


Poznámka: Knihovny `itertools` a `re` jsou součástí standardní knihovny Pythonu a není nutné je samostatně instalovat.

### Spuštění programu

Program lze spustit v libovolném IDE nebo příkazovém řádku:

```
python TSP_Branch_and_bound_algoritmus.py
```


## Použité knihovny

- **pandas** – manipulace s daty ve formátu MS Excel
- **pulp** – implementace lineárního programování v algoritmu
- **openpyxl** – práce s Excel soubory (používá pandas)
- **itertools.permutations** – standardní knihovna pro práci s permutacemi
- **re** – standardní knihovna pro práci s regulárními výrazy

## Popis funkcí programu

- `read_excel(filename)` – načte vstupní matici z Excel souboru
- `solve_tsp(matrix)` – implementace algoritmu větví a mezí pro řešení TSP
- `find_cycles(matrix, solution)` – identifikuje alternativní okruhy v řešení
- `write_excel(matrix, solution, cycles, filename)` – generuje výstupní Excel soubor
- `main(input_file, output_file)` – hlavní řídící funkce programu

## Budoucí vývoj

Do budoucna by velice zlepšilo uživatelskou přívětivost vytvoření grafického rozhraní pro tuto aplikaci, aby umožňovala snazší používání pro všechny, kteří budou chtít řešit okružní dopravní problém nebo v rámci studia ekonomicko-matematických metod, lineárního programování či operační analýzy potřebují vyřešit obdobný typ úloh.

## Licence

Program je pod opensource licencí MIT, tudíž s ním může každý volně nakládat, modifikovat, kopírovat a využívat. Tím se otevírá možnost, že každý může přispět k vylepšení, vytvoření grafického prostředí, rozšíření a úpravy této aplikace.

Vytvořeno v rámci bakalářské práce na téma řešení problému obchodního cestujícího pomocí metody větví a mezí.

---

Plné znění bakalářské práce včetně příloh a popis konkrétní aplikace této metody je k dispozici [zde](https://is.czu.cz/zp/index.pl?podrobnosti_zp=337864;zpet=;prehled=vyhledavani;vzorek_zp=fric;kde=nazev;kde=autor;kde=klic_slova;filtr_stav=bez;zobrazit=Zobrazit;typ=1;typ=2;typ=3;typ=101;typ=8;typ=7;fakulta=20;fakulta=41;fakulta=40;fakulta=71;fakulta=50;fakulta=73;fakulta=72;fakulta=10;fakulta=30;obhajoba=2024;obhajoba=2023;obhajoba=2022;jazyk=1;jazyk=3;jazyk=2;jazyk=-1).
