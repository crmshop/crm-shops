#!/usr/bin/env python3
"""
Script per applicare la migrazione 005: rendere user_id nullable in outfits
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg.conninfo import make_conninfo

# Aggiungi il path del progetto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

def get_db_connection_string():
    """Costruisce la connection string PostgreSQL da Supabase URL"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_db_password = os.getenv("SUPABASE_DB_PASSWORD")
    
    if not supabase_url:
        raise ValueError("SUPABASE_URL non trovata in .env")
    
    # Estrai informazioni dalla URL Supabase
    # Formato: https://xxxxx.supabase.co
    # Il database è su db.xxxxx.supabase.co:5432
    url_parts = supabase_url.replace("https://", "").replace("http://", "").split(".")
    project_ref = url_parts[0]
    
    # Costruisci connection string
    # Nota: per Supabase, usa la connection string diretta se disponibile
    # Altrimenti usa i parametri standard
    db_host = f"db.{project_ref}.supabase.co"
    db_port = 5432
    db_name = "postgres"
    db_user = "postgres"
    
    # Password dal .env o usa quella di default Supabase
    if not supabase_db_password:
        print("⚠️  SUPABASE_DB_PASSWORD non trovata in .env")
        print("   Usa la connection string completa da Supabase Dashboard:")
        print("   Settings > Database > Connection string > URI")
        print("   Aggiungila come SUPABASE_DB_CONNECTION_STRING in .env")
        
        # Prova a usare connection string diretta se disponibile
        db_conn_string = os.getenv("SUPABASE_DB_CONNECTION_STRING")
        if db_conn_string:
            return db_conn_string
        else:
            raise ValueError("Configura SUPABASE_DB_CONNECTION_STRING o SUPABASE_DB_PASSWORD in .env")
    
    conninfo = make_conninfo(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=supabase_db_password
    )
    
    return conninfo

def apply_migration():
    """Applica la migrazione 005"""
    migration_file = Path(__file__).parent / "005_make_outfits_user_id_nullable.sql"
    
    if not migration_file.exists():
        print(f"❌ File migrazione non trovato: {migration_file}")
        sys.exit(1)
    
    print(f"📄 Applicando migrazione: {migration_file.name}")
    
    # Leggi il contenuto SQL
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        # Connetti al database
        print("🔌 Connessione al database...")
        conn_string = get_db_connection_string()
        conn = psycopg.connect(conn_string)
        
        # Esegui la migrazione
        print("⚙️  Esecuzione migrazione...")
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
        
        print("✅ Migrazione applicata con successo!")
        conn.close()
        return True
        
    except psycopg.Error as e:
        print(f"❌ Errore database: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        print("\n💡 Alternativa: Applica la migrazione manualmente:")
        print("   1. Vai su Supabase Dashboard > SQL Editor")
        print(f"   2. Copia il contenuto di {migration_file.name}")
        print("   3. Esegui la query")
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)

