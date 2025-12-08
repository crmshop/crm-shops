#!/usr/bin/env python3
"""
Script per verificare se il bucket generated-images esiste su Supabase Storage
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carica variabili d'ambiente
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

try:
    from supabase import create_client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL non trovata in .env")
        sys.exit(1)
    
    # Prova prima con service key, poi con anon key
    supabase_key_to_use = None
    key_type = None
    
    if supabase_service_key:
        try:
            print(f"🔌 Tentativo connessione con Service Key...")
            supabase = create_client(supabase_url, supabase_service_key)
            # Se la creazione ha successo, testa una query semplice
            try:
                supabase.storage.list_buckets()
                supabase_key_to_use = supabase_service_key
                key_type = "Service Key"
            except:
                pass
        except:
            pass
    
    if not supabase_key_to_use and supabase_key:
        try:
            print(f"🔌 Tentativo connessione con Anon Key...")
            supabase = create_client(supabase_url, supabase_key)
            supabase_key_to_use = supabase_key
            key_type = "Anon Key"
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            sys.exit(1)
    
    if not supabase_key_to_use:
        print("❌ Nessuna chiave valida trovata")
        sys.exit(1)
    
    print(f"✅ Connesso con: {key_type}")
    print(f"   URL: {supabase_url}")
    print()
    
    # Bucket da verificare
    bucket_name = "generated-images"
    
    print(f"📦 Verifica bucket: {bucket_name}")
    print("-" * 50)
    
    try:
        # Prova a listare i file nel bucket (se esiste)
        files = supabase.storage.from_(bucket_name).list()
        print(f"✅ Bucket '{bucket_name}' ESISTE")
        print(f"   File presenti: {len(files)}")
        if files:
            print(f"   Primi file:")
            for file in files[:5]:
                print(f"     - {file.get('name', 'N/A')}")
            if len(files) > 5:
                print(f"     ... e altri {len(files) - 5} file")
        else:
            print(f"   Bucket vuoto (pronto per uso)")
        print()
        print("✅ Il bucket è configurato correttamente!")
        
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "does not exist" in error_msg or "bucket" in error_msg:
            print(f"❌ Bucket '{bucket_name}' NON TROVATO")
            print()
            print("📝 Per creare il bucket:")
            print("   1. Vai su Supabase Dashboard → Storage")
            print("   2. Clicca 'New bucket'")
            print("   3. Nome: generated-images")
            print("   4. Seleziona 'Public bucket'")
            print("   5. Descrizione: 'Immagini generate dall'AI'")
            print("   6. Clicca 'Create bucket'")
            sys.exit(1)
        else:
            print(f"⚠️  Errore verificando bucket: {e}")
            print()
            print("💡 Potrebbe essere un problema di permessi o connessione")
            sys.exit(1)
    
    # Verifica anche gli altri bucket necessari
    print()
    print("📋 Verifica altri bucket necessari:")
    print("-" * 50)
    
    required_buckets = [
        "customer-photos",
        "product-images",
        "generated-images"
    ]
    
    for bucket in required_buckets:
        try:
            files = supabase.storage.from_(bucket).list()
            print(f"✅ {bucket}: OK ({len(files)} file)")
        except Exception as e:
            print(f"❌ {bucket}: NON TROVATO")
    
except ImportError as e:
    print(f"❌ Errore import: {e}")
    print("   Assicurati di aver attivato il virtual environment")
    sys.exit(1)
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

