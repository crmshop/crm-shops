# Guida Setup GitHub con GitHub CLI

Questa guida ti aiuterà a configurare GitHub per il progetto CRM Shops usando GitHub CLI (`gh`).

## Prerequisiti

- GitHub CLI installato (`gh`)
- Account GitHub esistente o da creare

## Installazione GitHub CLI (se necessario)

Se non hai GitHub CLI installato:

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora
sudo dnf install gh
```

**Windows:**
```bash
# Con Chocolatey
choco install gh

# Con Scoop
scoop install gh
```

## Passi per configurare GitHub

### 1. Autenticarsi con GitHub CLI

1. Esegui il login:
   ```bash
   gh auth login
   ```

2. Segui le istruzioni interattive:
   - Scegli **GitHub.com**
   - Scegli **HTTPS** come protocollo
   - Scegli **Login with a web browser** (più semplice)
   - Autorizza GitHub CLI nel browser
   - Oppure usa **Paste an authentication token** se preferisci

3. Verifica l'autenticazione:
   ```bash
   gh auth status
   ```

### 2. Configurare Git locale (se non già fatto)

```bash
git config --global user.name "Il Tuo Nome"
git config --global user.email "tua-email@example.com"
```

### 3. Creare repository su GitHub

Nel terminale, nella directory del progetto:

```bash
cd /Users/mariofo/Python_projects/CRM_shops

# Crea repository pubblico
gh repo create crm-shops --public --description "Sistema CRM per negozi con AI generativa" --source=. --remote=origin --push

# OPPURE per repository privato
gh repo create crm-shops --private --description "Sistema CRM per negozi con AI generativa" --source=. --remote=origin --push
```

Questo comando:
- ✅ Crea il repository su GitHub
- ✅ Aggiunge il remote `origin`
- ✅ Fa il push del codice esistente

### 4. Verificare la configurazione

```bash
# Verifica remote
git remote -v

# Verifica stato
git status

# Apri repository su GitHub nel browser
gh repo view --web
```

### 5. (Alternativa) Se il repository esiste già

Se preferisci creare il repository manualmente e poi collegarlo:

```bash
# Crea repository su GitHub (senza push automatico)
gh repo create crm-shops --public --description "Sistema CRM per negozi con AI generativa"

# Aggiungi remote
git remote add origin https://github.com/TUO-USERNAME/crm-shops.git

# Fai commit e push
git add .
git commit -m "Initial commit: Setup progetto CRM Shops"
git branch -M main
git push -u origin main
```

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

