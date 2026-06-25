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

from django.core.management.base import BaseCommand

from core.models import (Bestemming, BlogArtikel, Expert, Faq, Feestdag, Land,
                         Plaats, Page, Reisweek, SectieTekst, SiteSettings, WeerMaand)

MAAND_NR = {"jan": 1, "feb": 2, "mrt": 3, "apr": 4, "mei": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}


def _parse_nl_date(s, jaar=2026):
    """'14 feb' -> date; geeft (start, eind) terug, eind=None tenzij een reeks
    zoals '15–17 feb' of '19 sep – 4 okt'."""
    s = s.replace("–", "-").replace(", ", "-")
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
        "intro": "Nederland kent vijf schoolvakanties per jaar, gespreid over drie regio's, Noord, Midden en Zuid, om de drukte op de wegen en in vakantiegebieden te verdelen. De meivakantie, zomervakantie en kerstvakantie staan wettelijk vast; de voorjaars- en herfstvakantie zijn adviesdata waar scholen van mogen afwijken.",
        "regio_info": "De spreiding over Noord, Midden en Zuid is in de jaren '80 ingevoerd om de drukte op de wegen en in vakantiegebieden te verminderen. Vooral de zomervakantie is daardoor regionaal verschillend.",
        "studiedagen_uitleg": "Naast de landelijke vakanties plannen scholen zelf studiedagen (margedagen): roostervrije dagen voor leerlingen waarop het team werkt. Deze verschillen per school en staan in de schoolgids. Gemiddeld 4–7 per schooljaar.",
        "weer_bron": "Langjarig gemiddelde · KNMI (De Bilt)",
        "weer_beste": "Mei, juni en september: zacht, relatief droog en buiten de drukste weken.",
        "bron": "Bron: Rijksoverheid (ministerie van OCW). Verplichte data staan vast; adviesdata kunnen per school verschillen, raadpleeg de schoolgids.",
        "bijgewerkt": "mei 2026",
    },
    "DE": {
        "intro": "Duitsland heeft geen landelijke schoolvakanties: elk van de 16 deelstaten (Bundesländer) bepaalt zijn eigen data. Alleen de zomervakantie wordt door de Kultusministerkonferenz gespreid (het 'Ferienkorridor') om files te voorkomen. Daardoor is het hele land vrijwel nooit tegelijk vrij.",
        "regio_info": "Duitsland kent geen provincie-indeling zoals Nederland: elk van de 16 deelstaten plant zelf. Alleen de zomervakantie wordt centraal gespreid. Voor Nederlandse reizigers zijn vooral Niedersachsen en Nordrhein-Westfalen relevant, die grenzen direct aan ons land.",
        "studiedagen_uitleg": "Deelstaten geven scholen 'bewegliche Ferientage': losse roostervrije dagen die de school zelf inplant, vaak brugdagen of rond Fasching/Karneval. Maximaal 6 per schooljaar.",
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
        "intro": "Frankrijk verdeelt de schoolvakanties over drie zones (A, B en C) om de drukte te spreiden, vooral rond de wintersport en de zomer goed merkbaar.",
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
     "De meivakantie, zomervakantie en kerstvakantie zijn wettelijk verplicht, daar mag geen enkele school van afwijken. De voorjaars- en herfstvakantie zijn adviesdata: scholen mogen hier, met instemming van de medezeggenschapsraad, van afwijken. Check altijd de schoolgids voor de definitieve data."),
    ("Waarom zijn de vakanties verdeeld over drie regio's?",
     "De spreiding over Noord, Midden en Zuid is in de jaren '80 ingevoerd om de drukte op de wegen en in vakantiegebieden te verminderen. Vooral de zomervakantie is daardoor regionaal verschillend; de andere vakanties volgen meestal het landelijke advies."),
    ("Wat is het verschil tussen de krokus- en carnavalsvakantie?",
     "Dat is dezelfde voorjaarsvakantie. In het zuiden van het land valt deze vaak rond carnaval en wordt hij carnavalsvakantie genoemd; elders heet hij krokusvakantie."),
    ("Wanneer is het het rustigst om met de kinderen weg te gaan?",
     "Net buiten de piek. Begin juli en eind augustus tot half september zijn duidelijk rustiger en goedkoper dan de drukke weken eind juli en begin augustus, wanneer alle regio's én veel buurlanden tegelijk vrij zijn."),
    ("Mag ik buiten de schoolvakanties op vakantie?",
     "Alleen in uitzonderlijke gevallen en met toestemming van de school. Zomaar eerder vertrekken valt onder ongeoorloofd schoolverzuim en kan een boete opleveren. Plan dus binnen de vakanties, of kies een slimme, rustige week erbinnen."),
]

