"""
Unit testy pro Správce úkolů s využitím pytest.
Prověřuje základní CRUD operace nad databází.
"""

import pytest
from unittest.mock import patch
import mysql.connector
from main import vytvoreni_tabulky

# Nastavení testovací databáze (izolované od produkční)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'VASEHESLO',  # Doplňte své heslo pro lokální testy
    'database': 'test_manager_ukolu'
}


@pytest.fixture(scope="module")
def db_conn():
    """
    Fixture pro vytvoření testovací DB a připojení.
    Po skončení testů celou databázi odstraní.
    """
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn.database = DB_CONFIG['database']
    vytvoreni_tabulky(conn)
    
    yield conn
    
    # Úklid po dokončení všech testů v modulu
    cursor.execute(f"DROP DATABASE {DB_CONFIG['database']}")
    conn.close()


@pytest.fixture(autouse=True)
def smazat_data(db_conn):
    """Před každým testem vymaže data v tabulce, aby byly testy izolované."""
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM ukoly")
    db_conn.commit()


# --- TESTY PRO FUNKCI PRIDAT_UKOL ---

def test_pridat_ukol_pozitivni(db_conn):
    """Ověří, že validní úkol je korektně uložen do DB."""
    from main import pridat_ukol
    
    # Simulujeme zadání názvu a popisu
    with patch('builtins.input', side_effect=['Uklidit', 'Vyluxovat obývák']):
        pridat_ukol(db_conn)
    
    cursor = db_conn.cursor()
    cursor.execute("SELECT nazev FROM ukoly WHERE nazev = 'Uklidit'")
    vysledek = cursor.fetchone()
    
    assert vysledek is not None
    assert vysledek[0] == 'Uklidit'


def test_pridat_ukol_negativni(db_conn):
    """
    Ověří, že úkol s prázdným názvem se neuloží.
    Simulujeme: 1. prázdný název, 2. opravu/změnu, která následně projde.
    """
    from main import pridat_ukol
    
    # První pokus prázdný, druhý pokus validní data pro ukončení smyčky
    inputs = ['', '', 'Platný název', 'Platný popis']
    with patch('builtins.input', side_effect=inputs):
        pridat_ukol(db_conn)
    
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ukoly")
    # V tabulce musí být jen ten jeden opravený úkol
    assert cursor.fetchone()[0] == 1


# --- TESTY PRO FUNKCI AKTUALIZOVAT_UKOL ---

def test_aktualizovat_ukol_pozitivni(db_conn):
    """Ověří úspěšnou změnu stavu u existujícího úkolu."""
    from main import aktualizovat_ukol
    
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)",
        ('Test', 'Popis', 'nezahájeno')
    )
    ukol_id = cursor.lastrowid
    db_conn.commit()

    # side_effect: 1. ID úkolu, 2. Volba nového stavu (2 = Hotovo)
    with patch('builtins.input', side_effect=[str(ukol_id), '2']):
        aktualizovat_ukol(db_conn)

    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (ukol_id,))
    assert cursor.fetchone()[0] == 'hotovo'


def test_aktualizovat_ukol_negativni(db_conn):
    """Ověří reakci na neexistující ID a korektní ukončení skrze 'q'."""
    from main import aktualizovat_ukol
    
    # Simulujeme zadání neexistujícího ID a následné zrušení operace klávesou 'q'
    with patch('builtins.input', side_effect=['999', 'q']):
        aktualizovat_ukol(db_conn)
    
    # Test projde, pokud funkce nezpůsobí pád a skončí po 'q'


# --- TESTY PRO FUNKCI ODSTRANIT_UKOL ---

def test_odstranit_ukol_pozitivni(db_conn):
    """Ověří trvalé smazání existujícího úkolu z databáze."""
    from main import odstranit_ukol
    
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES ('Na smazání', 'Popis')")
    ukol_id = cursor.lastrowid
    db_conn.commit()

    with patch('builtins.input', side_effect=[str(ukol_id)]):
        odstranit_ukol(db_conn)

    cursor.execute("SELECT COUNT(*) FROM ukoly WHERE id = %s", (ukol_id,))
    assert cursor.fetchone()[0] == 0


def test_odstranit_ukol_negativni(db_conn):
    """Ověří, že pokus o smazání neexistujícího ID nezmění data v DB."""
    from main import odstranit_ukol
    
    # Neexistující ID a ukončení smyčky
    with patch('builtins.input', side_effect=['888', 'q']):
        odstranit_ukol(db_conn)
        
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ukoly")
    assert cursor.fetchone()[0] == 0
