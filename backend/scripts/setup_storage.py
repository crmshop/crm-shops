#!/usr/bin/env python3
"""
Script per configurare Storage buckets su Supabase
"""
import os
import sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def setup_storage_buckets():
    """Configura i bucket Storage necessari"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL e SUPABASE_KEY devono essere configurate in .env")
        sys.exit(1)
    
    supabase = create_client(supabase_url, supabase_key)
    
    buckets = [
        {
            "name": "customer-photos",
            "public": True,
            "description": "Foto dei clienti caricate per la simulazione AI"
        },
        {
            "name": "product-images",
            "public": True,
            "description": "Immagini dei prodotti del catalogo"
        },
        {
            "name": "generated-images",
            "public": True,
            "description": "Immagini generate dall'AI"
        }
    ]
    
    print("📦 Configurazione Storage buckets...\n")
    
    for bucket in buckets:
        try:
            # Prova a creare il bucket
            # Nota: L'API Python di Supabase potrebbe non supportare direttamente la creazione di bucket
            # Dovrai crearli manualmente dal dashboard o usare l'API REST direttamente
            print(f"⚠️  Bucket '{bucket['name']}' deve essere creato manualmente:")
            print(f"   1. Vai su Supabase Dashboard → Storage")
            print(f"   2. Clicca 'New bucket'")
            print(f"   3. Nome: {bucket['name']}")
            print(f"   4. Pubblico: {bucket['public']}")
            print(f"   5. Descrizione: {bucket['description']}")
            print()
            
            # Verifica se il bucket esiste
            try:
                files = supabase.storage.from_(bucket['name']).list()
                print(f"✅ Bucket '{bucket['name']}' esiste già")
            except Exception as e:
                if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                    print(f"❌ Bucket '{bucket['name']}' non trovato - crealo manualmente")
                else:
                    print(f"⚠️  Errore verificando bucket '{bucket['name']}': {e}")
            print()
            
        except Exception as e:
            print(f"❌ Errore con bucket '{bucket['name']}': {e}")
    
    print("\n📝 Nota: I bucket devono essere creati manualmente dal Dashboard Supabase.")
    print("   Vai su: https://app.supabase.com/project/[PROJECT_ID]/storage/buckets")
    print("\n✅ Setup completato!")

if __name__ == "__main__":
    setup_storage_buckets()






