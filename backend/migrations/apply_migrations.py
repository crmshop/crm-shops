#!/usr/bin/env python3
"""
Script per applicare migrazioni database
"""
import os
import sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def apply_migration(migration_file: Path, supabase_client):
    """Applica una singola migrazione"""
    print(f"📄 Applicando migrazione: {migration_file.name}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        # Esegui la migrazione usando Supabase
        # Nota: Supabase Python client non ha un metodo diretto per eseguire SQL arbitrario
        # Dovrai usare il service_role_key o eseguire tramite dashboard
        print(f"⚠️  Per eseguire questa migrazione, usa il Supabase Dashboard:")
        print(f"   1. Vai su SQL Editor")
        print(f"   2. Copia il contenuto di {migration_file.name}")
        print(f"   3. Esegui la query")
        print(f"\nOppure usa Supabase CLI:")
        print(f"   supabase db push")
        return False
    except Exception as e:
        print(f"❌ Errore applicando migrazione: {e}")
        return False

def main():
    """Applica tutte le migrazioni in ordine"""
    migrations_dir = Path(__file__).parent
    
    # Verifica credenziali Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL e SUPABASE_KEY devono essere configurate in .env")
        sys.exit(1)
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Trova tutte le migrazioni SQL
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("⚠️  Nessuna migrazione trovata")
        return
    
    print(f"🔍 Trovate {len(migration_files)} migrazioni")
    print("\n⚠️  Nota: Le migrazioni SQL devono essere applicate manualmente tramite:")
    print("   1. Supabase Dashboard → SQL Editor")
    print("   2. Supabase CLI: supabase db push")
    print("\nFile migrazioni:")
    for migration_file in migration_files:
        print(f"   - {migration_file.name}")

if __name__ == "__main__":
    main()






