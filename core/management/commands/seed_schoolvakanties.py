"""
Seed de redactionele data die NIET uit de OpenHolidays API komt:
landintro's, weer-per-maand, officieuze feestdagen, bestemmingen, de
Reisweek-radar en de redactie (experts). Bron: de v3-designdata.

Idempotent en niet-klobberend: landteksten worden alleen ingevuld als ze leeg
zijn (zo overschrijft een herhaalde seed geen handmatige redactie); referentie-
data (weer, reisweken) wordt ge-upsert. Draai dit één keer na de eerste import:

    python manage.py import_openholidays
    python manage.py seed_schoolvakanties
"""
from __future__ import annotations

import datetime as dt
import sys

import html as _html

from django.core.management.base import BaseCommand

from core.models import (BlogArtikel, Bestemming, Expert, Faq, Feestdag, Land,
                         Reisweek, WeerMaand)

MAAND_NR = {"jan": 1, "feb": 2, "mrt": 3, "apr": 4, "mei": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}


def _parse_nl_date(s, jaar=2026):
    """'14 feb' -> date; geeft (start, eind) terug, eind=None tenzij een reeks
    zoals '15–17 feb' of '19 sep – 4 okt'."""
    s = s.replace("–", "-").replace("—", "-")
    parts = [p.strip() for p in s.split("-")]

    def one(token, fallback_month=None):
        bits = token.split()
        if len(bits) == 2:
            d, m = bits
            return dt.date(jaar, MAAND_NR[m[:3].lower()], int(d))
        if len(bits) == 1 and fallback_month:
            return dt.date(jaar, fallback_month, int(bits[0]))
        return None

    if len(parts) == 1:
        return one(parts[0]), None
    end = one(parts[1])
    start = one(parts[0], fallback_month=end.month if end else None)
    return start, end


