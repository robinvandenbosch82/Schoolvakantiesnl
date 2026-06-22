// Blog.jsx — blog-overzicht + detail met widgets die teruggrijpen op de tools.

const { useState: useStateB, useEffect: useEffectB } = React;

// ---------- gedeelde widgets ----------
function NieuwsbriefWidget() {
  const [done, setDone] = useStateB(false);
  return (
    <div className="widget nieuwsbrief">
      <h4>📬 Slim-weg nieuwsbrief</h4>
      <p>Elke maand de slimste reisweken en rustige bestemmingen in je inbox.</p>
      {done ? (
        <div className="nb-done">✓ Je bent aangemeld!</div>
      ) : (
        <form onSubmit={function (e) { e.preventDefault(); setDone(true); }}>
          <input type="email" placeholder="jouw@email.nl" required />
          <button className="btn" type="submit">Aanmelden</button>
        </form>
      )}
    </div>
  );
}

function VakantieCountdownWidget({ goTo }) {
  const [state, setState] = useStateB({ status: "loading", items: [] });
  useEffectB(function () {
    let alive = true;
    window.Holidays.getYearData("nl", 2026).then(function (d) {
      if (!alive) return;
      const vandaag = new Date(); vandaag.setHours(0, 0, 0, 0);
      const items = d.vakanties.map(function (v) {
        const start = window.Holidays.helpers.parse(v.minStart);
        return { naam: v.naam, start: start, dagen: Math.round((start - vandaag) / 86400000) };
      }).filter(function (x) { return x.dagen >= 0; }).sort(function (a, b) { return a.dagen - b.dagen; }).slice(0, 3);
      setState({ status: "ok", items: items });
    }).catch(function () { if (alive) setState({ status: "err", items: [] }); });
    return function () { alive = false; };
  }, []);
  return (
    <div className="widget countdown">
      <div className="widget-head"><h4>Aankomende vakanties</h4><span className="live-dot" title="Live via OpenHolidays"></span></div>
      {state.status === "ok" ? (
        <ul className="cd-list">
          {state.items.map(function (it) {
            return (
              <li key={it.naam}>
                <span className="cd-naam">{it.naam}</span>
                <span className="cd-dagen mono">{it.dagen} dagen</span>
              </li>
            );
          })}
        </ul>
      ) : <div className="cd-skel">{state.status === "err" ? "Niet beschikbaar" : "Laden…"}</div>}
      <button className="widget-link" onClick={function () { goTo("land"); }}>Alle schoolvakanties →</button>
    </div>
  );
}

function ReisweekWidget({ goTo }) {
  const W = window.SV.weeks;
  const best = W.reduce(function (b, w, i) { return w.score > W[b].score ? i : b; }, 0);
  const bw = W[best];
  return (
    <div className="widget reisweek">
      <h4>Slimste reisweek nu</h4>
      <div className="rw-body">
        <window.ScoreRing score={bw.score} band={bw.band} size={92} />
        <div className="rw-info">
          <span className="mono rw-wk">WEEK {bw.wk}</span>
          <strong>{bw.d1}</strong>
          <span className="rw-note">rustig, betaalbaar &amp; mooi weer</span>
        </div>
      </div>
      <button className="btn" style={{ width: "100%" }} onClick={function () { goTo("planner"); }}>Open de planner</button>
    </div>
  );
}

function BestemmingWidget({ b, goTo }) {
  const cls = b.slim >= 70 ? "rustig" : b.slim >= 45 ? "matig" : "druk";
  return (
    <div className="widget bestemming">
      <h4>Slim-score · {b.naam}</h4>
      <div className={"bw-grid is-" + cls}>
        <div className="bw-ring"><window.ScoreRing score={b.slim} band={cls} size={96} /></div>
        <div className="bw-stats">
          <div className="bw-stat"><span>Gezinsscore</span><strong>{b.gezin}/100</strong></div>
          <div className="bw-stat"><span>Beste reisweek</span><strong>{b.besteWeek}</strong></div>
          <div className="bw-stat"><span>Land</span><strong>{b.land}</strong></div>
        </div>
      </div>
      <button className="btn" style={{ width: "100%" }} onClick={function () { goTo("planner"); }}>Plan deze reis</button>
    </div>
  );
}

function CatChip({ cat }) { return <span className={"cat-chip cat-" + cat.replace(/[^a-z]/gi, "").toLowerCase()}>{cat}</span>; }

