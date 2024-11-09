#!/usr/bin/env python3
import subprocess
import paramiko
import os
from datetime import datetime
import sys
import json

class DatabaseSync:
    def __init__(self):
        # Remote server settings
        
        with open("config.json") as f:
            data = json.load(f)
           
        
        self.remote_host = data["remote_host"]
        self.remote_user = data["remote_user"]
        self.remote_db = data["remote_db"]
        self.remote_mysql_user = data["remote_mysql_user"]
        self.remote_mysql_password = data["remote_mysql_password"]
        
        # Local database settings
        self.local_mysql_user = data["local_mysql_user"]
        self.local_mysql_password = data["local_mysql_password"]
        self.local_db = data["local_db"]
        
        # SSH settings
        self.ssh_key_path = os.path.expanduser(data["ssh_key_path"])
        
        # Backup settings
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.local_backup_dir = "database_backups"
        self.remote_backup_dir = "/tmp/"  # Temporary directory on remote server
        self.dump_filename = f"dump_{self.timestamp}.sql"
        
        # Ensure local backup directory exists
        os.makedirs(self.local_backup_dir, exist_ok=True)

    def connect_ssh(self):
        """Establish SSH connection to remote server"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.remote_host,
                username=self.remote_user,
                key_filename=self.ssh_key_path
            )
            return ssh
        except Exception as e:
            print(f"Failed to connect to remote server: {str(e)}")
            sys.exit(1)

    def create_remote_dump(self, ssh):
        """Create database dump on remote server"""
        remote_dump_path = os.path.join(self.remote_backup_dir, self.dump_filename)
        try:
            # Create dump command
            dump_command = (
                f"mysqldump -u {self.remote_mysql_user} "
                f"-p{self.remote_mysql_password} "
                f"--routines "
                f"--events "
                f"--triggers "
                f"--add-drop-database "
                f"--add-drop-table "
                f"--databases "
                f"--create-options "
                f"--single-transaction "
                f"--set-gtid-purged=OFF "
                f"{self.remote_db} > {remote_dump_path}"
            )
            
            print(f"Creating dump on remote server in {remote_dump_path}...")
            stdin, stdout, stderr = ssh.exec_command(dump_command)
            
            # Wait for the command to complete
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error = stderr.read().decode()
                raise Exception(f"Remote dump failed: {error}")
            
            print("Remote dump created successfully")
            return remote_dump_path
            
        except Exception as e:
            print(f"Failed to create remote dump: {str(e)}")
            sys.exit(1)

    def download_dump(self, ssh, remote_path):
        """Download the dump file from remote to local machine"""
        local_path = os.path.join(self.local_backup_dir, self.dump_filename)
        try:
            # Create SFTP client
            sftp = ssh.open_sftp()
            
            print(f"Downloading dump from {remote_path} to {local_path}...")
            sftp.get(remote_path, local_path)
            
            # Remove remote dump file
            print("Removing remote dump file...")
            sftp.remove(remote_path)
            
            sftp.close()
            print("Dump file downloaded successfully")
            return local_path
            
        except Exception as e:
            print(f"Failed to download dump: {str(e)}")
            sys.exit(1)

    def restore_local_database(self, dump_path):
        """Restore the dump file to local database"""
        try:
            print(f"Restoring dump to local database {self.local_db}...")
            restore_command = [
                'mysql',
                f'-u{self.local_mysql_user}',
                f'-p{self.local_mysql_password}',
                self.local_db
            ]
            
            with open(dump_path, 'r') as dump_file:
                process = subprocess.Popen(
                    restore_command,
                    stdin=dump_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Restore failed: {stderr.decode()}")
                
            print("Local database restored successfully")
            
        except Exception as e:
            print(f"Failed to restore local database: {str(e)}")
            sys.exit(1)

    def cleanup_old_backups(self, keep_last=5):
        """Remove old backup files, keeping the specified number of recent ones"""
        try:
            files = sorted([
                os.path.join(self.local_backup_dir, f) 
                for f in os.listdir(self.local_backup_dir)
            ])
            
            # Remove old files
            for file in files[:-keep_last]:
                os.remove(file)
                print(f"Removed old backup: {file}")
                
        except Exception as e:
            print(f"Failed to cleanup old backups: {str(e)}")

    def sync_database(self):
        """Main method to perform the database synchronization"""
        print("Starting database synchronization...")
        
        # Connect to remote server
        ssh = self.connect_ssh()
        
        try:
            # Create dump on remote server
            remote_dump_path = self.create_remote_dump(ssh)
            
            # Download dump to local machine
            local_dump_path = self.download_dump(ssh, remote_dump_path)
            
            # Restore to local database
            self.restore_local_database(local_dump_path)
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            print("Database synchronization completed successfully!")
            
        finally:
            ssh.close()

if __name__ == "__main__":
    syncer = DatabaseSync()
    syncer.sync_database()
