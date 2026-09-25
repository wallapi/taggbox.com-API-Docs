import React, { useEffect, useRef, useState } from 'react';

// Social Widget - one drop-in component. It calls only /api/posts on our own
// server (which holds the token) and renders the same markup as preview.html.
// React escapes all text itself; links and images are limited to http(s).

const NET_MARK = {
  instagram: 'IG', facebook: 'f', twitter: 'X', x: 'X', tiktok: '♪', youtube: '▶', linkedin: 'in',
  pinterest: 'P', google: 'G', yelp: 'y', tripadvisor: 'T', trustpilot: '★',
};

function safeUrl(url) {
  return typeof url === 'string' && /^https?:\/\//i.test(url) ? url : '';
}

function shortDate(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return '';
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
}

function Card({ post, parts }) {
  const author = post.author || {};
  const network = post.network || {};
  const name = author.name || author.handle || '';
  const netName = network.name || '';
  const slug = String(network.slug || '').toLowerCase();
  const media = Array.isArray(post.media) ? post.media : [];
  // The first media entry of type "image" - never media[0], which can be a video.
  const image = parts.includes('media') ? media.find((m) => m && m.type === 'image' && safeUrl(m.cdn_url)) : null;
  const initial = name.slice(0, 1).toUpperCase();
  const rating = Math.round(Number(post.rating));
  const text = post.content && post.content.text;

  const blocks = {};
  if (image) {
    const style = {};
    if (image.width && image.height) style['--tbx-ar'] = `${Number(image.width)} / ${Number(image.height)}`;
    if (typeof image.preview_data_uri === 'string' && image.preview_data_uri.startsWith('data:image/')) {
      style['--tbx-ph'] = `url(${image.preview_data_uri})`;
    }
    blocks.media = (
      <div className="tbx-media" data-network={netName} style={style} key="media">
        <img src={image.cdn_url} alt="" loading="lazy" />
        {media.some((m) => m && m.type === 'video') && <span className="tbx-play" />}
      </div>
    );
  }
  blocks.head = (
    <div className="tbx-head" key="head">
      {safeUrl(author.avatar_url)
        ? <img className="tbx-avatar" src={author.avatar_url} alt="" loading="lazy" data-initial={initial} />
        : <span className="tbx-avatar">{initial}</span>}
      <div className="tbx-who">
        {name && <span className="tbx-author">{name}</span>}
        <time className="tbx-date" dateTime={post.created_at}>{shortDate(post.created_at)}</time>
      </div>
      <span className="tbx-net" data-net={slug} data-mark={NET_MARK[slug] || netName.slice(0, 1)} title={netName} />
    </div>
  );
  if (rating >= 1 && rating <= 5) {
    blocks.stars = (
      <div className="tbx-stars" aria-label={`${rating} out of 5`} key="stars">
        {'★'.repeat(rating) + '☆'.repeat(5 - rating)}
      </div>
    );
  }
  if (text) blocks.text = <p className="tbx-text" key="text">{text}</p>;

  const cls = image || !parts.includes('media') ? 'tbx-card' : 'tbx-card tbx-card--text';
  return (
    <a className={cls} href={safeUrl(post.source && post.source.permalink) || '#'} target="_blank" rel="noopener noreferrer">
      {parts.map((p) => blocks[p]).filter(Boolean)}
    </a>
  );
}

// Rating Badge / Badge: the average of every rated post, its stars and the count.
function Badge({ posts }) {
  const rated = posts.filter((p) => typeof p.rating === 'number' && p.rating >= 1 && p.rating <= 5);
  const nets = [];
  rated.forEach((p) => {
    const n = p.network || {};
    if (n.slug && !nets.some((x) => x.slug === n.slug)) nets.push({ slug: n.slug, name: n.name || '' });
  });
  const avg = rated.length ? rated.reduce((sum, p) => sum + p.rating, 0) / rated.length : 0;
  const full = Math.floor(avg + 0.5);
  return (
    <div className="tbx-badge">
      <div className="tbx-badge-nets">
        {nets.map((n) => (
          <span className="tbx-net" data-net={n.slug} data-mark={NET_MARK[n.slug] || n.name.slice(0, 1)} title={n.name} key={n.slug} />
        ))}
      </div>
      <div className="tbx-badge-title">{nets.length === 1 ? `${nets[0].name} Reviews` : 'Customer Reviews'}</div>
      <div className="tbx-badge-score">
        <span className="tbx-badge-avg">{avg.toFixed(1)}</span>
        <span className="tbx-stars" aria-label={`${avg.toFixed(1)} out of 5`}>{'★'.repeat(full) + '☆'.repeat(5 - full)}</span>
      </div>
      <div className="tbx-badge-count">Based on {rated.length} review{rated.length === 1 ? '' : 's'}</div>
    </div>
  );
}

export default function SocialWidget() {
  const [state, setState] = useState({ loading: true });
  const trackRef = useRef(null);

  useEffect(() => {
    let alive = true;
    fetch('/api/posts')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((data) => alive && setState({ data }))
      .catch((err) => alive && setState({ error: err.message }));
    return () => { alive = false; };
  }, []);

  if (state.loading) return <section className="tbx-widget"><p className="tbx-empty">Loading posts…</p></section>;
  if (state.error) return <section className="tbx-widget"><p className="tbx-empty">Could not load posts right now.</p></section>;

  const { theme, sample } = state.data;
  // Photo-only themes skip posts without an image - they would be empty cards.
  const posts = theme.parts.join() !== 'media' ? state.data.posts : state.data.posts.filter(
    (p) => Array.isArray(p.media) && p.media.some((m) => m && m.type === 'image' && safeUrl(m.cdn_url)));
  const slider = theme.layout === 'slider' && posts.length > 0;
  const scroll = (dir) => {
    const t = trackRef.current;
    if (t) t.scrollBy({ left: dir * t.clientWidth, behavior: 'smooth' });
  };
  const track = posts.length && theme.layout === 'badge'
    ? <Badge posts={posts} />
    : posts.length
    ? (
      <div className="tbx-track" ref={trackRef}>
        {posts.map((post, i) => <Card post={post} parts={theme.parts} key={post.id || i} />)}
      </div>
    )
    : <p className="tbx-empty">No posts to show yet.</p>;

  return (
    <section className={`tbx-widget tbx-t-${theme.slug} tbx-l-${theme.layout}${theme.clamp ? ' tbx-clamp' : ''}`}>
      <h1 className="tbx-header">Social Widget</h1>
      {sample && <p className="tbx-note">Sample posts - set ACCESS_TOKEN in .env to show your gallery.</p>}
      {slider
        ? (
          <div className="tbx-slider">
            <button className="tbx-arrow tbx-arrow--prev" type="button" aria-label="Previous" onClick={() => scroll(-1)}>‹</button>
            {track}
            <button className="tbx-arrow tbx-arrow--next" type="button" aria-label="Next" onClick={() => scroll(1)}>›</button>
          </div>
        )
        : track}
    </section>
  );
}
