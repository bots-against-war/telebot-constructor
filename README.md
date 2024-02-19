# telebot-constructor

Free & open-source Telegram bot constructor with no-code web UI, using
[telebot-components](https://github.com/bots-against-war/telebot-components) as backend .

## Development

### Basic dev setup

1. [Install](https://python-poetry.org/docs/) Poetry (tested with versions 1.5 - 1.7). Then, install
   backend dependencies with

```bash
poetry install
```

2. Start backend/API

```sh
# activate virtual env created by poetry
poetry shell

# set environment variables (example for unix-like systems)
export TELEBOT_CONSTRUCTOR_USE_REDIS_EMULATION=1
export SECRETS_ENCRYPTION_KEY=if-wLoSw7gEbQgY1xLHrEgI4E357PRUAeGfZudnaYu0=  # dummy value

# run the web app
python run_polling.py
```

3. With `npm` v18+ install frontend and start dev server

```bash
npm install
npm run dev
```

4. Visit `http://localhost:8081` in the browser.

### Generate TS interfaces for backend data model

On any update to Pydantic data types on backend, run

```bash
npm run pydantic:to:ts
```

Check that [JSON schema](data/schema.json) and
[Typescript types](frontend/src/api/types.ts) are updated accordingly.

### Backend

#### Running tests with coverage check

```bash
coverage run -m pytest tests -vv
coverage html
```

Then you can review `htmlcov/index.html` in browser.

### Frontend

We use:
- Tailwind CSS
- `flowbite` component library, see [docs](https://flowbite-svelte.com/docs/pages/introduction)
- `svelvet` (nodes/connections engine), see [docs](https://svelvet.mintlify.app/introduction)
- `flowbite-icons-svelte` for icons, see [catalog](https://flowbite-svelte-icons.vercel.app/solid)