LAND_FAQ = {
    "NL": FAQ_HOME,
    "DE": [
        ("Waarom heeft Duitsland 16 verschillende schoolvakanties?",
         "Elke deelstaat (Bundesland) bepaalt zijn eigen vakantiedata. Alleen de zomervakantie wordt door de Kultusministerkonferenz gecoördineerd en gespreid, zodat niet heel Duitsland tegelijk de weg op gaat."),
        ("Welke deelstaten grenzen aan Nederland?",
         "Niedersachsen (Nedersaksen) en Nordrhein-Westfalen (NRW) grenzen direct aan Nederland. NRW is met ruim 18 miljoen inwoners de dichtstbevolkte deelstaat, als die vakantie heeft, merk je dat aan de drukte."),
        ("Wanneer heeft heel Duitsland tegelijk vakantie?",
         "Rond 3 tot 5 augustus 2026 overlappen voor het eerst alle 16 deelstaten: dan is het in heel Duitsland zomervakantie. Dat is een landelijk verkeershoogtepunt."),
        ("Wat zijn 'bewegliche Ferientage'?",
         "Losse, roostervrije dagen die scholen zelf mogen inplannen, maximaal zes per schooljaar. Vaak voor brugdagen of Fasching/Karneval (Rosenmontag). Ze verschillen per school."),
        ("Hoe vermijd ik de drukte in Duitsland?",
         "Reis in een week waarin de grote, dichtbevolkte deelstaten (NRW, Beieren, Baden-Württemberg) nog naar school gaan, of juist net voor of na hun vakantie. Begin juli en half september zijn vaak het rustigst."),
    ],
}



# ── Redactie / experts (Travel Nerds-team) ──────────────────────────────────
# (naam, initialen, functie, korte functie, sinds, bio, credentials, focus/tags)
EXPERTS = [
    ("Jorrit Drenth", "JD", "Mede-eigenaar Travel Nerds", "Operatie", None,
     "Mede-eigenaar van Travel Nerds B.V. in Nijmegen, het bedrijf achter o.a. "
     "Vliegtickets.com, Vakantiewoningen.nl en Cruises.nl. Jorrit is verantwoordelijk "
     "voor de dagelijkse operatie en bewaakt de juistheid en kwaliteit van de vakantie- "
     "en feestdagdata op Schoolvakanties.nl.",
     ["Mede-eigenaar Travel Nerds B.V.", "Verantwoordelijk voor operatie & datakwaliteit"],
     "Operatie, Kwaliteit"),
    ("Robin van den Bosch", "RvdB", "Mede-eigenaar Travel Nerds", "Strategie", None,
     "Mede-eigenaar van Travel Nerds B.V. in Nijmegen, het bedrijf achter o.a. "
     "Vliegtickets.com, Vakantiewoningen.nl en Cruises.nl. Robin richt zich op de "
     "strategie en productontwikkeling en vertaalt de reismarkt naar praktische "
     "plantools voor gezinnen.",
     ["Mede-eigenaar Travel Nerds B.V.",
      "Achter Vliegtickets.com, Vakantiewoningen.nl & Cruises.nl"],
     "Strategie, Product"),
]

# Vaste (gecommitte) expertfoto's in static/. Worden alleen als fallback gezet:
# een upload of handmatige URL in de admin heeft altijd voorrang.
EXPERT_FOTOS = {
    "Jorrit Drenth": "/static/img/experts/jorrit.jpg",
}


