# Guida Negozio - Area Riservata

Questa guida descrive come i negozianti possono utilizzare l'area riservata per gestire clienti e foto.

## Accesso Area Riservata

1. **Registrazione/Login**:
   - Vai su `/register` e registrati come **negoziante**
   - Oppure fai login su `/login` se hai già un account

2. **Dashboard Negozio**:
   - Dopo il login, accedi alla dashboard negoziante
   - Troverai 3 tab principali:
     - **I Miei Negozi**: Gestisci i tuoi negozi
     - **Prodotti**: Gestisci il catalogo prodotti
     - **Clienti**: Gestisci i tuoi clienti

## Gestione Clienti

### Creare un Nuovo Cliente

1. Vai su **Dashboard → Clienti**
2. Clicca su **"+ Nuovo Cliente"**
3. Compila il form:
   - **Negozio**: Seleziona il negozio a cui appartiene il cliente
   - **Email**: Email del cliente (sarà usata per l'account)
   - **Password Temporanea**: Password iniziale (il cliente potrà cambiarla)
   - **Nome Completo**: Nome del cliente
   - **Telefono**: Numero di telefono (opzionale)
   - **Indirizzo**: Indirizzo del cliente (opzionale)
   - **Note**: Note aggiuntive sul cliente (opzionale)
4. Clicca **"Crea Cliente"**

**Nota**: Il sistema creerà automaticamente un account Supabase per il cliente con le credenziali fornite.

### Modificare Dati Cliente

1. Nella lista clienti, clicca **"Modifica"** sul cliente desiderato
2. Modifica i campi necessari
3. Clicca **"Salva Modifiche"**

**Nota**: L'email non può essere modificata dopo la creazione.

### Caricare Foto per un Cliente

1. Nella lista clienti, clicca **"+ Foto"** sul cliente desiderato
2. Seleziona la foto dal tuo computer
3. Scegli:
   - **Negozio**: Negozio associato alla foto
   - **Angolo**: Angolo della foto (frontale, laterale, posteriore, tre quarti)
   - **Consenso**: Se il cliente ha dato il consenso per l'uso della foto
4. Clicca **"Carica Foto"**

Le foto vengono caricate su Supabase Storage nel bucket `customer-photos` e sono accessibili pubblicamente.

### Visualizzare Foto Cliente

1. Nella lista clienti, clicca **"Foto"** sul cliente desiderato
2. Vedrai tutte le foto caricate per quel cliente

## Gestione Negozi

### Creare un Negozio

1. Vai su **Dashboard → I Miei Negozi**
2. Clicca su **"+ Nuovo Negozio"**
3. Compila i dati del negozio
4. Salva

### Gestire Prodotti

1. Vai su **Dashboard → Prodotti**
2. Clicca su **"+ Nuovo Prodotto"**
3. Compila i dati del prodotto:
   - Nome, descrizione, categoria
   - Stagione, occasione
   - Prezzo, immagine
4. Salva

## Workflow Completo

### Scenario: Nuovo Cliente con Foto

1. **Crea il Cliente**:
   ```
   Dashboard → Clienti → + Nuovo Cliente
   - Inserisci email, password, dati
   - Seleziona negozio
   - Crea
   ```

2. **Carica Foto Cliente**:
   ```
   Dashboard → Clienti → + Foto (sul cliente)
   - Seleziona foto
   - Scegli angolo
   - Carica
   ```

3. **Crea Prodotti** (se necessario):
   ```
   Dashboard → Prodotti → + Nuovo Prodotto
   - Inserisci dati prodotto
   - Carica immagine prodotto
   ```

4. **Genera Immagine AI** (opzionale):
   ```
   Il cliente può generare immagini AI dalla sua area cliente
   oppure puoi farlo tu se hai accesso al suo account
   ```

## Permessi e Sicurezza

- **Solo Negozianti**: Solo gli utenti con ruolo `negoziante` possono accedere all'area gestione clienti
- **Proprietà Negozi**: I negozianti possono vedere solo i clienti dei propri negozi
- **Creazione Account**: Per creare clienti, è necessaria `SUPABASE_SERVICE_KEY` configurata
- **Upload Foto**: Le foto vengono caricate su Storage pubblico ma associate al cliente

## Troubleshooting

### Errore "SUPABASE_SERVICE_KEY non configurata"
- Configura `SUPABASE_SERVICE_KEY` nel file `.env`
- Ottieni la Service Key da Supabase Dashboard → Settings → API

### Cliente non appare nella lista
- Verifica che il cliente abbia almeno una foto associata a un tuo negozio
- I clienti vengono mostrati solo se hanno foto nei tuoi negozi

### Upload foto fallisce
- Verifica che il bucket `customer-photos` esista su Supabase Storage
- Controlla che il bucket sia pubblico
- Verifica dimensione file (max 10MB)

## API Endpoints Disponibili

- `GET /api/customers/` - Lista clienti
- `POST /api/customers/` - Crea cliente
- `GET /api/customers/{id}` - Dettagli cliente
- `PUT /api/customers/{id}` - Aggiorna cliente
- `POST /api/customers/{id}/photos` - Carica foto cliente
- `GET /api/customers/{id}/photos` - Lista foto cliente

Tutti gli endpoint richiedono autenticazione come negoziante.

