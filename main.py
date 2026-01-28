
"""
Správce úkolů s využitím MySQL databáze. Vylepšený Task manager
author: Květoslav Leidorf
email: k.leidorf@gmail.com
discord: kvetos_95684
"""

import sys
import mysql.connector
from mysql.connector import Error


def pripojeni_db():
    """
    Vytvoří připojení k MySQL serveru a zajistí existenci databáze.
    Vrací objekt připojení nebo None při neúspěchu.
    """
    try:
        # Připojení k serveru (host, user a password upravte dle svého prostředí)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='VASEHESLO'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            # Automatická příprava prostředí
            cursor.execute("CREATE DATABASE IF NOT EXISTS manager_ukolu")
            cursor.execute("USE manager_ukolu")
            return connection
            
    except Error as e:
        print(f"Chyba při připojování k databázi: {e}")
        return None


def vytvoreni_tabulky(connection):
    """Vytvoří tabulku ukoly, pokud v databázi ještě neexistuje."""
    try:
        cursor = connection.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT NOT NULL,
            stav ENUM('nezahájeno', 'probíhá', 'hotovo') DEFAULT 'nezahájeno',
            datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")


def hlavni_menu() -> str:
    """Zobrazí hlavní menu a vrátí validovanou volbu uživatele."""
    while True:
        print(
            "\n" + "-" * 27,
            "Správce úkolů - MySQL Menu",
            "1. Přidat nový úkol",
            "2. Zobrazit úkoly (aktivní)",
            "3. Aktualizovat stav úkolu",
            "4. Odstranit úkol",
            "5. Ukončit program",
            "-" * 27,
            sep="\n"
        )
        
        volba = input("Vyberte možnost (1-5): ").strip()
        
        if volba in ("1", "2", "3", "4", "5"):
            return volba
            
        print("Neplatná volba, zkuste to prosím znovu.")


def pridat_ukol(connection) -> None:
    """Umožní uživateli zadat data a uloží nový úkol do MySQL."""
    while True:
        nazev = input("\nZadejte název úkolu: ").strip()
        popis = input("Zadejte popis úkolu: ").strip()
        
        if not nazev or not popis:
            print("Chyba: Název i popis úkolu jsou povinné! Zadejte znovu.")
            continue

        try:
            cursor = connection.cursor()
            query = "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, 'nezahájeno')"
            cursor.execute(query, (nazev, popis))
            connection.commit()
            print(f"Úkol '{nazev}' byl úspěšně uložen do databáze.")
            break
        except Error as e:
            print(f"Chyba při ukládání: {e}")
            break


def zobrazit_ukoly(connection, jen_aktivni=True) -> bool:
    """
    Vypíše úkoly z DB.
    Vrací True, pokud existují nějaké záznamy, jinak False.
    """
    try:
        cursor = connection.cursor()
        if jen_aktivni:
            query = "SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ('nezahájeno', 'probíhá')"
        else:
            query = "SELECT id, nazev, popis, stav FROM ukoly"
            
        cursor.execute(query)
        vysledky = cursor.fetchall()

        if not vysledky:
            print("\nSeznam úkolů v databázi je prázdný.")
            return False

        print("\nAktuální seznam úkolů:")
        for radek in vysledky:
            print(f"ID: {radek[0]} | Název: {radek[1]} | Stav: {radek[3]}")
            print(f"   Popis: {radek[2]}")
        return True
        
    except Error as e:
        print(f"Chyba při načítání dat: {e}")
        return False


def aktualizovat_ukol(connection) -> None:
    """Změní stav existujícího úkolu. Obsahuje validaci ID."""
    if not zobrazit_ukoly(connection, jen_aktivni=False):
        return

    while True:
        vstup_id = input("\nZadejte ID úkolu pro aktualizaci (nebo 'q' pro zrušení): ").strip()
        
        if vstup_id.lower() == 'q':
            break

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM ukoly WHERE id = %s", (vstup_id,))
            
            if not cursor.fetchone():
                print(f"Chyba: Úkol s ID {vstup_id} neexistuje.")
                continue

            print("Vyberte nový stav: 1. Probíhá, 2. Hotovo")
            volba_stavu = input("Volba: ").strip()
            
            novy_stav = "probíhá" if volba_stavu == "1" else "hotovo" if volba_stavu == "2" else None

            if novy_stav:
                cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, vstup_id))
                connection.commit()
                print(f"Úkol ID {vstup_id} byl úspěšně aktualizován na: {novy_stav}")
                break
            
            print("Neplatná volba stavu, zkuste to znovu.")
            
        except (Error, ValueError):
            print("Chyba: Zadejte platné číselné ID.")


def odstranit_ukol(connection) -> None:
    """Trvale odstraní úkol z DB na základě validovaného ID."""
    if not zobrazit_ukoly(connection, jen_aktivni=False):
        return

    while True:
        vstup_id = input("\nZadejte ID úkolu k odstranění (nebo 'q' pro zrušení): ").strip()
        
        if vstup_id.lower() == 'q':
            break

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM ukoly WHERE id = %s", (vstup_id,))
            
            if not cursor.fetchone():
                print(f"Chyba: Úkol s ID {vstup_id} neexistuje.")
                continue

            cursor.execute("DELETE FROM ukoly WHERE id = %s", (vstup_id,))
            connection.commit()
            print(f"Úkol ID {vstup_id} byl úspěšně odstraněn z databáze.")
            break
            
        except Error as e:
            print(f"Chyba při odstraňování: {e}")
            break


def spusti_program() -> None:
    """Hlavní řídicí smyčka programu."""
    db_conn = pripojeni_db()
    
    if not db_conn:
        print("Kritická chyba: Program nelze spustit bez připojení k MySQL.")
        return

    vytvoreni_tabulky(db_conn)

    while True:
        volba = hlavni_menu()
        
        if volba == "1":
            pridat_ukol(db_conn)
        elif volba == "2":
            zobrazit_ukoly(db_conn)
        elif volba == "3":
            aktualizovat_ukol(db_conn)
        elif volba == "4":
            odstranit_ukol(db_conn)
        elif volba == "5":
            print("\nUkončuji program. Odpojuji se od databáze.")
            if db_conn.is_connected():
                db_conn.close()
            sys.exit(0)


if __name__ == "__main__":
    spusti_program()
