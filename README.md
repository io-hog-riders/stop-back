# stop

## praca w repo

Róbcie na branchu i dawajcie Pull Requesty
starajmy się nie pushować na maina (xd)

## struktura projektu (wip)

```bash
src/
    db/                     # rzeczy związane z bazą /
                            # modele naszych danych
        models/         
        connection.py       # połączenie z bazą, inicjalizacja
    routes/                 # RESTowy middleware
        plan/
            controller.py   # middleware dot. planowania trasy
        stops/
    services/               # logika biznesowa, ogólna funkcjonalność
        plan/               # obliczanie ścieżki
        stops/              # szukanie przystanków
    app.py                  # inicjalizacja fastapi
    main.py                 # entry point aplikacji
```
Nie bójcie się zmieniać rzeczy, ale trzymajmy się w miarę
tej struktury.

## specyfikacja API

Możecie otworzyć `openapi.yaml` w `editor.swagger.io`
albo w vscodzie z odpowiednia wtyczką. Trzymajmy się
jak możemy istniejącej specyfikacji, jeżeli musicie coś
zmienić to piszcie.

## przydatne linki:
    - https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.routing.add_edge_travel_times

## baza danych: PostgreSQL + SQLAlchemy

Model bazy jest zaimplementowany na podstawie `src/db/models/database.dbml`.

### 1) konfiguracja

Ustaw zmienna srodowiskowa `DATABASE_URL`, np.:

```bash
postgresql+psycopg://postgres:postgres@localhost:5432/stop
```

Jesli nie ustawisz, aplikacja sprobuje polaczyc sie z domyslnym adresem powyzej.

### 1a) uruchomienie PostgreSQL przez Docker

Najprostszy wariant to odpalic sam serwer bazy w kontenerze:

```bash
docker compose up -d postgres
```

To stworzy kontener z PostgreSQL 16, baze `stop`, uzytkownika `postgres` i zapis danych w wolumenie `postgres_data`.

### 2) jak to dziala

- Modele ORM: `src/db/models/entities.py`
- Polaczenie i sesja: `src/db/connection.py`
- Proste operacje na bazie: `src/db/repositories.py`

Przy starcie FastAPI (`src/main.py`) wywolywane jest `init_db()`, ktore tworzy tabele, jesli jeszcze nie istnieja.

### 3) uruchomienie

```bash
docker compose up -d postgres
uv sync
uv run uvicorn src.main:app --reload
```

### 4) szybki test

- Endpoint `GET /health/db` robi `SELECT 1` i potwierdza polaczenie z PostgreSQL.