# ── Redactionele landdata (uit landdata.js) ─────────────────────────────────
LAND_TEKST = {
    "NL": {
        "intro": "Nederland kent vijf schoolvakanties per jaar, gespreid over drie regio's — Noord, Midden en Zuid — om de drukte op de wegen en in vakantiegebieden te verdelen. De meivakantie, zomervakantie en kerstvakantie staan wettelijk vast; de voorjaars- en herfstvakantie zijn adviesdata waar scholen van mogen afwijken.",
        "regio_info": "De spreiding over Noord, Midden en Zuid is in de jaren '80 ingevoerd om de drukte op de wegen en in vakantiegebieden te verminderen. Vooral de zomervakantie is daardoor regionaal verschillend.",
        "studiedagen_uitleg": "Naast de landelijke vakanties plannen scholen zelf studiedagen (margedagen): roostervrije dagen voor leerlingen waarop het team werkt. Deze verschillen per school en staan in de schoolgids. Gemiddeld 4–7 per schooljaar.",
        "weer_bron": "Langjarig gemiddelde · KNMI (De Bilt)",
        "weer_beste": "Mei, juni en september: zacht, relatief droog en buiten de drukste weken.",
        "bron": "Bron: Rijksoverheid (ministerie van OCW). Verplichte data staan vast; adviesdata kunnen per school verschillen — raadpleeg de schoolgids.",
        "bijgewerkt": "mei 2026",
    },
    "DE": {
        "intro": "Duitsland heeft geen landelijke schoolvakanties: elk van de 16 deelstaten (Bundesländer) bepaalt zijn eigen data. Alleen de zomervakantie wordt door de Kultusministerkonferenz gespreid (het 'Ferienkorridor') om files te voorkomen. Daardoor is het hele land vrijwel nooit tegelijk vrij.",
        "regio_info": "Duitsland kent geen provincie-indeling zoals Nederland: elk van de 16 deelstaten plant zelf. Alleen de zomervakantie wordt centraal gespreid. Voor Nederlandse reizigers zijn vooral Niedersachsen en Nordrhein-Westfalen relevant — die grenzen direct aan ons land.",
        "studiedagen_uitleg": "Deelstaten geven scholen 'bewegliche Ferientage': losse roostervrije dagen die de school zelf inplant — vaak brugdagen of rond Fasching/Karneval. Maximaal 6 per schooljaar.",
        "weer_bron": "Langjarig gemiddelde · Deutscher Wetterdienst (landelijk)",
        "weer_beste": "Mei tot september voor zon; juli en augustus het warmst, maar ook het drukst en duurst.",
        "bron": "Bron: Kultusministerkonferenz (KMK) en de afzonderlijke deelstaten. Alle data onder voorbehoud (ohne Gewähr).",
        "bijgewerkt": "mei 2026",
    },
    "BE": {
        "intro": "België kent drie gemeenschappen (Vlaams, Franstalig en Duitstalig) die hun schoolvakanties grotendeels samen plannen. De data liggen dicht bij de Nederlandse.",
        "weer_bron": "Langjarig gemiddelde (indicatief)",
        "weer_beste": "Mei, juni en september: zacht en relatief droog, buiten de drukste weken.",
        "bron": "Bron: OpenHolidays API. Data onder voorbehoud; raadpleeg de schoolkalender.",
        "bijgewerkt": "juni 2026",
    },
    "FR": {
        "intro": "Frankrijk verdeelt de schoolvakanties over drie zones (A, B en C) om de drukte te spreiden — vooral rond de wintersport en de zomer goed merkbaar.",
        "weer_bron": "Langjarig gemiddelde (indicatief)",
        "weer_beste": "Mei, juni en september voor aangenaam weer zonder de hoogzomerdrukte.",
        "bron": "Bron: OpenHolidays API. Data onder voorbehoud; raadpleeg de schoolkalender.",
        "bijgewerkt": "juni 2026",
    },
    "ES": {
        "intro": "Spanje regelt schoolvakanties per autonome regio. Daardoor verschillen vooral de kerst- en zomerdata per regio.",
        "weer_bron": "Langjarig gemiddelde (indicatief)",
        "weer_beste": "Mei, juni en september: warm en zonnig, net buiten de snikhete piek.",
        "bron": "Bron: OpenHolidays API. Data onder voorbehoud; raadpleeg de schoolkalender.",
        "bijgewerkt": "juni 2026",
    },
    "IT": {
        "intro": "Italië stelt de schoolvakanties per regio vast, met landelijke feestdagen daaroverheen. De zomervakantie is lang: vaak juni tot half september.",
        "weer_bron": "Langjarig gemiddelde (indicatief)",
        "weer_beste": "Mei, juni en september: zomers weer en warmer zeewater, rustiger dan augustus.",
        "bron": "Bron: OpenHolidays API. Data onder voorbehoud; raadpleeg de schoolkalender.",
        "bijgewerkt": "juni 2026",
    },
    "AT": {
        "intro": "Oostenrijk plant de schoolvakanties per deelstaat (Bundesland), met een gespreide semestervakantie in februari.",
        "weer_bron": "Langjarig gemiddelde (indicatief)",
        "weer_beste": "Mei tot september voor wandelen en meren; juli en augustus het warmst.",
        "bron": "Bron: OpenHolidays API. Data onder voorbehoud; raadpleeg de schoolkalender.",
        "bijgewerkt": "juni 2026",
    },
    "PT": {
        "intro": "Portugal kent landelijke schoolvakanties met enkele regionale feestdagen. De Algarve is een populaire gezinsbestemming.",
        "weer_bron": "Langjarig gemiddelde (indicatief)",
        "weer_beste": "Mei, juni en september: veel zon, warme zee en lagere prijzen dan in hoogzomer.",
        "bron": "Bron: OpenHolidays API. Data onder voorbehoud; raadpleeg de schoolkalender.",
        "bijgewerkt": "juni 2026",
    },
    "CH": {
        "intro": "Zwitserland regelt de schoolvakanties per kanton; daardoor is het land zelden in z'n geheel tegelijk vrij.",
        "weer_bron": "Langjarig gemiddelde (indicatief)",
        "weer_beste": "Juni tot september voor bergen en meren; juli en augustus het warmst.",
        "bron": "Bron: OpenHolidays API. Data onder voorbehoud; raadpleeg de schoolkalender.",
        "bijgewerkt": "juni 2026",
    },
}

