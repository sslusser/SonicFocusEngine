<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sonic Focus Engine — Coming Soon</title>
  <meta name="description"
    content="Generative soundscapes for deep focus and flow. Sonic Focus Engine is coming soon." />
  <meta name="theme-color" content="#0b0f14" />

  <!-- Open Graph / Twitter -->
  <meta property="og:title" content="Sonic Focus Engine — Coming Soon" />
  <meta property="og:description" content="Generative soundscapes for deep focus and flow." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://sonicfocusengine.com/" />

  <style>
    :root {
      --bg1: #0b0f14;
      --bg2: #121923;
      --fg: #e9f1ff;
      --muted: #a8b3c7;
      --accent: #86e1ff;
      --card: #0f141b;
      --ring: #2a3a4d;
    }

    html,
    body {
      height: 100%
    }

    body {
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Inter, Arial, sans-serif;
      color: var(--fg);
      background: radial-gradient(1200px 800px at 20% 10%, #122033 0%, transparent 60%),
        radial-gradient(1000px 700px at 80% 90%, #0e2233 0%, transparent 60%),
        linear-gradient(180deg, var(--bg1), var(--bg2));
      display: grid;
      place-items: center;
      overflow: hidden;
    }

    .wrap {
      text-align: center;
      padding: 48px 24px;
      max-width: 720px
    }

    .badge {
      display: inline-block;
      padding: 6px 10px;
      border: 1px solid var(--ring);
      border-radius: 999px;
      font-size: 12px;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--muted);
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(2px);
    }

    h1 {
      margin: 16px 0 8px;
      font-size: clamp(28px, 4vw, 44px);
      letter-spacing: .02em
    }

    .tag {
      color: var(--muted);
      font-size: clamp(14px, 2.2vw, 18px);
      margin: 0 0 28px
    }

    .card {
      margin: 0 auto 26px;
      padding: 18px 20px;
      border: 1px solid var(--ring);
      border-radius: 16px;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.01));
      display: inline-flex;
      gap: 14px;
      align-items: center;
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 12px var(--accent);
    }

    .links {
      display: flex;
      gap: 12px;
      justify-content: center;
      flex-wrap: wrap
    }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 16px;
      border-radius: 12px;
      border: 1px solid var(--ring);
      color: var(--fg);
      text-decoration: none;
      background: #111823;
      transition: .15s ease;
    }

    .btn:hover {
      transform: translateY(-1px);
      border-color: #3b536f
    }

    .btn.primary {
      border-color: transparent;
      background: linear-gradient(180deg, #193042, #111a24);
    }

    .btn .emoji {
      font-size: 18px
    }

    footer {
      position: fixed;
      bottom: 14px;
      left: 0;
      right: 0;
      text-align: center;
      color: var(--muted);
      font-size: 12px
    }

    /* subtle floating grain */
    .grain {
      pointer-events: none;
      position: fixed;
      inset: -50vmax;
      opacity: .08;
      mix-blend: overlay;
      background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(%23n)"/></svg>');
      animation: drift 40s linear infinite;
    }

    @keyframes drift {
      0% {
        transform: translate3d(0, 0, 0) rotate(0deg) scale(1)
      }

      50% {
        transform: translate3d(3%, -2%, 0) rotate(180deg) scale(1.02)
      }

      100% {
        transform: translate3d(0, 0, 0) rotate(360deg) scale(1)
      }
    }
  </style>
</head>

<body>
  <div class="grain" aria-hidden="true"></div>
  <main class="wrap" role="main">
    <span class="badge">Coming Soon</span>
    <h1>Sonic Focus Engine</h1>
    <p class="tag">Generative soundscapes for deep focus and flow.</p>

    <div class="card" role="status" aria-live="polite">
      <span class="dot" aria-hidden="true"></span>
      <span>First long-form ambient releases are in production.</span>
    </div>

    <div class="links">
      <a class="btn primary" href="https://www.youtube.com/@SonicFocusEngine" target="_blank" rel="noopener">
        <span class="emoji">▶️</span><span>Visit the YouTube Channel</span>
      </a>
      <a class="btn" href="mailto:sonicfocusengine@gmail.com?subject=Hello%20from%20the%20site">
        <span class="emoji">✉️</span><span>sonicfocusengine@gmail.com</span>
      </a>
    </div>
  </main>

  <footer>
    © <span id="y"></span> Sonic Focus Engine
  </footer>

  <script>
    document.getElementById('y').textContent = new Date().getFullYear();
  </script>
</body>

</html>
