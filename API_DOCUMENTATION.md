# Documentazione API - CRM Shops

## Base URL

```
http://localhost:8000
```

## Endpoint Disponibili

### Autenticazione (`/api/auth`)

#### POST `/api/auth/register`
Registra un nuovo utente.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "cliente",  // o "negoziante"
  "full_name": "Nome Cognome",  // opzionale
  "phone": "+39 123 456 7890"  // opzionale
}
```

**Response:**
```json
{
  "message": "Registrazione avvenuta con successo...",
  "access_token": "eyJhbGci...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "cliente",
    "full_name": "Nome Cognome"
  }
}
```

#### POST `/api/auth/login`
Effettua il login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login avvenuto con successo",
  "access_token": "eyJhbGci...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "cliente",
    "full_name": "Nome Cognome"
  }
}
```

#### POST `/api/auth/logout`
Effettua il logout.

**Response:**
```json
{
  "message": "Logout avvenuto con successo"
}
```

---

### Negozi (`/api/shops`)

#### GET `/api/shops`
Lista tutti i negozi o filtra per proprietario.

**Query Parameters:**
- `owner_id` (UUID, opzionale): Filtra per proprietario

**Response:**
```json
{
  "shops": [
    {
      "id": "uuid",
      "owner_id": "uuid",
      "name": "Nome Negozio",
      "description": "Descrizione",
      "address": "Indirizzo",
      "phone": "+39 123 456 7890",
      "email": "shop@example.com",
      "website": "https://shop.com",
      "created_at": "2025-12-03T...",
      "updated_at": "2025-12-03T..."
    }
  ],
  "count": 1
}
```

#### GET `/api/shops/{shop_id}`
Ottieni dettagli di un negozio specifico.

#### POST `/api/shops`
Crea un nuovo negozio.

**Request Body:**
```json
{
  "owner_id": "uuid",
  "name": "Nome Negozio",
  "description": "Descrizione",  // opzionale
  "address": "Indirizzo",  // opzionale
  "phone": "+39 123 456 7890",  // opzionale
  "email": "shop@example.com",  // opzionale
  "website": "https://shop.com"  // opzionale
}
```

#### PUT `/api/shops/{shop_id}`
Aggiorna un negozio esistente.

#### DELETE `/api/shops/{shop_id}`
Elimina un negozio.

---

### Prodotti (`/api/products`)

#### GET `/api/products`
Lista prodotti con filtri opzionali.

**Query Parameters:**
- `shop_id` (UUID, opzionale): Filtra per negozio
- `category` (string, opzionale): Filtra per categoria ('vestiti', 'scarpe', 'accessori')
- `available` (boolean, opzionale): Filtra per disponibilità

**Response:**
```json
{
  "products": [
    {
      "id": "uuid",
      "shop_id": "uuid",
      "name": "Nome Prodotto",
      "description": "Descrizione",
      "category": "vestiti",
      "season": "inverno",
      "occasion": "casual",
      "style": "casual",
      "price": 99.99,
      "image_url": "https://...",
      "available": true,
      "created_at": "2025-12-03T...",
      "updated_at": "2025-12-03T..."
    }
  ],
  "count": 1
}
```

#### GET `/api/products/{product_id}`
Ottieni dettagli di un prodotto specifico.

#### POST `/api/products`
Crea un nuovo prodotto.

**Request Body:**
```json
{
  "shop_id": "uuid",
  "name": "Nome Prodotto",
  "description": "Descrizione",  // opzionale
  "category": "vestiti",  // 'vestiti', 'scarpe', 'accessori'
  "season": "inverno",  // opzionale
  "occasion": "casual",  // opzionale
  "style": "casual",  // opzionale
  "price": 99.99,  // opzionale
  "image_url": "https://...",  // opzionale
  "available": true  // default: true
}
```

#### PUT `/api/products/{product_id}`
Aggiorna un prodotto esistente.

#### DELETE `/api/products/{product_id}`
Elimina un prodotto.

---

### Outfit (`/api/outfits`)

#### GET `/api/outfits`
Lista outfit con filtri opzionali.

**Query Parameters:**
- `user_id` (UUID, opzionale): Filtra per utente
- `shop_id` (UUID, opzionale): Filtra per negozio

**Response:**
```json
{
  "outfits": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "shop_id": "uuid",
      "name": "Outfit Invernale",
      "product_ids": ["uuid1", "uuid2"],
      "created_at": "2025-12-03T..."
    }
  ],
  "count": 1
}
```

#### GET `/api/outfits/{outfit_id}`
Ottieni dettagli di un outfit specifico.

#### POST `/api/outfits`
Crea un nuovo outfit.

**Request Body:**
```json
{
  "user_id": "uuid",
  "shop_id": "uuid",
  "name": "Outfit Invernale",  // opzionale
  "product_ids": ["uuid1", "uuid2"]
}
```

#### DELETE `/api/outfits/{outfit_id}`
Elimina un outfit.

---

## Health Check

#### GET `/health`
Verifica lo stato dell'API e della connessione Supabase.

**Response:**
```json
{
  "status": "healthy",
  "supabase": "connected",
  "environment": "development"
}
```

#### GET `/`
Informazioni generali sull'API.

**Response:**
```json
{
  "message": "CRM Shops API",
  "status": "running",
  "version": "0.1.0",
  "environment": "development"
}
```

---

## Errori

Tutti gli endpoint restituiscono errori nel formato:

```json
{
  "detail": "Messaggio di errore"
}
```

**Status Codes:**
- `200` - Successo
- `201` - Creato con successo
- `400` - Richiesta non valida
- `401` - Non autorizzato
- `404` - Non trovato
- `500` - Errore server

---

## Autenticazione

Per gli endpoint che richiedono autenticazione (da implementare), includere l'header:

```
Authorization: Bearer <access_token>
```

---

## Note

- Tutti gli UUID devono essere in formato stringa standard UUID
- Le date sono in formato ISO 8601 con timezone
- I filtri opzionali possono essere combinati
- Le operazioni DELETE sono permanenti (CASCADE su relazioni)






