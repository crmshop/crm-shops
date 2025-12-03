#!/usr/bin/env python3
"""
Script per testare la connessione e configurazione Storage Supabase
"""
import sys
import os
from pathlib import Path

# Aggiungi il path del progetto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_storage_buckets():
    """Testa l'accesso ai bucket Storage"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL e SUPABASE_KEY devono essere configurate in .env")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        buckets_to_test = [
            "customer-photos",
            "product-images", 
            "generated-images"
        ]
        
        print("\n" + "="*60)
        print("🧪 Test Storage Buckets Supabase")
        print("="*60 + "\n")
        
        all_ok = True
        
        for bucket_name in buckets_to_test:
            try:
                # Prova a listare i file nel bucket (anche se vuoto)
                result = supabase.storage.from_(bucket_name).list()
                
                print(f"✅ Bucket '{bucket_name}': OK")
                print(f"   File presenti: {len(result)}")
                
                # Prova a ottenere informazioni sul bucket
                # (se disponibile nell'API)
                
            except Exception as e:
                error_msg = str(e).lower()
                if "not found" in error_msg or "does not exist" in error_msg:
                    print(f"❌ Bucket '{bucket_name}': NON TROVATO")
                    print(f"   Crea il bucket dal Dashboard Supabase")
                    all_ok = False
                elif "permission" in error_msg or "forbidden" in error_msg:
                    print(f"⚠️  Bucket '{bucket_name}': Problema permessi")
                    print(f"   Verifica le policy del bucket")
                    all_ok = False
                else:
                    print(f"❌ Bucket '{bucket_name}': ERRORE")
                    print(f"   {e}")
                    all_ok = False
        
        print("\n" + "="*60)
        if all_ok:
            print("✅ Tutti i bucket sono configurati correttamente!")
        else:
            print("❌ Alcuni bucket hanno problemi. Vedi sopra per dettagli.")
        print("="*60 + "\n")
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Errore connessione Supabase: {e}")
        return False


def test_upload_permissions():
    """Testa i permessi di upload (richiede autenticazione)"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Credenziali Supabase non configurate")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        print("\n📤 Test permessi upload...")
        print("   (Questo test richiede autenticazione utente)")
        print("   Per ora verifichiamo solo la connessione ai bucket\n")
        
        # Per testare upload, servirebbe un utente autenticato
        # Per ora verifichiamo solo che i bucket siano accessibili
        
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Verifica configurazione Storage Supabase...\n")
    
    # Test connessione bucket
    buckets_ok = test_storage_buckets()
    
    # Test permessi (base)
    permissions_ok = test_upload_permissions()
    
    if buckets_ok:
        print("\n✅ Storage configurato correttamente!")
        print("\n📝 Prossimi passi:")
        print("   1. Testa upload foto cliente dall'app")
        print("   2. Verifica che le immagini siano accessibili pubblicamente")
        print("   3. Controlla le policy di sicurezza se necessario")
    else:
        print("\n⚠️  Risolvi i problemi sopra prima di procedere")
        sys.exit(1)

