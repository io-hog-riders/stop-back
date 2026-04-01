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
