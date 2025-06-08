import json
import os
import csv
import io
import paramiko
from datetime import datetime

def handle(event, context):
    """
    Fonction file-transformer
    - Déclenchée par un message sur le topic 'orders.import'
    - Se connecte au SFTP dans /USX/data, lit input.csv
    - Applique les transformations métier
    - Sauvegarde dans /USX/depot/output.csv
    """
    
    # Récupération des variables d'environnement
    user_id = os.getenv('USER_ID', 'US3')
    sftp_host = os.getenv('SFTP_HOST')
    sftp_user = os.getenv('SFTP_USER')
    sftp_pass = os.getenv('SFTP_PASS')
    
    # Chemins SFTP
    input_path = f"/{user_id}/data/input.csv"
    output_path = f"/{user_id}/depot/output.csv"
    
    try:
        # Connexion SFTP
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sftp_host, username=sftp_user, password=sftp_pass)
        sftp = ssh.open_sftp()
        
        # Lecture du fichier input.csv - FIX: ouvrir en mode binaire puis décoder
        with sftp.open(input_path, 'rb') as file:
            csv_bytes = file.read()
            csv_content = csv_bytes.decode('utf-8')
        
        # Traitement du CSV
        input_data = csv_content.splitlines()
        reader = csv.DictReader(input_data)
        
        # Préparation des données transformées
        processed_rows = []
        process_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for row in reader:
            # Transformations métier selon les spécifications
            transformed_row = {}
            
            # Copie des colonnes existantes avec transformations
            for key, value in row.items():
                if key.lower() == 'customers':
                    # upperCase pour la colonne customers
                    transformed_row[key] = value.upper() if value else ''
                elif key.lower() == 'product':
                    # lowerCase pour la colonne product
                    transformed_row[key] = value.lower() if value else ''
                else:
                    # Autres colonnes inchangées
                    transformed_row[key] = value if value else ''
            
            # Ajout des nouvelles colonnes
            transformed_row['Processed-Date'] = process_datetime
            transformed_row['process_by'] = user_id
            
            processed_rows.append(transformed_row)
        
        # Création du fichier CSV de sortie
        if processed_rows:
            output_buffer = io.StringIO()
            fieldnames = processed_rows[0].keys()
            writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
            
            # Sauvegarde sur SFTP - FIX: encoder en bytes pour l'écriture
            output_content = output_buffer.getvalue()
            with sftp.open(output_path, 'wb') as output_file:
                output_file.write(output_content.encode('utf-8'))
        
        # Nettoyage
        sftp.close()
        ssh.close()
        
        return json.dumps({
            "status": "success",
            "message": f"File processed successfully: {len(processed_rows)} rows transformed",
            "input_file": input_path,
            "output_file": output_path,
            "processed_by": user_id,
            "processed_date": process_datetime,
            "rows_processed": len(processed_rows)
        })
        
    except FileNotFoundError:
        return json.dumps({
            "status": "error",
            "message": f"Input file not found: {input_path}",
            "user_id": user_id
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Processing failed: {str(e)}",
            "user_id": user_id
        })