WEER = {
    "NL": [("jan", 6, 2, 12), ("feb", 7, 3, 10), ("mrt", 10, 4, 11), ("apr", 14, 6, 9),
           ("mei", 18, 7, 9), ("jun", 21, 7, 9), ("jul", 23, 7, 9), ("aug", 23, 6, 9),
           ("sep", 19, 5, 10), ("okt", 15, 4, 11), ("nov", 10, 2, 13), ("dec", 7, 1.5, 13)],
    "DE": [("jan", 4, 2, 11), ("feb", 5, 3, 9), ("mrt", 10, 4, 10), ("apr", 14, 6, 9),
           ("mei", 19, 7, 11), ("jun", 22, 8, 11), ("jul", 24, 8, 11), ("aug", 24, 7, 10),
           ("sep", 19, 5, 9), ("okt", 14, 4, 9), ("nov", 8, 2, 10), ("dec", 5, 2, 11)],
    "BE": [("jan", 6, 2, 12), ("feb", 7, 3, 10), ("mrt", 10, 4, 11), ("apr", 14, 5, 10),
           ("mei", 18, 6, 11), ("jun", 21, 7, 10), ("jul", 23, 7, 10), ("aug", 22, 6, 10),
           ("sep", 19, 5, 10), ("okt", 15, 4, 11), ("nov", 10, 2, 12), ("dec", 7, 2, 12)],
    "FR": [("jan", 7, 2, 10), ("feb", 8, 3, 9), ("mrt", 12, 5, 9), ("apr", 15, 6, 9),
           ("mei", 19, 7, 10), ("jun", 22, 8, 8), ("jul", 25, 9, 7), ("aug", 25, 8, 7),
           ("sep", 21, 6, 8), ("okt", 16, 4, 9), ("nov", 10, 3, 10), ("dec", 7, 2, 10)],
    "ES": [("jan", 10, 5, 5), ("feb", 12, 6, 5), ("mrt", 16, 6, 5), ("apr", 18, 7, 7),
           ("mei", 22, 9, 6), ("jun", 28, 11, 3), ("jul", 32, 12, 1), ("aug", 31, 11, 2),
           ("sep", 26, 9, 4), ("okt", 19, 6, 6), ("nov", 13, 5, 6), ("dec", 10, 4, 6)],
    "IT": [("jan", 12, 4, 7), ("feb", 13, 5, 7), ("mrt", 15, 6, 6), ("apr", 18, 7, 7),
           ("mei", 23, 8, 5), ("jun", 27, 10, 3), ("jul", 30, 11, 1), ("aug", 30, 10, 2),
           ("sep", 26, 8, 4), ("okt", 21, 6, 7), ("nov", 16, 4, 9), ("dec", 13, 4, 8)],
    "AT": [("jan", 2, 2, 8), ("feb", 4, 3, 7), ("mrt", 9, 4, 8), ("apr", 15, 6, 8),
           ("mei", 19, 7, 9), ("jun", 22, 8, 9), ("jul", 25, 8, 8), ("aug", 24, 7, 8),
           ("sep", 19, 5, 6), ("okt", 13, 4, 6), ("nov", 7, 2, 7), ("dec", 3, 1, 8)],
    "PT": [("jan", 12, 5, 9), ("feb", 13, 6, 7), ("mrt", 15, 7, 6), ("apr", 17, 8, 6),
           ("mei", 20, 9, 4), ("jun", 24, 11, 2), ("jul", 26, 12, 0), ("aug", 27, 12, 0),
           ("sep", 25, 9, 2), ("okt", 21, 7, 6), ("nov", 16, 5, 8), ("dec", 13, 5, 9)],
    "CH": [("jan", 2, 2, 9), ("feb", 4, 3, 8), ("mrt", 8, 4, 9), ("apr", 12, 5, 9),
           ("mei", 17, 6, 11), ("jun", 20, 7, 11), ("jul", 22, 8, 10), ("aug", 22, 7, 10),
           ("sep", 17, 6, 7), ("okt", 12, 4, 7), ("nov", 6, 2, 8), ("dec", 3, 2, 9)],
}

OFFICIEUS = {
    "NL": [("Valentijnsdag", "14 feb", "💌"), ("Carnaval", "15-17 feb", "🎭"),
           ("Moederdag", "10 mei", "💐"), ("Vaderdag", "21 jun", "👔"),
           ("Dierendag", "4 okt", "🐾"), ("Halloween", "31 okt", "🎃"),
           ("Sint-Maarten", "11 nov", "🏮"), ("Sinterklaas", "5 dec", "🎁"),
           ("Oudjaarsdag", "31 dec", "🎆")],
    "DE": [("Valentinstag", "14 feb", "❤️"), ("Rosenmontag", "16 feb", "🎭"),
           ("Muttertag", "10 mei", "💐"), ("Vatertag", "14 mei", "👔"),
           ("Halloween", "31 okt", "🎃"), ("Oktoberfest", "19 sep - 4 okt", "🍺"),
           ("Nikolaus", "6 dec", "🎅"), ("Silvester", "31 dec", "🎆")],
}

