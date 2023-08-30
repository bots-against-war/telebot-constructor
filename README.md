# telebot-constructor

Free & open-source Telegram bot constructor with no-code web UI, using as backend [telebot-components](https://github.com/bots-against-war/telebot-components).

## Development

### Dev setup

1. The project uses Poerty 1.5.1 (see [installation instruction](https://python-poetry.org/docs/master#installing-with-the-official-installer)). Using it,
   install Python package with the backend API code:

```bash
poetry install
```

<details>
  <summary>
    Poetry details
  </summary>
  <ul>
    <li>
      You might need to manually install dynamic versioning plugin (without it local build will
      always have version <code>0.0.0</code>): <code>poetry self add poetry-dynamic-versioning-plugin</code>
    </li>
    <li>
      To create virtualenv inside the project’s root directory, use: <code>poetry config virtualenvs.in-project false --local</code>
    </li>
  </ul>
</details>

2. Start backend/API application

```sh
export TELEBOT_CONSTRUCTOR_DEBUG=1
python run_polling.py
```

3. Frontend uses `npm` v16+, use it to install the dependencies and run the dev server for frontend

```bash
npm install
npm run dev
```

4. Visit `http://localhost:8081` in the browser.

### Generate TS interfaces for backend data model

Run from project root

```bash
python scripts/models/pydantic2jsonschema.py
node scripts/models/jsonschema2ts.mjs 
```
