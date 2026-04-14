from db.models.common import Location, OpeningHours, OpeningTimes, Rating
from db.models.plan import RoutePlanResponse, Route
from db.models.stops import Stop, StopIdent, StopType

#trasa Warszawa -> Kraków z OSRM simplified
#https://router.project-osrm.org/route/v1/driving/21.0122,52.2297;19.9383,50.0614?overview=simplified&geometries=geojson
def create_route_plan() -> RoutePlanResponse:
    return RoutePlanResponse(
        route= Route(
            distance= 295589,
            duration= 12091,
            points=[
                Location(lat=52.229679, lng=21.012233),
                Location(lat=52.224995, lng=20.988588),
                Location(lat=52.128764, lng=20.989169),
                Location(lat=52.078468, lng=20.964524),
                Location(lat=52.011716, lng=20.880064),
                Location(lat=51.947489, lng=20.843389),
                Location(lat=51.864643, lng=20.85089),
                Location(lat=51.684438, lng=20.936511),
                Location(lat=51.58038, lng=21.002494),
                Location(lat=51.523977, lng=21.084556),
                Location(lat=51.44556, lng=21.034652),
                Location(lat=51.317273, lng=21.01567),
                Location(lat=51.237585, lng=20.874616),
                Location(lat=51.16533, lng=20.857565),
                Location(lat=51.141051, lng=20.832504),
                Location(lat=51.115487, lng=20.847438),
                Location(lat=51.011461, lng=20.81025),
                Location(lat=50.935457, lng=20.664386),
                Location(lat=50.895196, lng=20.531094),
                Location(lat=50.829275, lng=20.467667),
                Location(lat=50.806388, lng=20.485297),
                Location(lat=50.758604, lng=20.460699),
                Location(lat=50.744896, lng=20.41648),
                Location(lat=50.702278, lng=20.39947),
                Location(lat=50.685181, lng=20.357508),
                Location(lat=50.62898, lng=20.313866),
                Location(lat=50.622197, lng=20.283413),
                Location(lat=50.556068, lng=20.203066),
                Location(lat=50.429541, lng=20.185),
                Location(lat=50.33549, lng=20.045663),
                Location(lat=50.300051, lng=20.027461),
                Location(lat=50.23375, lng=20.012011),
                Location(lat=50.190479, lng=20.022142),
                Location(lat=50.173526, lng=20.057974),
                Location(lat=50.1134, lng=20.04487),
                Location(lat=50.1006, lng=20.031025),
                Location(lat=50.110828, lng=19.965636),
                Location(lat=50.061376, lng=19.938377),
            ],

        ),
        #stopy generowane przez Chat zeby były na trasie fajnie
        suggestedStops=[
            #restauracja Radom
            Stop(
                ident=StopIdent(
                    id="stop-rest-1",
                    type=StopType.restaurant,
                    name="Karczma Pod Sosnami",
                    location=Location(lat=51.4027, lng=21.1471),
                    address="ul. Leśna 12, 26-600 Radom"
                ),
                detourDistance=1200,
                detourTime=300,
                website="https://karczmapodsosnami.pl",
                openingHours=OpeningTimes(
                    monday=OpeningHours(opens="1000", closes="2200")
                ),
                rating=Rating(rate=5)
            ),
            #restauracja Radom v2 - omijamy
            Stop(
                ident=StopIdent(
                    id="stop-rest-2",
                    type=StopType.restaurant,
                    name="Bistro Sadków 24",
                    location=Location(lat=51.3890, lng=21.1695),
                    address="ul. Lubelska 158, 26-600 Radom"
                ),
                detourDistance=1800,
                detourTime=420,
                website="https://bistro-sadkow.pl",
                openingHours=OpeningTimes(
                    monday=OpeningHours(opens="0900", closes="2100")
                ),
                rating=Rating(rate=3)
            ),

            #Hotel Kielce
            Stop(
                ident=StopIdent(
                    id="stop-hotel-1",
                    type=StopType.hotel,
                    name="Hotel Świętokrzyski",
                    location=Location(lat=50.8661, lng=20.6286),
                    address="ul. Warszawska 87, 25-516 Kielce"
                ),
                detourDistance=2500,
                detourTime=600,
                website="https://hotel-swietokrzyski.pl",
                openingHours=None,
                rating=Rating(rate=4)
            ),

            #Stacja Kielce
            Stop(
                ident=StopIdent(
                    id="stop-fuel-1",
                    type=StopType.gas_station,
                    name="Orlen Kielce Zachód",
                    location=Location(lat=50.8703, lng=20.6035),
                    address="ul. Krakowska 45, 25-705 Kielce"
                ),
                detourDistance=800,
                detourTime=180,
                website="https://www.orlen.pl",
                openingHours=OpeningTimes(
                    monday=OpeningHours(opens="0000", closes="2359"),
                    tuesday=OpeningHours(opens="0000", closes="2359"),
                    wednesday=OpeningHours(opens="0000",closes="2359"),
                    thursday=OpeningHours(opens="0000", closes="2359"),
                    friday=OpeningHours(opens="0000", closes="2359"),
                    saturday=OpeningHours(opens="0000", closes="2359"),
                    sunday=OpeningHours(opens="0000", closes="2359"),

                ),
                rating=Rating(rate=4)
            )
        ]

    )

