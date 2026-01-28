# Projekt 5: Vylepšený Task Manager s MySQL

Tento projekt představuje pokročilou verzi správce úkolů, který místo dočasné paměti využívá k ukládání dat **MySQL databázi**. Projekt je rozdělen na funkční aplikaci (CRUD operace) a sadu automatizovaných testů.

---

## 🚀 Část 1: Funkce aplikace
Program umožňuje plnohodnotnou správu úkolů v reálném čase:
* **Create (Vytvoření):** Přidání úkolu s povinným názvem a popisem.
* **Read (Čtení):** Zobrazení aktivních úkolů (filtrování stavů "nezahájeno" a "probíhá").
* **Update (Aktualizace):** Změna stavu úkolu na základě jeho unikátního ID.
* **Delete (Odstranění):** Trvalé smazání úkolu z databáze.

**Struktura databáze:**
Tabulka `ukoly` obsahuje pole: `id`, `nazev`, `popis`, `stav` (enum) a `datum_vytvoreni`.

---

## 🧪 Část 2: Automatizované testování
Kvalita kódu je ověřena pomocí frameworku **pytest**. Testy pracují s izolovanou testovací databází, která se po dokončení testů automaticky smaže.

**Rozsah testování (6 scénářů):**
1. **Přidání úkolu:** Pozitivní (validní data) a Negativní (prázdné vstupy).
2. **Aktualizace úkolu:** Pozitivní (existující ID) a Negativní (neexistující ID).
3. **Odstranění úkolu:** Pozitivní (smazání záznamu) a Negativní (neexistující ID).

---

## 🛠️ Instalace a spuštění (PowerShell)

### 1. Klonování a příprava
Ujistěte se, že máte nainstalovaný **MySQL Server** a **Python 3.10+**.

### 2. Instalace závislostí
V terminálu `pwsh.exe` ve složce projektu spusťte:
```powershell
pip install mysql-connector-python pytest
```

### 3. Konfigurace
V souborech `main.py` a `test_main.py` upravte proměnnou `password` ve funkci `pripojeni_db` (resp. fixture `db_conn`) dle vašeho místního nastavení MySQL.

### 4. Spuštění programu
V terminálu `pwsh.exe` spusťte aplikaci příkazem:
```powershell
python main.py
```

### 5. Spuštění testů
Pro ověření funkčnosti pomocí pytestu spusťte v `pwsh.exe`:
```powershell
pytest test_main.py
```

---

## 📁 Struktura projektu
* **`main.py`** – Hlavní kód aplikace s logikou CRUD a připojením k DB.
* **`test_main.py`** – Automatizované testy využívající mockování vstupů.
* **`README.md`** – Tato dokumentace.

---

**Autor:** Květoslav Leidorf  
**Email:** k.leidorf@gmail.com
