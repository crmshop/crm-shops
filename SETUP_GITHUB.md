# Guida Setup GitHub con MCP

Questa guida ti aiuterà a configurare GitHub per il progetto CRM Shops usando MCP GitHub (già configurato in Cursor).

## Prerequisiti

- MCP GitHub configurato in Cursor (già presente)
- Account GitHub autenticato tramite MCP

## Repository già creato! ✅

Il repository è stato creato automaticamente tramite MCP GitHub:
- **URL**: https://github.com/crmshop/crm-shops
- **Nome**: crm-shops
- **Descrizione**: Sistema CRM per negozi con AI generativa

## Configurazione Git locale

Se non già fatto, configura Git:

```bash
git config --global user.name "Il Tuo Nome"
git config --global user.email "tua-email@example.com"
```

## Collegare repository locale e fare push

Il repository è già stato creato su GitHub. Ora collega il repository locale:

```bash
cd /Users/mariofo/Python_projects/CRM_shops

# Aggiungi remote (se non già presente)
git remote add origin https://github.com/crmshop/crm-shops.git

# Verifica remote
git remote -v

# Fai commit e push
git add .
git commit -m "Initial commit: Setup progetto CRM Shops"
git branch -M main
git push -u origin main
```

### Risoluzione problemi autenticazione

Se ottieni errori di autenticazione durante il push:

**Opzione 1: Usa Personal Access Token**
1. Crea un token su GitHub: Settings → Developer settings → Personal access tokens
2. Usa il token come password quando Git lo richiede
3. Oppure configura Git credential helper:
   ```bash
   git config --global credential.helper osxkeychain  # macOS
   ```

**Opzione 2: Usa SSH**
```bash
# Cambia remote a SSH
git remote set-url origin git@github.com:crmshop/crm-shops.git
```

## Verificare repository

Visita il repository su GitHub:
https://github.com/crmshop/crm-shops

## Setup rapido con script

Puoi usare lo script automatico incluso:

```bash
./setup_github.sh
```

Lo script ti guiderà attraverso:
- Verifica installazione GitHub CLI
- Autenticazione (se necessario)
- Creazione repository
- Push del codice

## Verifica

Dopo il push, visita il tuo repository su GitHub per verificare che tutti i file siano presenti:

```bash
gh repo view --web
```

## Prossimi passi

Dopo aver configurato GitHub, puoi:
- Continuare con lo sviluppo locale
- Configurare CI/CD con GitHub Actions (opzionale)
- Preparare il deploy su Render (Task 17-18)

## Note importanti

- ⚠️ **NON committare mai** il file `.env` (contiene credenziali sensibili)
- ✅ Il file `.gitignore` è già configurato per escludere file sensibili
- 🔒 Mantieni le tue credenziali segrete

