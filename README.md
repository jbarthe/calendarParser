# Générateur de Planning de Congés

Cette application permet de générer un planning visuel (PDF) à partir d'un fichier Excel, CSV ou d'un Google Sheet.

## Installation

1. Assurez-vous d'avoir Python installé.
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Lancement

Lancez l'application avec Streamlit :
```bash
streamlit run app.py
```

## Utilisation

1. **Fichier Excel/CSV** : Téléversez votre fichier.
   - Le fichier doit contenir une colonne avec les noms.
   - Les autres colonnes doivent contenir les périodes au format : `Du DD/MM/YY au DD/MM/YY`.
2. **Google Sheets** : Collez le lien de votre Google Sheet.
   - Assurez-vous que le document est accessible (Public ou lien de partage).

Une fois les données chargées, cliquez sur le bouton de téléchargement pour obtenir votre PDF.
