#!/usr/bin/env python3
"""
Script per applicare la migration 007_scenario_prompts.sql
"""
import os
import sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def apply_migration_007():
    """Applica la migration 007_scenario_prompts.sql"""
    migration_file = Path(__file__).parent / "007_scenario_prompts.sql"
    
    if not migration_file.exists():
        print(f"❌ File migration non trovato: {migration_file}")
        sys.exit(1)
    
    # Verifica credenziali Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ SUPABASE_URL e SUPABASE_SERVICE_KEY devono essere configurate in .env")
        print("\nPer applicare la migration manualmente:")
        print("1. Vai su Supabase Dashboard → SQL Editor")
        print(f"2. Copia il contenuto di {migration_file.name}")
        print("3. Esegui la query")
        sys.exit(1)
    
    # Leggi il contenuto della migration
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"📄 Applicando migration: {migration_file.name}")
    print("⚠️  Nota: Supabase Python client non supporta direttamente l'esecuzione di SQL arbitrario.")
    print("   La migration deve essere applicata manualmente tramite Supabase Dashboard.\n")
    
    print("📋 Istruzioni:")
    print("1. Vai su https://supabase.com/dashboard")
    print("2. Seleziona il tuo progetto")
    print("3. Vai su SQL Editor (icona database nella sidebar)")
    print("4. Clicca su 'New query'")
    print("5. Copia e incolla il seguente SQL:\n")
    print("=" * 80)
    print(sql)
    print("=" * 80)
    print("\n6. Clicca su 'Run' per eseguire la query")
    print("\n✅ Dopo aver applicato la migration, il sistema sarà pronto per usare gli scenario prompts!")
    
    # Tentativo di applicare tramite REST API (richiede configurazione specifica)
    try:
        # Nota: Questo approccio potrebbe non funzionare con tutte le versioni di Supabase
        # Il modo più affidabile è usare il Dashboard o Supabase CLI
        print("\n💡 Alternativa: Usa Supabase CLI se installato:")
        print(f"   supabase db push --file {migration_file}")
    except Exception as e:
        print(f"\n⚠️  Impossibile applicare automaticamente: {e}")

if __name__ == "__main__":
    apply_migration_007()
