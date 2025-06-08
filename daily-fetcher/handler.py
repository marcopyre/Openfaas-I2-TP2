import json
import os
import requests
from datetime import datetime

def handle(event, context):
    """
    Fonction planifiée daily-fetcher
    - Déclenchée automatiquement tous les jours à 8h via CRON
    - Publie un message JSON sur le topic NATS 'orders.import'
    """
    
    user_id = os.getenv('USER_ID', 'US3')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Message à publier sur NATS
    message = {
        "date": current_date,
        "user_id": user_id,
        "action": "import_orders"
    }
    
    try:
        # Publication du message sur le topic NATS orders.import
        # Dans OpenFaaS, on utilise l'endpoint HTTP pour publier sur NATS
        nats_url = "http://gateway.openfaas:8080/async-function/file-transformer"
        
        response = requests.post(
            nats_url,
            json=message,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 202:
            return json.dumps({
                "status": "success",
                "message": f"Message published to orders.import topic",
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return json.dumps({
                "status": "error",
                "message": f"Failed to publish message: {response.status_code}",
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Exception occurred: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })