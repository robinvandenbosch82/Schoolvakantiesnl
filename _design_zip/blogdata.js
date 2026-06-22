// blogdata.js — artikelen + content + widget-koppelingen voor de blog.

window.BLOG = (function () {
  const CATS = ["Slim plannen", "Bestemmingen", "Met kinderen", "Drukte & prijzen"];

  const posts = [
    {
      id: "rustig-september",
      titel: "Waarom september de slimste maand is voor gezinnen",
      cat: "Slim plannen",
      excerpt: "Zomers weer, halflege stranden en lagere prijzen — wie net na de drukte vertrekt, heeft de beste kaarten. We rekenen het voor.",
      auteur: "Sanne de Vries", datum: "22 mei 2026", leestijd: 6, img: "img/toscane.jpg",
      featured: true,
      bestemming: { naam: "Toscane", land: "Italië", slim: 84, gezin: 88, besteWeek: "wk 37 · 7 sep" },
      toc: ["De prijs zakt na week 34", "Het weer blijft zomers", "Rustiger voor kinderen", "Zo plan je het"],
      body: [
        { t: "p", v: "De zomervakantie hoeft niet in juli of augustus. Sterker nog: de weken net erna zijn voor veel gezinnen aantoonbaar slimmer. Minder drukte, lagere prijzen en weer dat in Zuid-Europa nog volop zomers is." },
        { t: "h2", v: "De prijs zakt na week 34" },
        { t: "p", v: "Zodra de laatste regio's weer naar school gaan, dalen de prijzen van accommodaties en vluchten zichtbaar. In populaire gebieden scheelt dat al snel 25 tot 40 procent ten opzichte van de piekweken eind juli." },
        { t: "tip", v: "Vertrek een week ná de drukste week: vaak 30% rustiger én goedkoper, met nauwelijks minder mooi weer." },
        { t: "h2", v: "Het weer blijft zomers" },
        { t: "p", v: "Rond de Middellandse Zee liggen de temperaturen in september vaak nog tussen de 25 en 30 graden, terwijl het zeewater op zijn warmst is. Ideaal voor stranddagen zonder de verzengende hitte van hoogzomer." },
        { t: "quote", v: "We gingen voor het eerst in september. Half zoveel mensen, dezelfde zon — we doen het nooit meer anders." },
        { t: "h2", v: "Rustiger voor kinderen" },
        { t: "p", v: "Minder drukte betekent kortere wachtrijen, rustigere stranden en meer ruimte. Voor jonge kinderen scheelt dat een hoop prikkels — en dus een ontspannener vakantie voor iedereen." },
        { t: "list", v: ["Kortere rijen bij attracties en restaurants", "Meer keuze in accommodaties", "Rustiger verkeer onderweg", "Vriendelijker tarieven"] },
        { t: "h2", v: "Zo plan je het" },
        { t: "p", v: "Gebruik de Reisweek-radar om per week de Slim-score te vergelijken. Combineer dat met de druktekaart om te zien waar het op jouw reisweek het rustigst is. Binnen een paar klikken weet je wanneer én waar je het beste kunt zijn." },
      ],
    },
    {
      id: "duitse-deelstaten",
      titel: "Duitse deelstaten: zo gebruik je de gespreide vakanties",
      cat: "Drukte & prijzen",
      excerpt: "Duitsland is nooit in z'n geheel vrij. Slimme reizigers benutten dat — en ontwijken zo de files en hoge prijzen.",
      auteur: "Mark Jansen", datum: "18 mei 2026", leestijd: 5, img: "img/beieren.jpg",
      bestemming: { naam: "Beierse Alpen", land: "Duitsland", slim: 76, gezin: 85, besteWeek: "wk 36 · 31 aug" },
      toc: ["Het Ferienkorridor", "Wanneer is het druk?", "De grensregio's", "Praktische tips"],
      body: [
        { t: "p", v: "Anders dan Nederland kent Duitsland geen landelijke schoolvakanties. Elke deelstaat plant zelf, en alleen de zomervakantie wordt centraal gespreid. Dat maakt het land een paradijs voor wie drukte wil ontwijken." },
        { t: "h2", v: "Het Ferienkorridor" },
        { t: "p", v: "De zomervakanties rollen van eind juni (Hessen, Rheinland-Pfalz, Saarland) tot half september (Beieren) over het land. Daardoor is het nergens álle weken even druk." },
        { t: "tip", v: "Reis als de grote deelstaten NRW en Beieren nog op school zitten — dan zijn de Duitse snelwegen en bestemmingen merkbaar rustiger." },
        { t: "h2", v: "Wanneer is het druk?" },
        { t: "p", v: "Rond begin augustus overlappen vrijwel alle deelstaten. Dat is hét landelijke verkeershoogtepunt; vermijd dan de vrijdag- en zaterdagochtenden op de Autobahn." },
        { t: "h2", v: "De grensregio's" },
        { t: "p", v: "Voor Nederlandse reizigers zijn vooral Niedersachsen en Nordrhein-Westfalen relevant. Als die vrij zijn, merk je dat in de grensstreek en op de doorgaande routes naar het zuiden." },
        { t: "h2", v: "Praktische tips" },
        { t: "list", v: ["Check de deelstaat van je bestemming, niet alleen het land", "Plan reisdagen op een dinsdag of woensdag", "Kijk naar de overlap met de Nederlandse vakanties"] },
      ],
    },
    {
      id: "kinderen-onderweg",
      titel: "Lange autorit met kinderen? 9 dingen die echt werken",
      cat: "Met kinderen",
      excerpt: "Van slimme stops tot het juiste vertrekmoment — zo blijft de reis naar het zuiden ontspannen.",
      auteur: "Lisa Bakker", datum: "14 mei 2026", leestijd: 7, img: "img/ardennen.jpg",
      bestemming: { naam: "Ardennen", land: "België", slim: 81, gezin: 87, besteWeek: "wk 35 · 24 aug" },
      toc: ["Vertrek op het juiste moment", "Plan je stops", "Eten & ontspanning", "Onderweg rust houden"],
      body: [
        { t: "p", v: "Een lange autorit hoeft geen beproeving te zijn. Met een beetje planning — en het juiste vertrekmoment — kom je een stuk relaxter aan." },
        { t: "h2", v: "Vertrek op het juiste moment" },
        { t: "p", v: "Vermijd de klassieke zwarte zaterdagen. Een vertrek midweek of heel vroeg in de ochtend scheelt vaak uren file." },
        { t: "tip", v: "Check vóór vertrek de drukte-tijdlijn van je bestemmingsland — zo weet je of je reisdag in een piekweek valt." },
        { t: "h2", v: "Plan je stops" },
        { t: "list", v: ["Elke twee uur een korte pauze", "Zoek speeltuinen langs de route", "Houd een verrassingstas met kleine spelletjes klaar"] },
        { t: "h2", v: "Eten & ontspanning" },
        { t: "p", v: "Neem voldoende water en gezonde snacks mee. Een goed gevulde koelbox voorkomt hangerige kinderen en dure tankstation-stops." },
        { t: "h2", v: "Onderweg rust houden" },
        { t: "quote", v: "Het geheim is niet sneller rijden, maar slimmer vertrekken." },
      ],
    },
    {
      id: "algarve-gezin",
      titel: "De Algarve met het gezin: zon, strand en rust",
      cat: "Bestemmingen",
      excerpt: "Portugals zuidkust scoort hoog op gezinsvriendelijkheid. We zetten de beste weken en plekken op een rij.",
      auteur: "Sanne de Vries", datum: "9 mei 2026", leestijd: 6, img: "img/algarve.jpg",
      bestemming: { naam: "Algarve", land: "Portugal", slim: 79, gezin: 91, besteWeek: "wk 38 · 14 sep" },
      toc: ["Waarom de Algarve?", "De beste reisweken", "Stranden voor kinderen", "Praktisch"],
      body: [
        { t: "p", v: "Brede zandstranden, kalme baaitjes en betrouwbaar weer maken de Algarve tot een topbestemming voor gezinnen. De gezinsscore van 91 liegt er niet om." },
        { t: "h2", v: "Waarom de Algarve?" },
        { t: "p", v: "Korte vluchttijd, veel familievriendelijke accommodaties en een zee die in het naseizoen heerlijk op temperatuur is." },
        { t: "h2", v: "De beste reisweken" },
        { t: "tip", v: "Half september (week 38) combineert warm zeewater met rust en lagere prijzen — de hoogste Slim-score van het jaar." },
        { t: "h2", v: "Stranden voor kinderen" },
        { t: "list", v: ["Praia da Marinha — rustige baai", "Meia Praia — lange, brede zandvlakte", "Praia de Alvor — ondiep en veilig"] },
        { t: "h2", v: "Praktisch" },
        { t: "p", v: "Huur een auto voor flexibiliteit, en boek accommodatie net buiten de drukste badplaatsen voor meer rust en ruimte." },
      ],
    },
    {
      id: "overlap-checken",
      titel: "Vakantie-overlap: de verborgen oorzaak van hoge prijzen",
      cat: "Drukte & prijzen",
      excerpt: "Als meerdere landen tegelijk vrij zijn, schieten drukte én prijzen omhoog. Zo herken en ontwijk je het.",
      auteur: "Mark Jansen", datum: "3 mei 2026", leestijd: 4, img: "img/costabrava.jpg",
      bestemming: { naam: "Costa Brava", land: "Spanje", slim: 72, gezin: 84, besteWeek: "wk 36 · 31 aug" },
      toc: ["Wat is overlap?", "Waarom het de prijs opdrijft", "Zo check je het"],
      body: [
        { t: "p", v: "Het grootste prijsverschil zit niet in de bestemming, maar in het moment. En dat moment wordt bepaald door hoeveel landen tegelijk vakantie hebben." },
        { t: "h2", v: "Wat is overlap?" },
        { t: "p", v: "Overlap ontstaat als de schoolvakanties van bijvoorbeeld Nederland, Duitsland en Frankrijk in dezelfde weken vallen. Dan reist heel West-Europa tegelijk." },
        { t: "tip", v: "Een week met lage overlap is bijna altijd goedkoper én rustiger — ook al is het hetzelfde seizoen." },
        { t: "h2", v: "Waarom het de prijs opdrijft" },
        { t: "p", v: "Meer vraag, hetzelfde aanbod: accommodaties en vluchten worden duurder naarmate meer gezinnen tegelijk op pad willen." },
        { t: "h2", v: "Zo check je het" },
        { t: "p", v: "Gebruik de overlap-indicator op de landenpagina. Die toont per week hoe sterk de vakanties van buurlanden samenvallen — laag is beter." },
      ],
    },
    {
      id: "zeeland-dichtbij",
      titel: "Zeeland: de slimste vakantie zonder reistijd",
      cat: "Bestemmingen",
      excerpt: "Geen files, geen vliegtuig, wél zee en ruimte. Waarom dichtbij soms het slimste is.",
      auteur: "Lisa Bakker", datum: "28 apr 2026", leestijd: 5, img: "img/zeeland.jpg",
      bestemming: { naam: "Zeeland", land: "Nederland", slim: 86, gezin: 90, besteWeek: "wk 37 · 7 sep" },
      toc: ["Nul reistijd", "Wanneer het rustig is", "Voor elk gezin"],
      body: [
        { t: "p", v: "De hoogste Slim-score van al onze bestemmingen gaat naar Zeeland. Geen reisdag, geen grensdrukte — gewoon instappen en er zijn." },
        { t: "h2", v: "Nul reistijd" },
        { t: "p", v: "Binnen twee uur sta je met je voeten in het zand. Dat scheelt een hele reisdag heen én terug, en dus minder stress voor de kinderen." },
        { t: "tip", v: "Buiten de Nederlandse schoolvakanties is Zeeland verrassend rustig — perfect voor een lang weekend in september." },
        { t: "h2", v: "Wanneer het rustig is" },
        { t: "p", v: "Vermijd de weken waarin alle drie de Nederlandse regio's tegelijk vrij zijn. Daarbuiten heb je het strand vaak bijna voor jezelf." },
        { t: "h2", v: "Voor elk gezin" },
        { t: "list", v: ["Ondiepe, veilige stranden", "Veel natuurcampings", "Fietsen zonder hoogteverschil"] },
      ],
    },
  ];

  function related(id) {
    const post = posts.find(function (p) { return p.id === id; });
    return posts.filter(function (p) { return p.id !== id && p.cat === post.cat; })
      .concat(posts.filter(function (p) { return p.id !== id && p.cat !== post.cat; }))
      .slice(0, 3);
  }

  return { posts: posts, cats: CATS, related: related };
})();
