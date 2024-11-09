# MySQL Database Sync Tool

A Python-based tool for synchronizing MySQL databases between remote and local environments. This utility creates a secure backup of a remote database and restores it to your local environment, making it ideal for development and testing purposes.

## Features

- Secure SSH-based remote connection
- Automated database dump creation
- Secure file transfer via SFTP
- Local database restoration
- Automatic cleanup of old backups
- Configuration via JSON file
- Support for database routines, events, and triggers

## Prerequisites

- Python 3.x
- MySQL/MariaDB installed on both remote and local machines
- SSH access to the remote server
- Required Python packages:
  ```
  paramiko
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mysql-sync-tool.git
   cd mysql-sync-tool
   ```

2. Install required packages:
   ```bash
   pip install paramiko
   ```

3. Create a configuration file `config.json`:
   ```json
   {
     "remote_host": "your.remote.server",
     "remote_user": "ssh_username",
     "remote_db": "remote_database_name",
     "remote_mysql_user": "remote_mysql_username",
     "remote_mysql_password": "remote_mysql_password",
     "local_mysql_user": "local_mysql_username",
     "local_mysql_password": "local_mysql_password",
     "local_db": "local_database_name",
     "ssh_key_path": "~/.ssh/id_rsa"
   }
   ```

## Usage

Run the script:
```bash
python mysql-sync-python.py
```

The tool will:
1. Connect to the remote server via SSH
2. Create a dump of the remote database
3. Download the dump file to your local machine
4. Restore the dump to your local database
5. Clean up old backup files (keeps last 5 by default)

## Configuration Options

| Parameter | Description |
|-----------|-------------|
| remote_host | Remote server hostname or IP |
| remote_user | SSH username for remote server |
| remote_db | Name of the database on remote server |
| remote_mysql_user | MySQL username on remote server |
| remote_mysql_password | MySQL password on remote server |
| local_mysql_user | Local MySQL username |
| local_mysql_password | Local MySQL password |
| local_db | Name of the local database |
| ssh_key_path | Path to SSH private key |

## Backup Management

- Backups are stored in the `database_backups` directory
- Files are named with timestamp: `dump_YYYYMMDD_HHMMSS.sql`
- By default, only the 5 most recent backups are kept
- Adjust `keep_last` parameter in `cleanup_old_backups()` to change retention

## Security Considerations

- SSH key authentication is used for secure remote access
- Database credentials are stored in a separate configuration file
- Remote dump files are automatically removed after transfer
- Add `config.json` to `.gitignore` to prevent credential exposure

## Error Handling

The tool includes comprehensive error handling for:
- SSH connection failures
- Database dump creation issues
- File transfer problems
- Local restoration errors
- Backup cleanup failures

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Paramiko](http://www.paramiko.org/) for SSH functionality
- Inspired by the need for efficient database synchronization in development environments

## Support

For support, please open an issue in the GitHub repository.