### zygonic (2%)

### run web app
npm install
npm run dev

### run db
docker compose -f server/db/docker-compose.yml up -d
   add ~/users/ to Docker -> Preferences... -> Resources -> File Sharing. 
python server/db/cli.py setup
python db/test_db.py

### run server
setup .env file
pip install -r requirements.txt
python server/server.py