# ── Reisweek-radar (uit data.js) ────────────────────────────────────────────
WEEKS = [
    (19, "4 mei", 28, 34, 52, 18), (20, "11 mei", 30, 36, 58, 22), (21, "18 mei", 46, 52, 62, 40),
    (22, "25 mei", 38, 44, 66, 30), (23, "1 jun", 34, 40, 70, 26), (24, "8 jun", 36, 42, 74, 28),
    (25, "15 jun", 40, 46, 78, 34), (26, "22 jun", 48, 54, 80, 44), (27, "29 jun", 62, 66, 82, 60),
    (28, "6 jul", 74, 78, 84, 72), (29, "13 jul", 86, 88, 85, 84), (30, "20 jul", 92, 94, 86, 92),
    (31, "27 jul", 96, 97, 85, 96), (32, "3 aug", 90, 92, 84, 90), (33, "10 aug", 80, 84, 82, 78),
    (34, "17 aug", 64, 70, 78, 58), (35, "24 aug", 44, 50, 72, 36), (36, "31 aug", 30, 38, 66, 22),
    (37, "7 sep", 22, 30, 60, 14), (38, "14 sep", 24, 32, 56, 16),
]

# ── Bestemmingen (uit data.js) ──────────────────────────────────────────────
BESTEMMINGEN = [
    ("Toscane", "Italië", 84, 88, "Rustig in september"),
    ("Algarve", "Portugal", 79, 91, "Strand & zon"),
    ("Beierse Alpen", "Duitsland", 76, 85, "Korte reis"),
    ("Ardennen", "België", 81, 87, "Natuur dichtbij"),
    ("Costa Brava", "Spanje", 72, 84, "Familiestranden"),
    ("Zeeland", "Nederland", 86, 90, "Geen reistijd"),
]

# ── FAQ homepage (uit landdata.js, NL) ──────────────────────────────────────
FAQ_HOME = [
    ("Mag mijn school afwijken van deze vakantiedata?",
     "De meivakantie, zomervakantie en kerstvakantie zijn wettelijk verplicht — daar mag geen enkele school van afwijken. De voorjaars- en herfstvakantie zijn adviesdata: scholen mogen hier, met instemming van de medezeggenschapsraad, van afwijken. Check altijd de schoolgids voor de definitieve data."),
    ("Waarom zijn de vakanties verdeeld over drie regio's?",
     "De spreiding over Noord, Midden en Zuid is in de jaren '80 ingevoerd om de drukte op de wegen en in vakantiegebieden te verminderen. Vooral de zomervakantie is daardoor regionaal verschillend; de andere vakanties volgen meestal het landelijke advies."),
    ("Wat is het verschil tussen de krokus- en carnavalsvakantie?",
     "Dat is dezelfde voorjaarsvakantie. In het zuiden van het land valt deze vaak rond carnaval en wordt hij carnavalsvakantie genoemd; elders heet hij krokusvakantie."),
    ("Wanneer is het het rustigst om met de kinderen weg te gaan?",
     "Net buiten de piek. Begin juli en eind augustus tot half september zijn duidelijk rustiger en goedkoper dan de drukke weken eind juli en begin augustus, wanneer alle regio's én veel buurlanden tegelijk vrij zijn."),
    ("Mag ik buiten de schoolvakanties op vakantie?",
     "Alleen in uitzonderlijke gevallen en met toestemming van de school. Zomaar eerder vertrekken valt onder ongeoorloofd schoolverzuim en kan een boete opleveren. Plan dus binnen de vakanties — of kies een slimme, rustige week erbinnen."),
]

LAND_FAQ = {
    "NL": FAQ_HOME,
    "DE": [
        ("Waarom heeft Duitsland 16 verschillende schoolvakanties?",
         "Elke deelstaat (Bundesland) bepaalt zijn eigen vakantiedata. Alleen de zomervakantie wordt door de Kultusministerkonferenz gecoördineerd en gespreid, zodat niet heel Duitsland tegelijk de weg op gaat."),
        ("Welke deelstaten grenzen aan Nederland?",
         "Niedersachsen (Nedersaksen) en Nordrhein-Westfalen (NRW) grenzen direct aan Nederland. NRW is met ruim 18 miljoen inwoners de dichtstbevolkte deelstaat — als die vakantie heeft, merk je dat aan de drukte."),
        ("Wanneer heeft heel Duitsland tegelijk vakantie?",
         "Rond 3 tot 5 augustus 2026 overlappen voor het eerst alle 16 deelstaten: dan is het in heel Duitsland zomervakantie. Dat is een landelijk verkeershoogtepunt."),
        ("Wat zijn 'bewegliche Ferientage'?",
         "Losse, roostervrije dagen die scholen zelf mogen inplannen — maximaal zes per schooljaar. Vaak voor brugdagen of Fasching/Karneval (Rosenmontag). Ze verschillen per school."),
        ("Hoe vermijd ik de drukte in Duitsland?",
         "Reis in een week waarin de grote, dichtbevolkte deelstaten (NRW, Beieren, Baden-Württemberg) nog naar school gaan, of juist net voor of na hun vakantie. Begin juli en half september zijn vaak het rustigst."),
    ],
}

