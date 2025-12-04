# Architettura Gestione Clienti

Questo documento descrive l'architettura del sistema di gestione clienti in CRM Shops.

## Due Tipi di Clienti

Il sistema distingue tra due tipi di clienti:

### 1. Clienti Interni (Shop Customers)
- **Creati da**: Negoziante
- **Account**: ❌ NO account Supabase Auth
- **Email**: ❌ NO email inviata
- **Accesso**: ❌ NON possono fare login
- **Visibilità**: Solo nell'area riservata del negoziante
- **Tabella**: `shop_customers`
- **Uso**: Gestiti completamente dal negoziante

### 2. Clienti Esterni (External Customers)
- **Creati da**: Auto-registrazione
- **Account**: ✅ Account Supabase Auth
- **Email**: ✅ Email di conferma
- **Accesso**: ✅ Possono fare login
- **Visibilità**: Solo nella loro area personale
- **Tabella**: `users` (con riferimento a `auth.users`)
- **Uso**: Possono caricare foto, creare outfit, generare immagini AI

## Schema Database

### Tabella `shop_customers`
```sql
CREATE TABLE shop_customers (
    id UUID PRIMARY KEY,
    shop_id UUID REFERENCES shops(id),
    email VARCHAR(255),
    full_name VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(shop_id, email)
);
```

### Tabella `customer_photos`
Supporta entrambi i tipi di clienti:
- `user_id`: Per clienti esterni (riferimento a `users.id`)
- `customer_id`: Per clienti interni (riferimento a `shop_customers.id`)

```sql
ALTER TABLE customer_photos 
ADD COLUMN customer_id UUID REFERENCES shop_customers(id);
```

## API Endpoints

### Clienti Interni (Negoziante)
- `GET /api/customers/` - Lista clienti negozio
- `POST /api/customers/` - Crea cliente negozio
- `GET /api/customers/{id}` - Dettagli cliente
- `PUT /api/customers/{id}` - Aggiorna cliente
- `POST /api/customers/{id}/photos` - Carica foto cliente
- `GET /api/customers/{id}/photos` - Lista foto cliente

**Protezione**: Solo negozianti autenticati

### Clienti Esterni (Auto-registrazione)
- `POST /api/auth/register` - Registrazione cliente esterno
- `POST /api/auth/login` - Login cliente esterno
- `GET /api/customer-photos/` - Lista foto proprie
- `POST /api/customer-photos/` - Upload foto propria

**Protezione**: Solo clienti autenticati

## Flusso Operativo

### Scenario 1: Cliente Interno (Negoziante)
```
1. Negozio crea cliente → shop_customers
2. Negozio carica foto → customer_photos (customer_id)
3. Cliente NON riceve email
4. Cliente NON può fare login
5. Cliente visibile solo al negoziante
```

### Scenario 2: Cliente Esterno (Auto-registrazione)
```
1. Cliente si registra → auth.users + users
2. Cliente riceve email conferma
3. Cliente fa login
4. Cliente carica foto → customer_photos (user_id)
5. Cliente può generare immagini AI
6. Cliente NON è associato a nessun negozio
```

## Query Esempi

### Lista clienti interni di un negozio
```sql
SELECT * FROM shop_customers 
WHERE shop_id = '...';
```

### Lista foto cliente interno
```sql
SELECT * FROM customer_photos 
WHERE customer_id = '...';
```

### Lista foto cliente esterno
```sql
SELECT * FROM customer_photos 
WHERE user_id = '...';
```

## Vantaggi Architettura

1. **Separazione Chiara**: Clienti interni ed esterni completamente separati
2. **Privacy**: Clienti esterni non visibili ai negozianti
3. **Semplicità**: Clienti interni senza complessità Auth
4. **Flessibilità**: Ogni tipo di cliente ha il suo flusso

## Migrazione

Per applicare le modifiche al database:

```bash
# Applica migrazione shop_customers
# Vedi backend/migrations/003_shop_customers.sql
```

La migrazione:
- Crea tabella `shop_customers`
- Aggiunge colonna `customer_id` a `customer_photos`
- Crea indici per performance
- Aggiunge trigger per `updated_at`




