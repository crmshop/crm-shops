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
    password: str  # Password temporanea per il cliente
    shop_id: UUID  # Negozio a cui appartiene il cliente


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
        
        # Filtra per shop_id se specificato, altrimenti tutti i negozi del negoziante
        query = supabase.from_('users').select('*, shops!inner(id, owner_id)').eq('role', 'cliente')
        
        if shop_id:
            query = query.eq('shops.id', str(shop_id))
        else:
            query = query.in_('shops.id', [str(sid) for sid in shop_ids])
        
        # Per semplicità, recuperiamo i clienti dalla tabella users filtrati per negozio
        # attraverso le foto cliente o altri dati associati
        # Alternativa: creare una tabella customers con shop_id
        
        # Per ora, recuperiamo i clienti che hanno foto associate ai negozi del negoziante
        customers_response = supabase.from_('customer_photos').select(
            'user_id, shops!inner(id, owner_id)'
        ).in_('shops.id', [str(sid) for sid in shop_ids]).execute()
        
        customer_ids = list(set([photo['user_id'] for photo in customers_response.data if photo.get('user_id')]))
        
        if not customer_ids:
            return []
        
        # Recupera i dati dei clienti
        users_response = supabase.from_('users').select('*').in_('id', customer_ids).eq('role', 'cliente').execute()
        
        # Aggiungi shop_id per ogni cliente (dal primo negozio trovato)
        customers = []
        for user in users_response.data:
            # Trova il primo shop associato a questo cliente
            photo_response = supabase.from_('customer_photos').select('shop_id').eq('user_id', user['id']).limit(1).execute()
            shop_id_for_customer = photo_response.data[0]['shop_id'] if photo_response.data else None
            
            customers.append({
                **user,
                'shop_id': shop_id_for_customer
            })
        
        return [CustomerResponse.model_validate(c) for c in customers]
        
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
        # Usa service key per operazioni admin
        from backend.config import settings
        if not settings.SUPABASE_SERVICE_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_SERVICE_KEY non configurata. Necessaria per creare clienti."
            )
        
        # Crea client Supabase con service key per operazioni admin
        from supabase import create_client
        admin_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        
        # Crea l'utente cliente in Supabase Auth
        auth_response = admin_supabase.auth.admin.create_user({
            "email": customer.email,
            "password": customer.password,
            "email_confirm": True,  # Auto-conferma email per clienti creati da negoziante
            "user_metadata": {
                "role": "cliente",
                "created_by_shop_owner": True,
                "shop_id": str(customer.shop_id)
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore nella creazione dell'utente cliente"
            )
        
        user_id = auth_response.user.id
        
        # Crea/aggiorna il record nella tabella users
        user_data = {
            "id": user_id,
            "email": customer.email,
            "role": "cliente",
            "full_name": customer.full_name,
            "phone": customer.phone
        }
        
        # Usa upsert per creare o aggiornare
        users_response = supabase.from_('users').upsert(user_data).execute()
        
        if not users_response.data:
            # Se fallisce, elimina l'utente da auth
            try:
                admin_supabase.auth.admin.delete_user(user_id)
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore nel salvare i dati del cliente"
            )
        
        # Crea record nella tabella customers (se esiste) o usa una relazione
        # Per ora, il cliente è associato al negozio tramite le foto che caricherà
        
        return CustomerResponse.model_validate({
            **users_response.data[0],
            "shop_id": customer.shop_id,
            "address": customer.address,
            "notes": customer.notes
        })
        
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
    """Ottieni dettagli di un cliente specifico"""
    supabase = get_supabase()
    
    try:
        # Verifica che il cliente appartenga a un negozio del negoziante
        customer_response = supabase.from_('users').select('*').eq('id', str(customer_id)).eq('role', 'cliente').single().execute()
        
        if not customer_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente non trovato"
            )
        
        # Verifica che il cliente abbia foto associate a un negozio del negoziante
        shops_response = supabase.from_('shops').select('id').eq('owner_id', current_user['id']).execute()
        shop_ids = [shop['id'] for shop in shops_response.data]
        
        photo_response = supabase.from_('customer_photos').select('shop_id').eq('user_id', str(customer_id)).in_('shop_id', [str(sid) for sid in shop_ids]).limit(1).execute()
        
        if not photo_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non autorizzato a vedere questo cliente"
            )
        
        shop_id = photo_response.data[0]['shop_id']
        
        return CustomerResponse.model_validate({
            **customer_response.data,
            "shop_id": shop_id
        })
        
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
        
        response = supabase.from_('users').update(update_data).eq('id', str(customer_id)).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore nell'aggiornamento del cliente"
            )
        
        # Recupera shop_id per la risposta
        photo_response = supabase.from_('customer_photos').select('shop_id').eq('user_id', str(customer_id)).limit(1).execute()
        shop_id = photo_response.data[0]['shop_id'] if photo_response.data else None
        
        return CustomerResponse.model_validate({
            **response.data[0],
            "shop_id": shop_id
        })
        
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
        # Leggi il file
        file_content = await file.read()
        file_name = f"{customer_id}/{file.filename}"
        
        # Carica su Supabase Storage
        bucket_name = "customer-photos"
        
        storage_response = supabase.storage.from_(bucket_name).upload(
            file_name,
            file_content,
            file_options={"content-type": file.content_type or "image/jpeg"}
        )
        
        # Ottieni URL pubblico
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        
        # Salva metadati nel database
        photo_data = {
            "user_id": str(customer_id),
            "shop_id": str(shop_id),
            "image_url": public_url,
            "angle": angle,
            "consent_given": consent_given
        }
        
        insert_response = supabase.from_('customer_photos').insert(photo_data).execute()
        
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
        
        response = supabase.from_('customer_photos').select('*').eq('user_id', str(customer_id)).in_('shop_id', [str(sid) for sid in shop_ids]).execute()
        
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

