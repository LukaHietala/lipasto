Fast webview using pygit2 (lib2git) bindings. For my personal use, for now

<img width="1280" height="960" alt="image" src="https://github.com/user-attachments/assets/1ce40e5f-1eed-4085-a1b4-698aac9c557f" />

## Setup

1. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```
2. Create a git server: https://git-scm.com/book/en/v2/Git-on-the-Server-Setting-Up-the-Server
3. Set the `GIT_REPO_PATH` in .env to point to your git repositories dir
4. Create a systemd service to run the app (optional)
```ini
# /etc/systemd/system/lipasto.service
[Unit]
Description="mirrin lipasto"
After=network.target

[Service]
User=USERNAME
Group=www-data
SupplementaryGroups=GITUSERGROUP # optional
WorkingDirectory=/home/USERNAME/lipasto/
Environment="PATH=/home/USERNAME/lipasto/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/USERNAME/lipasto/.venv/bin/gunicorn --bind unix:lipasto.sock --workers=4 --log-level=debug -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```
5. Setup nginx or apache to serve the app (optional)
```nginx
# example nginx config
server {
   server_name git.mirrinlipasto.fi;
   location / {
      include proxy_params;
      proxy_pass http://unix:/home/USERNAME/lipasto/py-gitweb.sock;
   }
}
```

Note: Libgit2 might have some issues with git.safe dir settings. If you run into issues, try setting `git config --global --add safe.directory '*'`

<img width="1917" height="1043" alt="image" src="https://github.com/user-attachments/assets/15e9a5e9-41b7-424e-b0ef-19a4e09dfcaa" />
<img width="1917" height="1043" alt="image" src="https://github.com/user-attachments/assets/098ea60c-235a-4f9f-beb0-718b0e2c8b28" />
<img width="1917" height="1043" alt="image" src="https://github.com/user-attachments/assets/47b2bde4-fdbb-4bb5-a3e8-dae33ec1a0d8" />
<img width="1917" height="1043" alt="image" src="https://github.com/user-attachments/assets/8285fa07-f4de-4a7c-b93f-fe74fa46925c" />