// ---------- OVERZICHT ----------
function BlogOverview({ goTo, openPost }) {
  const [cat, setCat] = useStateB("Alle");
  const posts = window.BLOG.posts;
  const featured = posts.find(function (p) { return p.featured; }) || posts[0];
  const filtered = posts.filter(function (p) { return p !== featured && (cat === "Alle" || p.cat === cat); });

  return (
    <div className="page blog rise">
      <div className="blog-head">
        <span className="eye">Blog &amp; reisinspiratie</span>
        <h1>Slim weg met het gezin</h1>
        <p className="lead">Praktische tips, rustige bestemmingen en alles over slim plannen rond de schoolvakanties.</p>
      </div>

      {/* FEATURED */}
      <article className="feat-post" onClick={function () { openPost(featured.id); }}>
        <div className="feat-img"><img src={featured.img} alt={featured.titel} /><span className="feat-badge">Uitgelicht</span></div>
        <div className="feat-body">
          <CatChip cat={featured.cat} />
          <h2>{featured.titel}</h2>
          <p>{featured.excerpt}</p>
          <div className="post-meta"><span>{featured.auteur}</span><span>·</span><span>{featured.datum}</span><span>·</span><span>{featured.leestijd} min</span></div>
        </div>
      </article>

      <div className="blog-layout">
        <div>
          {/* FILTERS */}
          <div className="blog-filters">
            {["Alle"].concat(window.BLOG.cats).map(function (c) {
              return <button key={c} className={cat === c ? "on" : ""} onClick={function () { setCat(c); }}>{c}</button>;
            })}
          </div>
          {/* GRID */}
          <div className="post-grid">
            {filtered.map(function (p) {
              return (
                <article key={p.id} className="post-card" onClick={function () { openPost(p.id); }}>
                  <div className="post-img"><img src={p.img} alt={p.titel} loading="lazy" /><span className="post-cat-ov"><CatChip cat={p.cat} /></span></div>
                  <div className="post-card-body">
                    <h3>{p.titel}</h3>
                    <p>{p.excerpt}</p>
                    <div className="post-meta"><span>{p.datum}</span><span>·</span><span>{p.leestijd} min</span></div>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
        {/* SIDEBAR */}
        <aside className="blog-side">
          <ReisweekWidget goTo={goTo} />
          <VakantieCountdownWidget goTo={goTo} />
          <NieuwsbriefWidget />
        </aside>
      </div>
    </div>
  );
}

// ---------- DETAIL ----------
function BlogDetail({ goTo, postId, openPost, backToList }) {
  const post = window.BLOG.posts.find(function (p) { return p.id === postId; });
  const author = window.TEAM.byNaam(post.auteur);
  const reviewer = (author && author.id === "sanne") ? window.TEAM.get("mark") : window.TEAM.get("sanne");
  const related = window.BLOG.related(postId);
  const stripTheme = { "Met kinderen": "familie", "Drukte & prijzen": "familie", "Bestemmingen": "zomer", "Slim plannen": "zomer" }[post.cat] || "familie";
  const stripCode = { "Nederland": "nl", "Duitsland": "de" }[post.bestemming.land] || null;
  const stripTitle = stripCode ? "Maak er een uitje van in " + post.bestemming.land : "Populaire uitjes voor je gezinsvakantie";
  useEffectB(function () { window.scrollTo(0, 0); }, [postId]);

  // body met één inline widget na de eerste h2
  let h2seen = 0;
  const blocks = [];
  post.body.forEach(function (b, i) {
    blocks.push(b);
    if (b.t === "h2") { h2seen++; if (h2seen === 1) blocks.push({ t: "inlinewidget" }); }
  });

  return (
    <div className="page blogdetail rise">
      <button className="back-link" onClick={backToList}>← Alle artikelen</button>

      <header className="art-head">
        <CatChip cat={post.cat} />
        <h1>{post.titel}</h1>
        <window.EEAT.AuthorByline author={author} datum={post.datum} leestijd={post.leestijd} />
      </header>

      <div className="art-hero"><img src={post.img} alt={post.titel} /></div>

      <div className="art-layout">
        <article className="art-body">
          {blocks.map(function (b, i) {
            if (b.t === "p") return <p key={i}>{b.v}</p>;
            if (b.t === "h2") return <h2 key={i} id={"s" + i}>{b.v}</h2>;
            if (b.t === "tip") return <div key={i} className="art-tip"><span className="art-tip-ic">💡</span><p>{b.v}</p></div>;
            if (b.t === "quote") return <blockquote key={i}>{b.v}</blockquote>;
            if (b.t === "list") return <ul key={i} className="art-list">{b.v.map(function (li, j) { return <li key={j}>{li}</li>; })}</ul>;
            if (b.t === "inlinewidget") return (
              <div key={i} className="art-inline-widget">
                <BestemmingWidget b={post.bestemming} goTo={goTo} />
              </div>
            );
            return null;
          })}

          {/* share */}
          <div className="art-share">
            <span>Deel dit artikel</span>
            <div className="share-btns">
              <button aria-label="Deel op X">𝕏</button>
              <button aria-label="Deel op Facebook">f</button>
              <button aria-label="Deel via WhatsApp">✆</button>
              <button aria-label="Kopieer link">🔗</button>
            </div>
          </div>

          {/* auteur + controle (E-E-A-T) */}
          <window.EEAT.AuthorCard author={author} reviewer={reviewer} updated={post.datum} />
        </article>

        <aside className="art-side">
          <div className="widget toc">
            <h4>In dit artikel</h4>
            <ol>
              {post.toc.map(function (t, i) { return <li key={i}>{t}</li>; })}
            </ol>
          </div>
          <BestemmingWidget b={post.bestemming} goTo={goTo} />
          <VakantieCountdownWidget goTo={goTo} />
          <NieuwsbriefWidget />
        </aside>
      </div>

      {/* VIATOR affiliate strip */}
      <window.ActivitiesStrip theme={stripTheme} countryCode={stripCode} title={stripTitle} />

      {/* RELATED */}
      <section className="related">
        <h2>Lees ook</h2>
        <div className="post-grid three">
          {related.map(function (p) {
            return (
              <article key={p.id} className="post-card" onClick={function () { openPost(p.id); }}>
                <div className="post-img"><img src={p.img} alt={p.titel} loading="lazy" /><span className="post-cat-ov"><CatChip cat={p.cat} /></span></div>
                <div className="post-card-body">
                  <h3>{p.titel}</h3>
                  <div className="post-meta"><span>{p.datum}</span><span>·</span><span>{p.leestijd} min</span></div>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}

// ---------- ROUTER ----------
function Blog({ goTo }) {
  const [postId, setPostId] = useStateB(null);
  function openPost(id) { setPostId(id); window.scrollTo(0, 0); }
  function backToList() { setPostId(null); window.scrollTo(0, 0); }
  return postId
    ? <BlogDetail goTo={goTo} postId={postId} openPost={openPost} backToList={backToList} />
    : <BlogOverview goTo={goTo} openPost={openPost} />;
}

window.Blog = Blog;
