// experts.js — redactie & expertprofielen voor E-E-A-T (auteurs, reviewers, bronnen)

window.TEAM = (function () {
  const experts = [
    {
      id: "sanne",
      naam: "Sanne de Vries",
      mono: "SdV",
      rol: "Hoofdredacteur & reisplanner",
      kort: "Hoofdredacteur",
      sinds: 2012,
      bio: "Reisjournalist met ruim veertien jaar ervaring in gezinsvakanties. Sanne bewaakt de redactionele lijn en controleert alle vakantie- en feestdagdata voordat ze online gaan.",
      cred: ["14 jaar reisredactie", "Bezocht 30+ landen met kinderen", "Eindverantwoordelijk voor data-accuratesse"],
      focus: ["Redactie", "Slim plannen"],
    },
    {
      id: "mark",
      naam: "Mark Jansen",
      mono: "MJ",
      rol: "Data- & drukte-analist",
      kort: "Data-analist",
      sinds: 2015,
      bio: "Bouwde het drukte- en Slim-score-model achter Schoolvakanties.nl. Mark combineert officiële vakantiekalenders met verkeers- en boekingsdata tot voorspelbare reisweken.",
      cred: ["Ontwierp het Slim-score-model", "Werkt met OpenHolidays & KMK-bronnen", "Specialist Duitse deelstaten"],
      focus: ["Drukte & prijzen", "Data"],
    },
    {
      id: "lisa",
      naam: "Lisa Bakker",
      mono: "LB",
      rol: "Redacteur — reizen met kinderen",
      kort: "Reisredacteur",
      sinds: 2018,
      bio: "Moeder van drie en gepokt en gemazeld in lange autoritten naar het zuiden. Lisa schrijft de praktische gidsen en test bestemmingen op gezinsvriendelijkheid.",
      cred: ["60+ gezinsreizen", "Specialist bestemmingen met kinderen", "Praktijktest van elke tip"],
      focus: ["Met kinderen", "Bestemmingen"],
    },
  ];

  const byId = {};
  experts.forEach(function (e) { byId[e.id] = e; });
  const byNaam = {};
  experts.forEach(function (e) { byNaam[e.naam] = e; });

  // redactie als geheel — gebruikt als 'gecontroleerd door' op tool-pagina's
  const redactie = {
    id: "redactie",
    naam: "de Schoolvakanties.nl-redactie",
    mono: "SV",
    rol: "Onderwijs- & reisredactie",
    kort: "Redactie",
  };

  const bronnen = [
    { naam: "Rijksoverheid.nl", wat: "officiële schoolvakanties NL" },
    { naam: "OpenHolidays API", wat: "live vakantie- & feestdagdata EU" },
    { naam: "KMK (Duitsland)", wat: "spreiding deelstaten" },
  ];

  return {
    experts: experts,
    redactie: redactie,
    bronnen: bronnen,
    get: function (id) { return byId[id] || null; },
    byNaam: function (naam) { return byNaam[naam] || null; },
    // laatst geverifieerd — toon op tool-pagina's
    updated: "18 juni 2026",
  };
})();
