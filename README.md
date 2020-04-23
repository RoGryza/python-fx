# python-fx

Dummy FX REST API and website made with Python, Svelte and fixer.io.

## Quickstart

You can run the application in development mode with docker-compose:

```shellsession
$ docker-compose up
```

The website is then accessible at `localhost:8000`. Note that by default the database won't persist on restarts.

### Configuration

By default the application stores persistent data in the SQLite file ./fx.db (though the volume is not persisted in docker-compose.yaml) and a dummy API with fixed exchange rates is used instead of fixer.io.

You can change the database through the environment variable `FX_DATABASE`, which is SQLAlchemy database URL. If you want to use postgres or MySQL, you'll need to install their respective dependencies: `asyncpg` and `aiomysql`.

You need to set the environment variable `FX_FIXER_TOKEN` to your API key in order to get live exchange rates (see https://fixer.io/documentation).

### Backend

The backend is a REST server implemented with [FastAPI](https://fastapi.tiangolo.com/).

You need [poetry](https://github.com/python-poetry/poetry) to manage the project environment. You can run the backend locally with:

```shellssession
$ poetry install
$ poetry run uvicorn fx:app --reload
```

### Frontend

The frontend is implemented under the `webapp` directory. You'll need npm or yarn to manage dependencies and building the project.

The web application is written using the [Svelte](https://svelte.dev/) framework. You can get a live-reloading development version running with `npm run dev` or `yarn run dev`.

Static files for production can be built with `yarn build`, the result is built under the `public` directory.