#Przejezdzamy przez 1,3,4
def update_route_plan() -> RoutePlanResponse:
    return RoutePlanResponse(
        route=Route(
            distance=300689,
            duration=12171,
            points=[
                Location(lat=52.229679, lng=21.012233),
                Location(lat=51.684438, lng=20.936511),
                Location(lat=51.523977, lng=21.084556),
                Location(lat=51.44556, lng=21.034652),

                Location(lat=51.4027, lng=21.1471),

                Location(lat=51.317273, lng=21.01567),
                Location(lat=51.237585, lng=20.874616),
                Location(lat=51.011461, lng=20.81025),
                Location(lat=50.935457, lng=20.664386),

                Location(lat=50.8661, lng=20.6286),

                Location(lat=50.8703, lng=20.6035),

                Location(lat=50.806388, lng=20.485297),
                Location(lat=50.744896, lng=20.41648),
                Location(lat=50.62898, lng=20.313866),
                Location(lat=50.429541, lng=20.185),
                Location(lat=50.190479, lng=20.022142),
                Location(lat=50.061376, lng=19.938377),
            ],
        ),
        suggestedStops=[
            # restauracja Radom
            Stop(
                ident=StopIdent(
                    id="stop-rest-1",
                    type=StopType.restaurant,
                    name="Karczma Pod Sosnami",
                    location=Location(lat=51.4027, lng=21.1471),
                    address="ul. Leśna 12, 26-600 Radom"
                ),
                detourDistance=1200,
                detourTime=300,
                website="https://karczmapodsosnami.pl",
                openingHours=OpeningTimes(
                    monday=OpeningHours(opens="1000", closes="2200")
                ),
                rating=Rating(rate=5)
            ),
            # restauracja Radom v2 - omijamy
            Stop(
                ident=StopIdent(
                    id="stop-rest-2",
                    type=StopType.restaurant,
                    name="Bistro Sadków 24",
                    location=Location(lat=51.3890, lng=21.1695),
                    address="ul. Lubelska 158, 26-600 Radom"
                ),
                detourDistance=1800,
                detourTime=420,
                website="https://bistro-sadkow.pl",
                openingHours=OpeningTimes(
                    monday=OpeningHours(opens="0900", closes="2100")
                ),
                rating=Rating(rate=3)
            ),

            # Hotel Kielce
            Stop(
                ident=StopIdent(
                    id="stop-hotel-1",
                    type=StopType.hotel,
                    name="Hotel Świętokrzyski",
                    location=Location(lat=50.8661, lng=20.6286),
                    address="ul. Warszawska 87, 25-516 Kielce"
                ),
                detourDistance=2500,
                detourTime=600,
                website="https://hotel-swietokrzyski.pl",
                openingHours=None,
                rating=Rating(rate=4)
            ),

            # Stacja Kielce
            Stop(
                ident=StopIdent(
                    id="stop-fuel-1",
                    type=StopType.gas_station,
                    name="Orlen Kielce Zachód",
                    location=Location(lat=50.8703, lng=20.6035),
                    address="ul. Krakowska 45, 25-705 Kielce"
                ),
                detourDistance=800,
                detourTime=180,
                website="https://www.orlen.pl",
                openingHours=OpeningTimes(
                    monday=OpeningHours(opens="0000", closes="2359"),
                    tuesday=OpeningHours(opens="0000", closes="2359"),
                    wednesday=OpeningHours(opens="0000", closes="2359"),
                    thursday=OpeningHours(opens="0000", closes="2359"),
                    friday=OpeningHours(opens="0000", closes="2359"),
                    saturday=OpeningHours(opens="0000", closes="2359"),
                    sunday=OpeningHours(opens="0000", closes="2359"),

                ),
                rating=Rating(rate=4)
            )
        ]
    )
