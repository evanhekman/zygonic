**Prerequisites:**  Node.js

### run web app
npm install
npm run dev

### run server
setup .env file
pip install -r requirements.txt
python server/server.py

### run db
docker compose -f db/docker-compose.yml up -d
python db/setup_db.py
python db/test_db.py
