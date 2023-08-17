cd frontend
apt install curl
curl https://www.npmjs.com/install.sh | sh
curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash -
apt install nodejs
npm install
npm run build
cd ..