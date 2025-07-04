# TSP_Branch_and_bound_algoritmus

Tento repozitář obsahuje jednoduchý Python program, který byl vytvořen v rámci bakalářské práce pro výpočet nejkratší možné okružní dopravní trasy pomocí metody **Branch and bound** (metoda větví a mezí). Tento problém se označuje též jako problém obchodního cestujícího nebo *Travelling salesman problem (TSP)*.

## Návod, jak program použít:
- **Vstupní matice** musí být v Excelovém vstupním souboru umístěna úplně vlevo nahoře.
- **Excelový soubor** se vstupní maticí se pro správnou funkčnost musí jmenovat `input.xlsx` (název lze změnit v kódu).
- **Excel s výstupem** se vygeneruje automaticky a pojmenuje se jako `output_metoda_branch_and_bound.xlsx`.
- Ve vstupní matici se počítá s tím, že každý vrchol je pojmenovaný (lze pojmenovat i fiktivním názvem).
- **Umístění souboru:** Vstupní Excelový soubor s maticí vzdáleností musí být ve stejném adresáři jako tento Python program.
- Ve vstupní matici musí být nastaveny extrémně nevýhodné (vysoké, klidně o několik řádů vyšší než je nejvyšší hodnota v matici) sazby pro shodné dvojice míst, aby bylo zajištěno, že si je program nezvolí.
- **Spuštění:** Program lze spustit v libovolném IDE, kde se musí kliknout na spustit soubor.
- **Závislosti:** Je nutné mít nainstalované Python knihovny, které jsou využité v programu – `Pandas` pro manipulaci s daty ve formátu MS Excel a `PuLP` pro zajištění průběhu lineárního programování v algoritmu.

Do budoucna by velice zlepšilo uživatelskou přívětivost vytvoření grafického rozhraní pro tuto aplikaci, aby umožňovala snazší používání pro všechny, kteří budou chtít řešit okružní dopravní problém nebo v rámci studia ekonomicko-matematických metod, lineárního programování či operační analýzy potřebují vyřešit obdobný typ úloh.

Plné znění bakalářské práce včetně příloh a popis konkrétní aplikace této metody je k dispozici [zde](https://is.czu.cz/zp/index.pl?podrobnosti_zp=337864;zpet=;prehled=vyhledavani;vzorek_zp=fric;kde=nazev;kde=autor;kde=klic_slova;filtr_stav=bez;zobrazit=Zobrazit;typ=1;typ=2;typ=3;typ=101;typ=8;typ=7;fakulta=20;fakulta=41;fakulta=40;fakulta=71;fakulta=50;fakulta=73;fakulta=72;fakulta=10;fakulta=30;obhajoba=2024;obhajoba=2023;obhajoba=2022;jazyk=1;jazyk=3;jazyk=2;jazyk=-1).

Program je rovněž pod opensource licencí MIT, tudíž s ním může každý volně nakládat, modifikovat, kopírovat a využívat. **Tím se otevírá možnost, že každý může přispět k vylepšení, vytvoření grafického prostředí, rozšíření a úpravy této aplikace.**
