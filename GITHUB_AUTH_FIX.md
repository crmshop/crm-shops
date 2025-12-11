# Risoluzione Problema Permessi GitHub

## Problema
```
You don't have permissions to push to "crmshop/crm-shops" on GitHub
```

## Soluzioni Disponibili

### Opzione 1: Personal Access Token (PAT) - CONSIGLIATO

1. **Crea un Personal Access Token su GitHub:**
   - Vai su: https://github.com/settings/tokens
   - Clicca "Generate new token" → "Generate new token (classic)"
   - Nome: `CRM Shops - Local Development`
   - Scadenza: Scegli una durata (es. 90 giorni o No expiration)
   - Permessi necessari:
     - ✅ `repo` (Full control of private repositories)
   - Clicca "Generate token"
   - **COPIA IL TOKEN** (lo vedrai solo una volta!)

2. **Usa il token per autenticarti:**
   
   **Metodo A: Durante il push (temporaneo)**
   ```bash
   git push origin main
   # Quando richiesto:
   # Username: marianzit
   # Password: [incolla il tuo PAT qui]
   ```

   **Metodo B: Salva nel credential helper (permanente)**
   ```bash
   # macOS
   git config --global credential.helper osxkeychain
   
   # Poi fai push normalmente
   git push origin main
   # Inserisci username e PAT quando richiesto
   # Verrà salvato nel keychain
   ```

   **Metodo C: Usa il token nell'URL (non consigliato per sicurezza)**
   ```bash
   git remote set-url origin https://marianzit:YOUR_TOKEN@github.com/crmshop/crm-shops.git
   ```

### Opzione 2: SSH (Se hai chiavi SSH configurate)

1. **Verifica se hai chiavi SSH:**
   ```bash
   ls -la ~/.ssh/id_*.pub
   ```

2. **Se non hai chiavi, creale:**
   ```bash
   ssh-keygen -t ed25519 -C "marianzit@users.noreply.github.com"
   # Premi Enter per accettare percorso default
   # Inserisci passphrase (opzionale ma consigliato)
   ```

3. **Aggiungi la chiave pubblica a GitHub:**
   ```bash
   # Copia la chiave pubblica
   cat ~/.ssh/id_ed25519.pub
   # Copia tutto l'output
   
   # Vai su: https://github.com/settings/keys
   # Clicca "New SSH key"
   # Incolla la chiave e salva
   ```

4. **Cambia remote a SSH:**
   ```bash
   git remote set-url origin git@github.com:crmshop/crm-shops.git
   git remote -v  # Verifica
   ```

5. **Testa la connessione:**
   ```bash
   ssh -T git@github.com
   # Dovresti vedere: "Hi marianzit! You've successfully authenticated..."
   ```

6. **Fai push:**
   ```bash
   git push origin main
   ```

### Opzione 3: Verifica Permessi Repository

Se il repository appartiene all'organizzazione `crmshop`:

1. **Verifica se sei collaboratore:**
   - Vai su: https://github.com/crmshop/crm-shops/settings/access
   - Controlla se il tuo account `marianzit` è nella lista dei collaboratori

2. **Se non sei collaboratore:**
   - Chiedi al proprietario del repository di aggiungerti come collaboratore
   - Oppure crea un fork (vedi Opzione 4)

### Opzione 4: Fork e Push (Se non hai accesso diretto)

Se non puoi ottenere accesso al repository originale:

1. **Crea un fork:**
   - Vai su: https://github.com/crmshop/crm-shops
   - Clicca "Fork" in alto a destra
   - Scegli dove fare il fork (sul tuo account)

2. **Cambia remote al tuo fork:**
   ```bash
   git remote set-url origin https://github.com/marianzit/crm-shops.git
   git push origin main
   ```

3. **Per sincronizzare con il repository originale:**
   ```bash
   # Aggiungi upstream (una volta)
   git remote add upstream https://github.com/crmshop/crm-shops.git
   
   # Per aggiornare dal repository originale
   git fetch upstream
   git merge upstream/main
   ```

## Soluzione Rapida (CONSIGLIATA) - GitHub CLI

Hai GitHub CLI installato! Usa questo metodo per autenticarti facilmente:

```bash
# 1. Autenticati con GitHub CLI
gh auth login

# Segui le istruzioni:
# - Seleziona "GitHub.com"
# - Seleziona "HTTPS" o "SSH" (consigliato HTTPS)
# - Seleziona "Login with a web browser" o "Paste an authentication token"
# - Se scegli web browser, segui il link e autorizza

# 2. Verifica autenticazione
gh auth status

# 3. Fai push normalmente
git push origin main
```

**Vantaggi:**
- ✅ Autenticazione automatica per Git
- ✅ Gestione token automatica
- ✅ Più sicuro e semplice

## Alternativa: Personal Access Token Manuale

Se preferisci configurare manualmente:

```bash
# 1. Crea PAT su GitHub (vedi sopra)
# 2. Configura credential helper
git config --global credential.helper osxkeychain

# 3. Fai push (inserisci PAT quando richiesto)
git push origin main
```

## Verifica Configurazione

Dopo aver configurato, verifica:

```bash
# Verifica remote
git remote -v

# Verifica configurazione Git
git config --list | grep -E "(user|credential|remote)"

# Test push (se ci sono cambiamenti)
git status
```

## Note di Sicurezza

⚠️ **IMPORTANTE:**
- **NON committare mai** il tuo PAT nel codice
- **NON condividere** il tuo PAT pubblicamente
- Se il PAT viene compromesso, revocalo immediatamente su GitHub
- Usa scadenze ragionevoli per i token
- Considera di usare SSH per maggiore sicurezza a lungo termine

## Troubleshooting

### "Permission denied (publickey)"
- Verifica che la chiave SSH sia aggiunta a GitHub
- Testa con: `ssh -T git@github.com`

### "Authentication failed"
- Verifica che il PAT sia corretto
- Controlla che il PAT abbia i permessi `repo`
- Prova a rigenerare il PAT

### "Repository not found"
- Verifica che il nome del repository sia corretto
- Controlla se il repository è privato e hai accesso
- Verifica che tu sia collaboratore del repository
