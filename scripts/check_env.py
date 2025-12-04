#!/usr/bin/env python3
"""
Script per verificare le variabili d'ambiente configurate
"""
import sys
from pathlib import Path

# Aggiungi il path del progetto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.env_loader import print_env_status

if __name__ == "__main__":
    print_env_status()




