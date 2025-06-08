import json
import os
import paramiko
from datetime import datetime

def handle(event, context):
    """
    Fonction status-checker
    - Accessible via HTTP
    - Se connecte au SFTP et compte les fichiers dans /USX/depot
    - Retourne l'état d'avancement du traitement
    """
    
    # Récupération des variables d'environnement
    user_id = os.getenv('USER_ID', 'US3')
    sftp_host = os.getenv('SFTP_HOST')
    sftp_user = os.getenv('SFTP_USER')
    sftp_pass = os.getenv('SFTP_PASS')
    
    # Chemin du répertoire depot
    depot_path = f"/{user_id}/depot"
    
    try:
        # Connexion SFTP
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sftp_host, username=sftp_user, password=sftp_pass)
        sftp = ssh.open_sftp()
        
        # Listage des fichiers dans le répertoire depot
        try:
            files = sftp.listdir(depot_path)
            file_count = len(files)
            
            # Filtrage pour ne compter que les fichiers (pas les dossiers)
            actual_files = []
            for file in files:
                try:
                    file_path = f"{depot_path}/{file}"
                    stat = sftp.stat(file_path)
                    # Vérifier que c'est un fichier et non un dossier
                    if not stat.st_mode & 0o040000:  # S_IFDIR
                        actual_files.append({
                            "name": file,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                except:
                    # En cas d'erreur sur un fichier spécifique, on l'ignore
                    pass
            
        except FileNotFoundError:
            # Le répertoire depot n'existe pas encore
            actual_files = []
            file_count = 0
        
        # Nettoyage
        sftp.close()
        ssh.close()
        
        return json.dumps({
            "status": "success",
            "user_id": user_id,
            "depot_path": depot_path,
            "file_count": len(actual_files),
            "files": actual_files,
            "check_timestamp": datetime.now().isoformat(),
            "message": f"Found {len(actual_files)} files in depot directory"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to check status: {str(e)}",
            "user_id": user_id,
            "depot_path": depot_path,
            "check_timestamp": datetime.now().isoformat()
        })
