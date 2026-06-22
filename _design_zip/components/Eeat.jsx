// Eeat.jsx — herbruikbare E-E-A-T-blokken: avatar, auteursregel, auteurskaart, controle-balk

(function () {
  // monogram-avatar (geen foto's — schone initialen)
  function Avatar({ p, size }) {
    const s = size || 44;
    return (
      <span className="eeat-av" style={{ width: s, height: s, fontSize: s * 0.34 }} aria-hidden="true">
        {p.mono}
      </span>
    );
  }

  // compacte auteursregel onder een titel: "Geschreven door Naam · rol"
  function AuthorByline({ author, datum, leestijd, onOpen }) {
    if (!author) return null;
    return (
      <div className="eeat-byline">
        <Avatar p={author} size={40} />
        <div className="eeat-byline-txt">
          <span className="eeat-by-name">
            Geschreven door{" "}
            {onOpen
              ? <button className="eeat-link" onClick={onOpen}>{author.naam}</button>
              : <strong>{author.naam}</strong>}
          </span>
          <span className="eeat-by-meta">
            {author.kort}
            {datum ? <span> · {datum}</span> : null}
            {leestijd ? <span> · {leestijd} min lezen</span> : null}
          </span>
        </div>
      </div>
    );
  }

  // volledige auteurskaart (onder artikel): bio + credentials + reviewer
  function AuthorCard({ author, reviewer, updated, onOpen }) {
    if (!author) return null;
    return (
      <div className="eeat-card">
        <div className="eeat-card-head">
          <Avatar p={author} size={56} />
          <div>
            <span className="eeat-eyebrow">Over de auteur</span>
            <h4 className="eeat-card-name">
              {onOpen
                ? <button className="eeat-link" onClick={onOpen}>{author.naam}</button>
                : author.naam}
            </h4>
            <span className="eeat-card-rol">{author.rol} · sinds {author.sinds}</span>
          </div>
        </div>
        <p className="eeat-card-bio">{author.bio}</p>
        {author.cred ? (
          <ul className="eeat-cred">
            {author.cred.map(function (c, i) { return <li key={i}>{c}</li>; })}
          </ul>
        ) : null}
        {reviewer ? (
          <div className="eeat-review-line">
            <span className="eeat-check" aria-hidden="true">✓</span>
            <span>Feitelijk gecontroleerd door <strong>{reviewer.naam}</strong>, {reviewer.kort}
              {updated ? <span> — laatst geverifieerd {updated}</span> : null}.
            </span>
          </div>
        ) : null}
      </div>
    );
  }

  // controle-balk voor tool-/contentpagina's: "Gecontroleerd door … · bijgewerkt … · bronnen"
  function ReviewBar({ reviewer, updated, sources, onOver }) {
    const T = window.TEAM;
    const rev = reviewer || (T && T.redactie);
    const upd = updated || (T && T.updated);
    const src = sources || (T && T.bronnen) || [];
    if (!rev) return null;
    return (
      <div className="eeat-bar">
        <div className="eeat-bar-in">
          <div className="eeat-bar-main">
            <span className="eeat-check lg" aria-hidden="true">✓</span>
            <div className="eeat-bar-txt">
              <span className="eeat-bar-lead">
                Gecontroleerd door{" "}
                {onOver
                  ? <button className="eeat-link" onClick={onOver}>{rev.naam}</button>
                  : <strong>{rev.naam}</strong>}
              </span>
              <span className="eeat-bar-sub">
                Data uit officiële bronnen, handmatig geverifieerd. Laatst bijgewerkt: {upd}.
              </span>
            </div>
          </div>
          {src.length ? (
            <div className="eeat-sources">
              <span className="eeat-src-lbl">Bronnen</span>
              <div className="eeat-src-list">
                {src.map(function (b, i) {
                  return <span key={i} className="eeat-src" title={b.wat}>{b.naam}</span>;
                })}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    );
  }

  window.EEAT = { Avatar: Avatar, AuthorByline: AuthorByline, AuthorCard: AuthorCard, ReviewBar: ReviewBar };
})();