# ── Bewerkbare paginacopy (SectieTekst) ─────────────────────────────────────
# (pagina, sleutel, omschrijving, tekst). De template toont deze tekst via
# {% stekst pagina sleutel %}; in de admin (Sectieteksten) kan de redactie 'm
# aanpassen. Niet-klobberend: een herhaalde seed overschrijft geen admin-edits.
SECTIES = [
    ("home", "hero_eye", "Home, hero bovenkop", "Slimme reisplanner voor gezinnen"),
    ("home", "hero_lead", "Home, hero intro",
     "Kies je bestemming en maand, wij tonen meteen de slimste weken om met de kinderen op pad te gaan. Drukte, prijs, weer en schoolvakanties, in één score."),
    ("over_ons", "hero_kop", "Over ons, titel", "De mensen achter Schoolvakanties.nl"),
    ("over_ons", "hero_lead", "Over ons, intro",
     "Sinds 2009 helpen we Nederlandse gezinnen om slim weg te gaan. Geen overgenomen lijstjes, maar officiële data, een vaste redactie en een drukte-model dat we zelf bouwden en onderhouden."),
    ("over_ons", "missie_kop", "Over ons, missie-kop", "Vakantieplannen zonder gedoe, en zonder verrassingen"),
    ("over_ons", "missie_tekst", "Over ons, missie-tekst",
     "Schoolvakanties verschillen per regio, per land en per jaar. Dat maakt plannen lastig en drukte onvoorspelbaar. Wij brengen alle officiële data samen op één plek en vertalen die naar concreet advies: wanneer is het rustig, waar is het betaalbaar, en welke week past bij jouw gezin. Onafhankelijk, transparant en altijd herleidbaar naar de bron."),
    ("over_ons", "redactie_kop", "Over ons, redactie-kop", "Wie schrijft en controleert"),
    ("over_ons", "redactie_intro", "Over ons, redactie-intro",
     "Het team van Travel Nerds, het huis achter o.a. Vliegtickets.com, Vakantiewoningen.nl en Cruises.nl."),
    ("samenwerken", "hero_kop", "Samenwerken, titel", "Bereik gezinnen op het moment dat ze hun vakantie plannen"),
    ("samenwerken", "hero_lead", "Samenwerken, intro",
     "Schoolvakanties.nl is voor veel Nederlandse ouders het startpunt van elke reisplanning. Of je nu reisbureau, hotel, creator of merk bent, er is volop ruimte om samen te werken."),
    ("samenwerken", "contact_kop", "Samenwerken, contact-kop", "Laten we kennismaken"),
    ("samenwerken", "contact_tekst", "Samenwerken, contact-tekst",
     "Vertel kort wat je voor ogen hebt, dan denken we mee over de beste vorm. We reageren doorgaans binnen één werkdag."),
]


