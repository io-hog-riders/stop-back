# stop

## praca w repo

Róbcie na branchu i dawajcie Pull Requesty
starajmy się nie pushować na maina (xd)
Jak nazywacie brancha to mozecie dawać numer taska
ze Scruma

## jak odpalić lokalnie
```bash
cd src
uvicorn main:app
```
albo
```bash
fastapi src/main.py
```

## Jak odpalić serwer przez dockera
```
docker build -t 'stop-server'
docker run -p 3000:3000 'stop-server'
```

## struktura projektu (wip)

```bash
src/
    db/                     # rzeczy związane z bazą /
                            # modele naszych danych
        models/         
        connection.py       # połączenie z bazą, inicjalizacja
    routes/                 # RESTowy middleware
        plan/
            router.py       # router i middleware dot. planowania trasy
        stops/
    services/               # logika biznesowa, ogólna funkcjonalność
        plan/               # obliczanie ścieżki
            service.py
        stops/              # szukanie przystanków
            service.py
    app.py                  # inicjalizacja fastapi
    main.py                 # entry point aplikacji (odpalanie wszystkiego w dobrej kolejności)
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