# ── Blog (uit blogdata.js) ──────────────────────────────────────────────────
# (slug, titel, categorie, excerpt, auteur, datum, leestijd, featured, toc, body-blocks)
BLOG_POSTS = [
    ("rustig-september", "Waarom september de slimste maand is voor gezinnen", "Slim plannen",
     "Zomers weer, halflege stranden en lagere prijzen — wie net na de drukte vertrekt, heeft de beste kaarten. We rekenen het voor.",
     "Sanne de Vries", "22 mei 2026", 6, True,
     ["De prijs zakt na week 34", "Het weer blijft zomers", "Rustiger voor kinderen", "Zo plan je het"],
     [("p", "De zomervakantie hoeft niet in juli of augustus. Sterker nog: de weken net erna zijn voor veel gezinnen aantoonbaar slimmer. Minder drukte, lagere prijzen en weer dat in Zuid-Europa nog volop zomers is."),
      ("h2", "De prijs zakt na week 34"),
      ("p", "Zodra de laatste regio's weer naar school gaan, dalen de prijzen van accommodaties en vluchten zichtbaar. In populaire gebieden scheelt dat al snel 25 tot 40 procent ten opzichte van de piekweken eind juli."),
      ("tip", "Vertrek een week ná de drukste week: vaak 30% rustiger én goedkoper, met nauwelijks minder mooi weer."),
      ("h2", "Het weer blijft zomers"),
      ("p", "Rond de Middellandse Zee liggen de temperaturen in september vaak nog tussen de 25 en 30 graden, terwijl het zeewater op zijn warmst is. Ideaal voor stranddagen zonder de verzengende hitte van hoogzomer."),
      ("quote", "We gingen voor het eerst in september. Half zoveel mensen, dezelfde zon — we doen het nooit meer anders."),
      ("h2", "Rustiger voor kinderen"),
      ("p", "Minder drukte betekent kortere wachtrijen, rustigere stranden en meer ruimte. Voor jonge kinderen scheelt dat een hoop prikkels — en dus een ontspannener vakantie voor iedereen."),
      ("list", ["Kortere rijen bij attracties en restaurants", "Meer keuze in accommodaties", "Rustiger verkeer onderweg", "Vriendelijker tarieven"]),
      ("h2", "Zo plan je het"),
      ("p", "Gebruik de Reisweek-radar om per week de Slim-score te vergelijken. Combineer dat met de druktekaart om te zien waar het op jouw reisweek het rustigst is. Binnen een paar klikken weet je wanneer én waar je het beste kunt zijn.")]),
    ("duitse-deelstaten", "Duitse deelstaten: zo gebruik je de gespreide vakanties", "Drukte & prijzen",
     "Duitsland is nooit in z'n geheel vrij. Slimme reizigers benutten dat — en ontwijken zo de files en hoge prijzen.",
     "Mark Jansen", "18 mei 2026", 5, False,
     ["Het Ferienkorridor", "Wanneer is het druk?", "De grensregio's", "Praktische tips"],
     [("p", "Anders dan Nederland kent Duitsland geen landelijke schoolvakanties. Elke deelstaat plant zelf, en alleen de zomervakantie wordt centraal gespreid. Dat maakt het land een paradijs voor wie drukte wil ontwijken."),
      ("h2", "Het Ferienkorridor"),
      ("p", "De zomervakanties rollen van eind juni (Hessen, Rheinland-Pfalz, Saarland) tot half september (Beieren) over het land. Daardoor is het nergens álle weken even druk."),
      ("tip", "Reis als de grote deelstaten NRW en Beieren nog op school zitten — dan zijn de Duitse snelwegen en bestemmingen merkbaar rustiger."),
      ("h2", "Wanneer is het druk?"),
      ("p", "Rond begin augustus overlappen vrijwel alle deelstaten. Dat is hét landelijke verkeershoogtepunt; vermijd dan de vrijdag- en zaterdagochtenden op de Autobahn."),
      ("h2", "De grensregio's"),
      ("p", "Voor Nederlandse reizigers zijn vooral Niedersachsen en Nordrhein-Westfalen relevant. Als die vrij zijn, merk je dat in de grensstreek en op de doorgaande routes naar het zuiden."),
      ("h2", "Praktische tips"),
      ("list", ["Check de deelstaat van je bestemming, niet alleen het land", "Plan reisdagen op een dinsdag of woensdag", "Kijk naar de overlap met de Nederlandse vakanties"])]),
    ("kinderen-onderweg", "Lange autorit met kinderen? 9 dingen die echt werken", "Met kinderen",
     "Van slimme stops tot het juiste vertrekmoment — zo blijft de reis naar het zuiden ontspannen.",
     "Lisa Bakker", "14 mei 2026", 7, False,
     ["Vertrek op het juiste moment", "Plan je stops", "Eten & ontspanning", "Onderweg rust houden"],
     [("p", "Een lange autorit hoeft geen beproeving te zijn. Met een beetje planning — en het juiste vertrekmoment — kom je een stuk relaxter aan."),
      ("h2", "Vertrek op het juiste moment"),
      ("p", "Vermijd de klassieke zwarte zaterdagen. Een vertrek midweek of heel vroeg in de ochtend scheelt vaak uren file."),
      ("tip", "Check vóór vertrek de drukte-tijdlijn van je bestemmingsland — zo weet je of je reisdag in een piekweek valt."),
      ("h2", "Plan je stops"),
      ("list", ["Elke twee uur een korte pauze", "Zoek speeltuinen langs de route", "Houd een verrassingstas met kleine spelletjes klaar"]),
      ("h2", "Eten & ontspanning"),
      ("p", "Neem voldoende water en gezonde snacks mee. Een goed gevulde koelbox voorkomt hangerige kinderen en dure tankstation-stops."),
      ("h2", "Onderweg rust houden"),
      ("quote", "Het geheim is niet sneller rijden, maar slimmer vertrekken.")]),
    ("algarve-gezin", "De Algarve met het gezin: zon, strand en rust", "Bestemmingen",
     "Portugals zuidkust scoort hoog op gezinsvriendelijkheid. We zetten de beste weken en plekken op een rij.",
     "Sanne de Vries", "9 mei 2026", 6, False,
     ["Waarom de Algarve?", "De beste reisweken", "Stranden voor kinderen", "Praktisch"],
     [("p", "Brede zandstranden, kalme baaitjes en betrouwbaar weer maken de Algarve tot een topbestemming voor gezinnen. De gezinsscore van 91 liegt er niet om."),
      ("h2", "Waarom de Algarve?"),
      ("p", "Korte vluchttijd, veel familievriendelijke accommodaties en een zee die in het naseizoen heerlijk op temperatuur is."),
      ("h2", "De beste reisweken"),
      ("tip", "Half september (week 38) combineert warm zeewater met rust en lagere prijzen — de hoogste Slim-score van het jaar."),
      ("h2", "Stranden voor kinderen"),
      ("list", ["Praia da Marinha — rustige baai", "Meia Praia — lange, brede zandvlakte", "Praia de Alvor — ondiep en veilig"]),
      ("h2", "Praktisch"),
      ("p", "Huur een auto voor flexibiliteit, en boek accommodatie net buiten de drukste badplaatsen voor meer rust en ruimte.")]),
    ("overlap-checken", "Vakantie-overlap: de verborgen oorzaak van hoge prijzen", "Drukte & prijzen",
     "Als meerdere landen tegelijk vrij zijn, schieten drukte én prijzen omhoog. Zo herken en ontwijk je het.",
     "Mark Jansen", "3 mei 2026", 4, False,
     ["Wat is overlap?", "Waarom het de prijs opdrijft", "Zo check je het"],
     [("p", "Het grootste prijsverschil zit niet in de bestemming, maar in het moment. En dat moment wordt bepaald door hoeveel landen tegelijk vakantie hebben."),
      ("h2", "Wat is overlap?"),
      ("p", "Overlap ontstaat als de schoolvakanties van bijvoorbeeld Nederland, Duitsland en Frankrijk in dezelfde weken vallen. Dan reist heel West-Europa tegelijk."),
      ("tip", "Een week met lage overlap is bijna altijd goedkoper én rustiger — ook al is het hetzelfde seizoen."),
      ("h2", "Waarom het de prijs opdrijft"),
      ("p", "Meer vraag, hetzelfde aanbod: accommodaties en vluchten worden duurder naarmate meer gezinnen tegelijk op pad willen."),
      ("h2", "Zo check je het"),
      ("p", "Gebruik de overlap-indicator op de landenpagina. Die toont per week hoe sterk de vakanties van buurlanden samenvallen — laag is beter.")]),
    ("zeeland-dichtbij", "Zeeland: de slimste vakantie zonder reistijd", "Bestemmingen",
     "Geen files, geen vliegtuig, wél zee en ruimte. Waarom dichtbij soms het slimste is.",
     "Lisa Bakker", "28 apr 2026", 5, False,
     ["Nul reistijd", "Wanneer het rustig is", "Voor elk gezin"],
     [("p", "De hoogste Slim-score van al onze bestemmingen gaat naar Zeeland. Geen reisdag, geen grensdrukte — gewoon instappen en er zijn."),
      ("h2", "Nul reistijd"),
      ("p", "Binnen twee uur sta je met je voeten in het zand. Dat scheelt een hele reisdag heen én terug, en dus minder stress voor de kinderen."),
      ("tip", "Buiten de Nederlandse schoolvakanties is Zeeland verrassend rustig — perfect voor een lang weekend in september."),
      ("h2", "Wanneer het rustig is"),
      ("p", "Vermijd de weken waarin alle drie de Nederlandse regio's tegelijk vrij zijn. Daarbuiten heb je het strand vaak bijna voor jezelf."),
      ("h2", "Voor elk gezin"),
      ("list", ["Ondiepe, veilige stranden", "Veel natuurcampings", "Fietsen zonder hoogteverschil"])]),
]


