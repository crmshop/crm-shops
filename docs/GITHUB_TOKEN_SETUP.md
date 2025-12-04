# Configurazione GitHub Personal Access Token

## 📝 Passaggi per creare il token

1. **Vai su GitHub Settings:**
   - Apri: https://github.com/settings/tokens
   - Oppure: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Genera nuovo token:**
   - Clicca **"Generate new token"** → **"Generate new token (classic)"**

3. **Configura il token:**
   - **Note**: Dai un nome descrittivo (es: "CRM Shops Deploy")
   - **Expiration**: Scegli scadenza (consigliato: 90 giorni o No expiration)
   - **Select scopes**: Seleziona almeno:
     - ✅ **repo** (tutti i permessi) - necessario per push/pull

4. **Genera e copia:**
   - Clicca **"Generate token"**
   - ⚠️ **COPIA IL TOKEN SUBITO** - lo vedrai solo una volta!

## 🔧 Configurazione Git con token

### Metodo 1: Usa token come password (consigliato)

Quando fai `git push`, usa:
- **Username**: Il tuo username GitHub
- **Password**: Il token (NON la password GitHub!)

### Metodo 2: Salva token in Git credential helper

```bash
# Configura Git per salvare le credenziali
git config --global credential.helper osxkeychain  # macOS
# oppure
git config --global credential.helper store         # Linux/Windows

# Al primo push inserisci username e token
# Git lo salverà per i prossimi push
```

### Metodo 3: Usa token nell'URL (temporaneo)

```bash
git remote set-url origin https://TOKEN@github.com/crmshop/crm-shops.git
git push origin main
# Poi rimuovi il token dall'URL per sicurezza
git remote set-url origin https://github.com/crmshop/crm-shops.git
```

## ✅ Verifica configurazione

```bash
# Verifica remote configurato
git remote -v

# Prova push
git push origin main
```

## 🔒 Sicurezza

- ⚠️ **NON committare mai il token nel codice**
- ⚠️ **NON condividere il token pubblicamente**
- ✅ Usa variabili d'ambiente per CI/CD
- ✅ Rigenera il token se compromesso

## 🆘 Troubleshooting

### Errore: "Authentication failed"
- Verifica che il token abbia scope `repo`
- Controlla che il token non sia scaduto
- Verifica username corretto

### Errore: "Permission denied"
- Verifica di avere accesso al repository `crmshop/crm-shops`
- Controlla che il token abbia permessi di scrittura



