# telebot-constructor

Free & open-source Telegram bot constructor with no-code web UI, using as backend [telebot-components](https://github.com/bots-against-war/telebot-components).

## Development

### Setup

1. The project requires Poerty 1.5.1 (see [installation instruction](https://python-poetry.org/docs/master#installing-with-the-official-installer))).

2. Then, to install the library with all dependencies, run from project root
   ```bash
   poetry install
   ```
   - You might need to manually install dynamic versioning plugin (without it local build will
     always have version `0.0.0`):
     ```bash
     poetry self add poetry-dynamic-versioning-plugin
     ```
   - To create virtualenv inside the project’s root directory, use command
     ```bash
     poetry config virtualenvs.in-project false --local
     ```


### Running in debug mode

```sh
export TELEBOT_CONSTRUCTOR_DEBUG=1
python run_polling.py
```