# ── Losse pagina's: privacy / cookies / voorwaarden ─────────────────────────
# Feitelijke teksten; de formele bedrijfsgegevens (KvK, adres) komen los uit de
# site-instellingen en worden in het template getoond, zodat ze op één plek staan.
LEGAL = {
    "privacy": {
        "heading": "Privacyverklaring",
        "intro": "Hoe Schoolvakanties.nl met je persoonsgegevens omgaat.",
        "body": """
<p>Schoolvakanties.nl respecteert je privacy en verwerkt persoonsgegevens in overeenstemming met de Algemene verordening gegevensbescherming (AVG). Hieronder lees je welke gegevens we verwerken, waarvoor en welke rechten je hebt.</p>
<h2>Welke gegevens we verwerken</h2>
<ul>
<li><strong>Contactformulier (samenwerken):</strong> je naam, eventueel je bedrijfsnaam, je e-mailadres en het bericht dat je achterlaat. Voor misbruikpreventie loggen we daarbij je IP-adres.</li>
<li><strong>E-mailcontact:</strong> als je ons mailt, bewaren we je bericht en e-mailadres om je te kunnen antwoorden.</li>
<li><strong>Technische gegevens:</strong> onze server houdt standaard logbestanden bij (zoals IP-adres en opgevraagde pagina) voor beveiliging en het oplossen van storingen.</li>
</ul>
<p>We vragen geen account aan, verwerken geen betaalgegevens en verkopen je gegevens nooit.</p>
<h2>Waarvoor en op welke grondslag</h2>
<ul>
<li>Het afhandelen van je aanvraag of vraag (grondslag: uitvoering van of aanloop naar een overeenkomst en ons gerechtvaardigd belang om te reageren).</li>
<li>De beveiliging en goede werking van de website (gerechtvaardigd belang).</li>
</ul>
<h2>Hoe lang we bewaren</h2>
<p>Aanvragen en e-mailcontact bewaren we niet langer dan nodig, in de regel maximaal 24 maanden na het laatste contact. Technische logbestanden bewaren we kort, doorgaans enkele weken.</p>
<h2>Delen met derden</h2>
<p>We delen gegevens alleen met dienstverleners die ons helpen de site te draaien, zoals onze hosting- en e-mailprovider, en uitsluitend voor zover dat nodig is. Met deze partijen zijn verwerkersafspraken gemaakt. We geven geen gegevens door buiten de Europese Economische Ruimte zonder passende waarborgen.</p>
<h2>Cookies</h2>
<p>Schoolvakanties.nl gebruikt alleen functionele en noodzakelijke cookies. Lees er meer over in onze <a href="/cookies/">cookieverklaring</a>.</p>
<h2>Externe data</h2>
<p>De vakantie- en feestdagdata op deze site komen uit officiële, openbare bronnen (zoals Rijksoverheid.nl, OpenHolidays en Nager.Date). Daarbij worden geen persoonsgegevens van jou uitgewisseld.</p>
<h2>Je rechten</h2>
<p>Je hebt het recht op inzage, correctie, verwijdering en beperking van je gegevens, en je kunt bezwaar maken tegen de verwerking. Stuur je verzoek naar het e-mailadres hieronder. Ben je het niet eens met hoe we met je gegevens omgaan, dan kun je een klacht indienen bij de Autoriteit Persoonsgegevens.</p>
<h2>Beveiliging</h2>
<p>We nemen passende technische en organisatorische maatregelen om je gegevens te beschermen, waaronder versleuteling van het dataverkeer via HTTPS.</p>
""",
    },
    "cookies": {
        "heading": "Cookieverklaring",
        "intro": "Welke cookies Schoolvakanties.nl gebruikt en waarom.",
        "body": """
<p>Schoolvakanties.nl gebruikt cookies zo beperkt mogelijk. We plaatsen alleen functionele en noodzakelijke cookies; daarvoor is geen toestemming vereist.</p>
<h2>Wat zijn cookies?</h2>
<p>Cookies zijn kleine tekstbestanden die bij een bezoek aan een website op je apparaat worden opgeslagen. Ze zorgen er bijvoorbeeld voor dat een website goed en veilig werkt.</p>
<h2>Welke cookies we gebruiken</h2>
<table>
<tr><th>Cookie</th><th>Doel</th><th>Bewaartermijn</th></tr>
<tr><td>sessionid</td><td>Noodzakelijk: houdt je sessie in stand (o.a. voor formulieren).</td><td>Sessie, max. 2 weken</td></tr>
<tr><td>csrftoken</td><td>Noodzakelijk: beveiligt formulieren tegen misbruik (CSRF).</td><td>1 jaar</td></tr>
</table>
<p>We gebruiken op dit moment geen tracking-, advertentie- of analytics-cookies die jou persoonlijk volgen. Mochten we in de toekomst analytische of marketingcookies willen plaatsen, dan vragen we daar vooraf je toestemming voor.</p>
<h2>Cookies beheren</h2>
<p>Je kunt cookies altijd zelf beheren of verwijderen via de instellingen van je browser. Het uitschakelen van noodzakelijke cookies kan ertoe leiden dat onderdelen van de site niet goed werken.</p>
""",
    },
    "voorwaarden": {
        "heading": "Gebruiksvoorwaarden",
        "intro": "De spelregels voor het gebruik van Schoolvakanties.nl.",
        "body": """
<p>Deze gebruiksvoorwaarden zijn van toepassing op het gebruik van de website Schoolvakanties.nl. Door de site te gebruiken ga je akkoord met deze voorwaarden.</p>
<h2>Doel van de website</h2>
<p>Schoolvakanties.nl is een informatieve website die schoolvakanties, feestdagen en reisdrukte in Nederland en Europa overzichtelijk samenbrengt en vertaalt naar plantips. De site verkoopt zelf geen reizen of producten.</p>
<h2>Juistheid van de informatie</h2>
<p>We stellen de vakantie- en feestdagdata met de grootste zorg samen op basis van officiële bronnen en controleren ze handmatig. Toch kunnen data wijzigen of onvolledig zijn. Aan de informatie op deze site kunnen geen rechten worden ontleend. Controleer voor je definitieve planning altijd de officiële bron, zoals de schoolgids of Rijksoverheid.nl.</p>
<h2>Intellectueel eigendom</h2>
<p>De teksten, vormgeving, het drukte-model en de overige inhoud op deze site zijn eigendom van de uitgever of haar licentiegevers. Overname zonder voorafgaande schriftelijke toestemming is niet toegestaan; kort citeren met bronvermelding en een link mag.</p>
<h2>Aansprakelijkheid</h2>
<p>Het gebruik van de site is voor eigen risico. Voor zover wettelijk toegestaan zijn we niet aansprakelijk voor schade die voortvloeit uit het gebruik van de site of uit onjuiste of onvolledige informatie.</p>
<h2>Links naar derden</h2>
<p>De site kan links bevatten naar websites van derden. We hebben geen invloed op de inhoud daarvan en zijn daar niet verantwoordelijk voor.</p>
<h2>Wijzigingen</h2>
<p>We kunnen deze voorwaarden van tijd tot tijd aanpassen. De actuele versie staat altijd op deze pagina.</p>
<h2>Toepasselijk recht</h2>
<p>Op deze voorwaarden is Nederlands recht van toepassing. Geschillen worden voorgelegd aan de bevoegde rechter in het arrondissement waar de uitgever is gevestigd.</p>
""",
    },
}


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
        self._seed_secties()
        self._seed_bedrijf()
        self._seed_legal()
        self._seed_nl_plaatsen()
        # De blog wordt NIET geseed: de echte artikelen komen uit de WordPress-
        # export via `manage.py import_wp_blog`. We kennen wel auteur + reviewer toe.
        self._seed_blog_redactie()
        self.stdout.write(self.style.SUCCESS("\nSeed klaar."))

    # Gecureerde basisset plaats -> regio (provincie-correct). De volledige lijst
    # met álle gemeenten (incl. de Gelderland-splitsing) vult `import_plaatsen`
    # op productie uit OpenHolidays; dit zorgt dat de zoekfunctie meteen werkt.
    NL_PLAATSEN = {
        "Noord": ["Groningen", "Leeuwarden", "Assen", "Emmen", "Zwolle", "Deventer",
                  "Enschede", "Hengelo", "Almelo", "Almere", "Lelystad", "Amsterdam",
                  "Haarlem", "Zaanstad", "Hilversum", "Alkmaar", "Den Helder", "Hoorn",
                  "Amstelveen", "Heerhugowaard", "Meppel", "Hoogeveen", "Hardenberg"],
        "Midden": ["Rotterdam", "Den Haag", "Leiden", "Delft", "Gouda", "Dordrecht",
                   "Zoetermeer", "Alphen aan den Rijn", "Utrecht", "Amersfoort",
                   "Nieuwegein", "Veenendaal", "Zeist", "Woerden", "Houten"],
        "Zuid": ["Middelburg", "Vlissingen", "Goes", "Terneuzen", "Eindhoven", "Tilburg",
                 "Breda", "'s-Hertogenbosch", "Den Bosch", "Helmond", "Roosendaal",
                 "Bergen op Zoom", "Oss", "Maastricht", "Venlo", "Roermond", "Heerlen",
                 "Sittard", "Weert", "Nijmegen"],
    }

    def _seed_nl_plaatsen(self):
        from core.models import Land
        nl = Land.objects.filter(iso_code="NL").first()
        if not nl:
            return
        n = 0
        for regio, plaatsen in self.NL_PLAATSEN.items():
            for naam in plaatsen:
                _, created = Plaats.objects.get_or_create(
                    land=nl, naam=naam, defaults={"regio": regio})
                n += int(created)
        self.stdout.write(f"NL plaatsen->regio: {n} toegevoegd "
                          f"({Plaats.objects.filter(land=nl).count()} totaal).")

    def _seed_bedrijf(self):
        """Bedrijfsgegevens (Travel Nerds B.V.) in de site-instellingen. Vult
        alleen lege velden, zodat handmatige wijzigingen blijven staan."""
        site = SiteSettings.load()
        defaults = {
            "bedrijfsnaam": "Travel Nerds B.V.",
            "kvk_nummer": "91114373",
            "vestigingsnummer": "000056802544",
            "adres_straat": "Hertogstraat 131",
            "adres_postcode": "6511 RZ",
            "adres_plaats": "Nijmegen",
            "phone": "085 060 0043",
            "email": "klantenservice@travelnerds.nl",
        }
        changed = []
        for veld, waarde in defaults.items():
            if not getattr(site, veld, ""):
                setattr(site, veld, waarde)
                changed.append(veld)
        if changed:
            site.save(update_fields=changed)
        self.stdout.write(f"Bedrijfsgegevens: {len(changed)} veld(en) ingevuld.")

    def _seed_legal(self):
        """Maak/­vul de losse pagina's (privacy/cookies/voorwaarden). Body alleen
        zetten als die nog leeg is, zodat admin-edits niet worden overschreven."""
        reviewer = Expert.objects.filter(active=True).order_by("order").first()
        n = 0
        for key, data in LEGAL.items():
            page, _ = Page.objects.get_or_create(
                key=key, defaults={"label": data["heading"], "path": f"/{key}/"})
            if not page.body_html:
                page.heading = page.heading or data["heading"]
                page.intro = page.intro or data["intro"]
                page.body_html = data["body"].strip()
                if not page.byline_date:
                    page.byline_date = "juni 2026"
                if reviewer and not page.reviewer_id:
                    page.reviewer = reviewer
                page.save()
                n += 1
        self.stdout.write(f"Losse pagina's: {n} gevuld.")

    def _seed_blog_redactie(self):
        """Verdeel auteur + reviewer over de experts voor de E-E-A-T byline.

        Deterministisch op slug (zodat re-runs stabiel zijn) en alleen voor
        artikelen zonder auteur, zodat handmatige toewijzingen in de admin
        blijven staan."""
        experts = list(Expert.objects.filter(active=True).order_by("order"))
        if len(experts) < 1:
            return
        n = 0
        artikelen = BlogArtikel.objects.filter(author__isnull=True).order_by("slug")
        for i, art in enumerate(artikelen):
            art.author = experts[i % len(experts)]
            art.reviewer = experts[(i + 1) % len(experts)]
            art.save(update_fields=["author", "reviewer"])
            n += 1
        self.stdout.write(f"Blog-redactie toegekend aan {n} artikel(en).")

    def _seed_secties(self):
        n = 0
        for i, (pagina, sleutel, naam, tekst) in enumerate(SECTIES):
            _, created = SectieTekst.objects.get_or_create(
                pagina=pagina, sleutel=sleutel,
                defaults={"naam": naam, "tekst": tekst, "order": i})
            n += int(created)
        self.stdout.write(f"Sectieteksten: {n} aangemaakt.")

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
        n = upd = 0
        for i, (naam, mono, rol, kort, sinds, bio, cred, focus) in enumerate(EXPERTS):
            obj, created = Expert.objects.get_or_create(
                name=naam,
                defaults={"mono": mono, "role": rol, "kort": kort, "sinds": sinds,
                          "bio": bio, "credentials": "\n".join(cred), "tags": focus,
                          "order": i, "active": True})
            if created:
                n += 1
            else:
                # Redactionele velden zijn seed-gestuurd: werk ze bij zodat de
                # feitelijke tekst altijd klopt (admin-edits aan bio kunnen later).
                obj.mono, obj.role, obj.kort = mono, rol, kort
                obj.bio = bio
                obj.credentials = "\n".join(cred)
                obj.tags = focus
                obj.save(update_fields=["mono", "role", "kort", "bio", "credentials", "tags"])
                upd += 1
            # Fallback-foto: alleen zetten als er nog geen foto is (upload/URL wint).
            foto = EXPERT_FOTOS.get(naam)
            if foto and not obj.photo_upload and not obj.photo_local and not obj.photo_url:
                obj.photo_url = foto
                obj.save(update_fields=["photo_url"])
        self.stdout.write(f"Experts: {n} aangemaakt, {upd} bijgewerkt.")
