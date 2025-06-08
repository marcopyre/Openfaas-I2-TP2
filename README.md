# TP2 OpenFaaS - Chaîne de traitement de commandes DataRetailX

## Architecture

Ce projet implémente une chaîne de traitement automatisée de commandes pour DataRetailX en utilisant OpenFaaS sur Kubernetes.

### Fonctions développées

1. **daily-fetcher** : Fonction planifiée (CRON à 8h) qui déclenche le processus
2. **file-transformer** : Fonction déclenchée par NATS qui traite les fichiers CSV
3. **status-checker** : Fonction HTTP qui vérifie l'état du traitement

## Prérequis

- Minikube
- faas-cli installé
- Helm installé
- Accès SFTP configuré (credentials a modifier dans stack.yml)

## Structure du projet

```
├── daily-fetcher/
│   ├── handler.py
│   └── requirements.txt
├── file-transformer/
│   ├── handler.py
│   └── requirements.txt
├── status-checker/
│   ├── handler.py
│   └── requirements.txt
├── stack.yml
├── daily-fetcher-cronjob.yaml
├── deploy.sh
└── README.md
```

## Déploiement

```bash
chmod +x deploy.sh
./deploy.sh
```

# Screenshots:

![Screenshot of daily-fetcher](/screenshots/daily-fetcher.png)

![Screenshot of file-transformer](/screenshots/file-transformer.png)

![Screenshot of status-checker](/screenshots/status-checker.png)
