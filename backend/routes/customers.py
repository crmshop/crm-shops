"""
Route per gestione clienti (solo negozianti)
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from backend.database import get_supabase
from backend.middleware.auth import get_current_shop_owner
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/customers", tags=["clienti"])


class CustomerBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    shop_id: UUID  # Negozio a cui appartiene il cliente
    # Nota: I clienti creati dal negoziante NON hanno account autonomo
    # Rimangono solo nell'area del negozio senza email di conferma


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: UUID
    shop_id: UUID
    created_at: str
    updated_at: str
    user_id: Optional[UUID] = None  # ID utente se ha account

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    shop_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_shop_owner)
):
    """Lista clienti del negoziante (solo propri negozi)"""
    supabase = get_supabase()
    
    # Se shop_id è specificato, verifica che appartenga al negoziante
    if shop_id:
        shop_response = supabase.from_('shops').select('id, owner_id').eq('id', str(shop_id)).single().execute()
        if not shop_response.data or shop_response.data['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non autorizzato a vedere i clienti di questo negozio"
            )
    
    try:
        # Recupera tutti i negozi del negoziante
        shops_response = supabase.from_('shops').select('id').eq('owner_id', current_user['id']).execute()
        shop_ids = [shop['id'] for shop in shops_response.data]
        
        if not shop_ids:
            return []
        
        # I clienti creati dal negoziante sono nella tabella shop_customers
        # Non nella tabella users (quelli sono clienti esterni con account)
        query = supabase.from_('shop_customers').select('*')
        
        # Filtra per shop_id se specificato, altrimenti tutti i negozi del negoziante
        if shop_id:
            # Verifica che shop_id appartenga al negoziante
            if str(shop_id) not in [str(sid) for sid in shop_ids]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Non autorizzato a vedere i clienti di questo negozio"
                )
            query = query.eq('shop_id', str(shop_id))
        else:
            query = query.in_('shop_id', [str(sid) for sid in shop_ids])
        
        customers_response = query.execute()
        
        if not customers_response.data:
            return []
        
        # Converti i dati in CustomerResponse
        customers = []
        for customer_data in customers_response.data:
            # Aggiungi campi mancanti per compatibilità con CustomerResponse
            customer_dict = {
                'id': customer_data.get('id'),
                'shop_id': customer_data.get('shop_id'),
                'email': customer_data.get('email'),
                'full_name': customer_data.get('full_name'),
                'phone': customer_data.get('phone'),
                'address': customer_data.get('address'),
                'notes': customer_data.get('notes'),
                'created_at': customer_data.get('created_at', customer_data.get('created_at')),
                'updated_at': customer_data.get('updated_at', customer_data.get('created_at')),
                'user_id': None  # I clienti shop_customers non hanno user_id
            }
            customers.append(CustomerResponse.model_validate(customer_dict))
        
        return customers
        
    except Exception as e:
        logger.error(f"Errore nel listare i clienti: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nel recupero dei clienti"
        )


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    current_user: dict = Depends(get_current_shop_owner)
):
    """Crea un nuovo cliente (solo negozianti)"""
    supabase = get_supabase()
    
    # Verifica che il negozio appartenga al negoziante
    shop_response = supabase.from_('shops').select('id, owner_id').eq('id', str(customer.shop_id)).single().execute()
    if not shop_response.data or shop_response.data['owner_id'] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a creare clienti per questo negozio"
        )
    
    try:
        # I clienti creati dal negoziante NON hanno account Supabase Auth
        # Sono solo record nella tabella shop_customers (separata da users)
        # NON ricevono email e rimangono solo nell'area del negozio
        
        customer_data = {
            "shop_id": str(customer.shop_id),
            "email": customer.email,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "address": customer.address,
            "notes": customer.notes
        }
        
        # Inserisci nella tabella shop_customers (non users)
        customers_response = supabase.from_('shop_customers').insert(customer_data).execute()
        
        if not customers_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore nel salvare i dati del cliente"
            )
        
        return CustomerResponse.model_validate(customers_response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore nella creazione del cliente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nella creazione del cliente: {str(e)}"
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    current_user: dict = Depends(get_current_shop_owner)
):
    """Ottieni dettagli di un cliente interno specifico (solo clienti del negozio, non clienti esterni)"""
    supabase = get_supabase()
    
    try:
        # Recupera il cliente dalla tabella shop_customers (solo clienti interni)
        customer_response = supabase.from_('shop_customers').select('*').eq('id', str(customer_id)).single().execute()
        
        if not customer_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente non trovato"
            )
        
        # Verifica che il cliente appartenga a un negozio del negoziante
        shops_response = supabase.from_('shops').select('id').eq('owner_id', current_user['id']).execute()
        shop_ids = [str(shop['id']) for shop in shops_response.data]
        
        if customer_response.data['shop_id'] not in shop_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non autorizzato a vedere questo cliente"
            )
        
        return CustomerResponse.model_validate(customer_response.data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore nel recuperare il cliente {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nel recupero del cliente"
        )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    customer: CustomerUpdate,
    current_user: dict = Depends(get_current_shop_owner)
):
    """Aggiorna dati di un cliente"""
    supabase = get_supabase()
    
    # Verifica autorizzazione (stesso controllo di get_customer)
    await get_customer(customer_id, current_user)
    
    try:
        update_data = customer.model_dump(exclude_unset=True)
        
        # Aggiorna nella tabella shop_customers
        response = supabase.from_('shop_customers').update(update_data).eq('id', str(customer_id)).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore nell'aggiornamento del cliente"
            )
        
        return CustomerResponse.model_validate(response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore nell'aggiornamento del cliente {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nell'aggiornamento del cliente"
        )


@router.post("/{customer_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_customer_photo(
    customer_id: UUID,
    file: UploadFile = File(...),
    shop_id: Optional[UUID] = None,
    angle: Optional[str] = None,
    consent_given: bool = False,
    current_user: dict = Depends(get_current_shop_owner)
):
    """Carica una foto per un cliente (solo negozianti)"""
    # Usa admin client per upload Storage (bypassa RLS)
    from backend.database import get_supabase_admin
    try:
        supabase_admin = get_supabase_admin()
        logger.info("✅ Client Supabase Admin inizializzato correttamente")
    except Exception as e:
        logger.error(f"❌ Errore inizializzazione Supabase Admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore configurazione backend: SUPABASE_SERVICE_KEY potrebbe non essere configurata"
        )
    
    # Usa client normale per query database (rispetta RLS)
    supabase = get_supabase()
    
    # Verifica che il cliente appartenga a un negozio del negoziante
    await get_customer(customer_id, current_user)
    
    # Se shop_id non è specificato, usa il primo negozio del negoziante associato al cliente
    if not shop_id:
        shops_response = supabase.from_('shops').select('id').eq('owner_id', current_user['id']).execute()
        if shops_response.data:
            shop_id = shops_response.data[0]['id']
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nessun negozio trovato per il negoziante"
            )
    
    # Verifica che il negozio appartenga al negoziante
    shop_response = supabase.from_('shops').select('id, owner_id').eq('id', str(shop_id)).single().execute()
    if not shop_response.data or shop_response.data['owner_id'] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a caricare foto per questo negozio"
        )
    
    try:
        # Verifica configurazione SUPABASE_SERVICE_KEY
        from backend.config import settings
        if not settings.SUPABASE_SERVICE_KEY:
            logger.error("❌ SUPABASE_SERVICE_KEY non configurata!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_SERVICE_KEY non configurata. Configurala su Render Dashboard > Environment Variables"
            )
        logger.info(f"✅ SUPABASE_SERVICE_KEY configurata (lunghezza: {len(settings.SUPABASE_SERVICE_KEY)})")
        
        # Verifica che il client admin sia inizializzato correttamente
        logger.info(f"🔍 Verifica client admin: {type(supabase_admin)}")
        logger.info(f"🔍 Client admin URL: {supabase_admin.supabase_url if hasattr(supabase_admin, 'supabase_url') else 'N/A'}")
        
        # Leggi il file
        file_content = await file.read()
        file_name = f"{customer_id}/{file.filename}"
        
        # Carica su Supabase Storage usando admin client (bypassa RLS)
        bucket_name = "customer-photos"
        
        # Verifica che il bucket esista (opzionale, ma utile per debug)
        try:
            buckets = supabase_admin.storage.list_buckets()
            bucket_exists = any(b.name == bucket_name for b in buckets)
            logger.info(f"🔍 Bucket '{bucket_name}' esiste: {bucket_exists}")
            if not bucket_exists:
                logger.warning(f"⚠️ Bucket '{bucket_name}' non trovato. Verifica su Supabase Dashboard > Storage")
        except Exception as bucket_check_error:
            logger.warning(f"⚠️ Impossibile verificare bucket: {bucket_check_error}")
        
        logger.info(f"📤 Tentativo upload Storage: bucket={bucket_name}, file={file_name}")
        logger.info(f"   Service key presente: {bool(settings.SUPABASE_SERVICE_KEY)}")
        logger.info(f"   Service key lunghezza: {len(settings.SUPABASE_SERVICE_KEY) if settings.SUPABASE_SERVICE_KEY else 0}")
        
        try:
            # Prova upload con upsert per sovrascrivere file esistenti
            storage_response = supabase_admin.storage.from_(bucket_name).upload(
                file_name,
                file_content,
                file_options={
                    "content-type": file.content_type or "image/jpeg",
                    "upsert": "true"  # Permette sovrascrittura
                }
            )
            logger.info(f"✅ Upload Storage riuscito: {storage_response}")
        except Exception as storage_error:
            error_str = str(storage_error)
            logger.error(f"❌ Errore durante upload Storage: {storage_error}")
            logger.error(f"   Tipo errore: {type(storage_error)}")
            logger.error(f"   Dettagli: {error_str}")
            
            # Verifica se è un errore RLS o di autorizzazione
            if any(keyword in error_str.lower() for keyword in ["row-level security", "unauthorized", "permission", "forbidden", "403", "401"]):
                logger.error("⚠️ Errore RLS/Autorizzazione su Storage")
                logger.error("   Possibili cause:")
                logger.error("   1. SUPABASE_SERVICE_KEY non configurata su Render")
                logger.error("   2. SUPABASE_SERVICE_KEY è la anon key invece della service_role key")
                logger.error("   3. Storage policies su Supabase bloccano anche il service role")
                logger.error("   4. Bucket 'customer-photos' non esiste o ha policies restrittive")
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "Errore RLS su Storage. Verifica:\n"
                        "1. SUPABASE_SERVICE_KEY è configurata su Render Dashboard > Environment\n"
                        "2. È la service_role key (NON la anon key) da Supabase Dashboard > Settings > API\n"
                        "3. Il bucket 'customer-photos' esiste su Supabase Dashboard > Storage\n"
                        "4. Le Storage policies permettono upload con service role"
                    )
                )
            raise
        
        # Ottieni URL pubblico
        public_url = supabase_admin.storage.from_(bucket_name).get_public_url(file_name)
        
        # Salva metadati nel database usando admin client (bypassa RLS)
        # Usa customer_id (cliente negozio) invece di user_id (cliente esterno)
        photo_data = {
            "customer_id": str(customer_id),  # Cliente negozio (non ha user_id)
            "shop_id": str(shop_id),
            "image_url": public_url,
            "angle": angle,
            "consent_given": consent_given
        }
        
        logger.info(f"📝 Tentativo insert customer_photos con admin client: {photo_data}")
        try:
            insert_response = supabase_admin.from_('customer_photos').insert(photo_data).execute()
            logger.info(f"✅ Insert riuscito: {insert_response.data}")
        except Exception as insert_error:
            logger.error(f"❌ Errore durante insert con admin client: {insert_error}")
            logger.error(f"   Tipo errore: {type(insert_error)}")
            logger.error(f"   Dettagli: {str(insert_error)}")
            # Verifica se SUPABASE_SERVICE_KEY è configurata
            from backend.config import settings
            if not settings.SUPABASE_SERVICE_KEY:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="SUPABASE_SERVICE_KEY non configurata. Configurala su Render Dashboard > Environment Variables"
                )
            raise
        
        if not insert_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore nel salvare la foto nel database"
            )
        
        return {
            "message": "Foto caricata con successo",
            "photo": insert_response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore durante l'upload della foto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'upload della foto: {str(e)}"
        )


@router.get("/{customer_id}/photos")
async def get_customer_photos(
    customer_id: UUID,
    current_user: dict = Depends(get_current_shop_owner)
):
    """Ottieni tutte le foto di un cliente"""
    supabase = get_supabase()
    
    # Verifica autorizzazione
    await get_customer(customer_id, current_user)
    
    try:
        # Recupera shop_ids del negoziante
        shops_response = supabase.from_('shops').select('id').eq('owner_id', current_user['id']).execute()
        shop_ids = [shop['id'] for shop in shops_response.data]
        
        # Recupera foto usando customer_id (cliente negozio) invece di user_id
        response = supabase.from_('customer_photos').select('*').eq('customer_id', str(customer_id)).in_('shop_id', [str(sid) for sid in shop_ids]).execute()
        
        return {
            "photos": response.data or []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore nel recuperare le foto del cliente {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nel recupero delle foto"
        )