# Blogartikel-slug -> ISO-landcodes (voor het blogblok op de landenpagina).
BLOG_LAND = {
    "rustig-september": ["IT"],
    "duitse-deelstaten": ["DE"],
    "kinderen-onderweg": ["BE"],
    "algarve-gezin": ["PT"],
    "overlap-checken": ["ES", "NL", "DE"],
    "zeeland-dichtbij": ["NL"],
}


def _blocks_to_html(blocks):
    out = []
    for t, v in blocks:
        if t == "p":
            out.append(f"<p>{_html.escape(v)}</p>")
        elif t == "h2":
            out.append(f"<h2>{_html.escape(v)}</h2>")
        elif t == "tip":
            out.append(f'<div class="art-tip"><span class="art-tip-ic">💡</span><p>{_html.escape(v)}</p></div>')
        elif t == "quote":
            out.append(f"<blockquote>{_html.escape(v)}</blockquote>")
        elif t == "list":
            items = "".join(f"<li>{_html.escape(li)}</li>" for li in v)
            out.append(f'<ul class="art-list">{items}</ul>')
    return "\n".join(out)


# ── Redactie / experts (uit experts.js) ─────────────────────────────────────
EXPERTS = [
    ("Sanne de Vries", "SdV", "Hoofdredacteur & reisplanner", "Hoofdredacteur", 2012,
     "Reisjournalist met ruim veertien jaar ervaring in gezinsvakanties. Sanne bewaakt de redactionele lijn en controleert alle vakantie- en feestdagdata voordat ze online gaan.",
     ["14 jaar reisredactie", "Bezocht 30+ landen met kinderen", "Eindverantwoordelijk voor data-accuratesse"],
     "Redactie, Slim plannen"),
    ("Mark Jansen", "MJ", "Data- & drukte-analist", "Data-analist", 2015,
     "Bouwde het drukte- en Slim-score-model achter Schoolvakanties.nl. Mark combineert officiële vakantiekalenders met verkeers- en boekingsdata tot voorspelbare reisweken.",
     ["Ontwierp het Slim-score-model", "Werkt met OpenHolidays & KMK-bronnen", "Specialist Duitse deelstaten"],
     "Drukte & prijzen, Data"),
    ("Lisa Bakker", "LB", "Redacteur — reizen met kinderen", "Reisredacteur", 2018,
     "Moeder van drie en gepokt en gemazeld in lange autoritten naar het zuiden. Lisa schrijft de praktische gidsen en test bestemmingen op gezinsvriendelijkheid.",
     ["60+ gezinsreizen", "Specialist bestemmingen met kinderen", "Praktijktest van elke tip"],
     "Met kinderen, Bestemmingen"),
]


