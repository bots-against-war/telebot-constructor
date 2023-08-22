# telebot-constructor

Free & open-source Telegram bot constructor with no-code web UI, using as backend [telebot-components](https://github.com/bots-against-war/telebot-components).

## Development

### Dev setup

1. The project uses Poerty 1.5.1 (see [installation instruction](https://python-poetry.org/docs/master#installing-with-the-official-installer)). Using it,
   install Python package with the backend API code:

```bash
poetry install
```

<spoiler>
  Poetry details
  <details>
    - You might need to manually install dynamic versioning plugin (without it local build will
      always have version `0.0.0`):
      ```bash
      poetry self add poetry-dynamic-versioning-plugin
      ```
    - To create virtualenv inside the project’s root directory, use command
    `bash
    poetry config virtualenvs.in-project false --local
    `
  </details>
</spoiler>

2. Start backend/API application

```sh
export TELEBOT_CONSTRUCTOR_DEBUG=1
python run_polling.py
```

2. Frontend uses `npm` v16+, use it to install the dependencies and run the dev server for frontend

```bash
npm install
npm run dev
```

3. Visit `http://localhost:8081` in the browser.