class Command(BaseCommand):
    help = "Seed de redactionele schoolvakanties-data (landintro's, weer, bestemmingen, radar, experts)."

    def handle(self, *args, **opts):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

        self._seed_landteksten()
        self._seed_weer()
        self._seed_officieus()
        self._seed_reisweken()
        self._seed_bestemmingen()
        self._seed_experts()
        self._seed_faq()
        # NB: de blog wordt NIET meer geseed. De echte artikelen komen uit de
        # WordPress-export via `manage.py import_wp_blog` (anders verschijnen de
        # oude demo-posts naast de echte). De BLOG_POSTS/BLOG_LAND-constanten
        # hierboven zijn bewust verouderd en ongebruikt (op te ruimen bij P2-cleanup).
        self.stdout.write(self.style.SUCCESS("\nSeed klaar."))

    def _seed_faq(self):
        n = 0
        for i, (vraag, antwoord) in enumerate(FAQ_HOME):
            _, created = Faq.objects.get_or_create(
                page_key="home", question=vraag,
                defaults={"answer": antwoord, "order": i, "active": True})
            n += int(created)
        for code, items in LAND_FAQ.items():
            for i, (vraag, antwoord) in enumerate(items):
                _, created = Faq.objects.get_or_create(
                    page_key=f"land-{code.lower()}", question=vraag,
                    defaults={"answer": antwoord, "order": i, "active": True})
                n += int(created)
        self.stdout.write(f"FAQ: {n} aangemaakt.")

    def _seed_landteksten(self):
        n = 0
        for code, velden in LAND_TEKST.items():
            land = Land.objects.filter(iso_code=code).first()
            if not land:
                continue
            changed = []
            for veld, waarde in velden.items():
                if not getattr(land, veld):  # alleen invullen als leeg (niet-klobberend)
                    setattr(land, veld, waarde)
                    changed.append(veld)
            if changed:
                land.save(update_fields=changed)
                n += 1
        self.stdout.write(f"Landteksten: {n} land(en) bijgewerkt.")

    def _seed_weer(self):
        n = 0
        for code, rows in WEER.items():
            land = Land.objects.filter(iso_code=code).first()
            if not land:
                continue
            for m, temp, zon, regen in rows:
                WeerMaand.objects.update_or_create(
                    land=land, maand=MAAND_NR[m],
                    defaults={"temp": temp, "zon": zon, "regen": regen})
                n += 1
        self.stdout.write(f"Weer: {n} maandrijen ge-upsert.")

    def _seed_officieus(self):
        n = 0
        for code, rows in OFFICIEUS.items():
            land = Land.objects.filter(iso_code=code).first()
            if not land:
                continue
            for naam, datum, emoji in rows:
                start, eind = _parse_nl_date(datum)
                _, created = Feestdag.objects.get_or_create(
                    land=land, naam=naam, categorie="officieus",
                    defaults={"start_datum": start, "eind_datum": eind, "emoji": emoji,
                              "landelijk": True, "bron": "handmatig"})
                n += int(created)
        self.stdout.write(f"Officieuze feestdagen: {n} aangemaakt.")

    def _seed_reisweken(self):
        for i, (wk, d1, drukte, prijs, weer, overlap) in enumerate(WEEKS):
            Reisweek.objects.update_or_create(
                jaar=2026, weeknr=wk,
                defaults={"start_label": d1, "drukte": drukte, "prijs": prijs,
                          "weer": weer, "overlap": overlap, "order": i})
        self.stdout.write(f"Reisweken: {len(WEEKS)} ge-upsert.")

    def _seed_bestemmingen(self):
        n = 0
        for i, (naam, land_naam, slim, gezin, tag) in enumerate(BESTEMMINGEN):
            land = Land.objects.filter(naam=land_naam).first()
            _, created = Bestemming.objects.get_or_create(
                naam=naam,
                defaults={"land": land, "land_naam": land_naam, "slim_score": slim,
                          "gezin_score": gezin, "tag": tag, "order": i})
            n += int(created)
        self.stdout.write(f"Bestemmingen: {n} aangemaakt.")

    def _seed_experts(self):
        n = 0
        for i, (naam, mono, rol, kort, sinds, bio, cred, focus) in enumerate(EXPERTS):
            _, created = Expert.objects.get_or_create(
                name=naam,
                defaults={"mono": mono, "role": rol, "kort": kort, "sinds": sinds,
                          "bio": bio, "credentials": "\n".join(cred), "tags": focus,
                          "order": i, "active": True})
            n += int(created)
        self.stdout.write(f"Experts: {n} aangemaakt.")
