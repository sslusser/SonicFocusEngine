# Sonic Focus Engine — Product Requirements Document

## 1. Summary

Sonic Focus Engine is a personal generative audio tool that creates long-form ambient soundscapes centered on a chosen fundamental frequency rather than a traditional key. It outputs WAV files that are suitable for multi hour YouTube videos and personal focus sessions. It is not a SaaS. It runs locally first. A thin web UI is optional after the core engine is stable. Authentication is required for any web surface to ensure safety and prevent misuse.

Primary deliverables

- A command line tool that renders frequency centric WAVs of 5 to 180 plus minutes
- A modular Python audio engine with layers, modulation, and evolution over time
- Optional lightweight web app to collect inputs and return a WAV or ZIP of stems
- Preset system for repeatable moods and seeds
- Authenticated access for any HTTP endpoints

Target outcome

- Produce a consistent pipeline for two hour ambient pieces with minimal manual steps
- Match or exceed the utility of channels like Ambient Outpost for ADHD focus use

## 2. Goals and Non Goals

### 2.1 Goals

- Generate long, evolving, non repeating ambient audio centered on a single frequency
- Support deterministic seeds for repeatable results and random mode for variation
- Allow multi track stem output for later mixing or direct stereo WAV render
- Stream render to disk to avoid high memory usage on very long files
- Simple UX: a single command or a single form posts inputs and returns a download
- Enforce authentication for the web API, even in local deployments

### 2.2 Non Goals for v1

- No sampling or external VSTs
- No AI models
- No multi user accounts or payments
- No complex DAW integration beyond exporting standard WAV and optional MIDI

## 3. Personas and Use Cases

### 3.1 Persona: Scott

- Needs a fast path from idea to a two hour WAV
- Prefers deterministic seeds to reproduce a piece if the result is good
- Runs locally on macOS and Linux servers
- Wants safe, private access to the tool behind authentication

### 3.2 Core use cases

1. Render a 2 hour focus drone at 136.1 Hz with light harmonic drift
2. Generate stems for drone, harmonics, partials, and noise, then mix
3. Create a 10 minute preview, then render full length if acceptable
4. Render several seeds and keep the best one
5. Use one preset recipe nightly with date stamped output names
6. Access the web form locally or over VPN with authentication

## 4. Functional Requirements

### 4.1 Inputs

- fundamental_hz: float, example 136.1
- duration_minutes: int, 5 to 360
- sample_rate: int, default 44100, optional 48000
- bit_depth: 16 or 24, default 16
- channels: mono or stereo
- seed: int or the literal string "random"
- preset: string id, optional
- layers: list of layer specs
  - drone layer on fundamental
  - harmonic overtones: multiples such as 2x, 3x, 4x, 5x, 6x
  - inharmonic partials: ratios such as 1.618x or 2.618x
  - filtered noise wash: pink or brown noise with bandpass
- modulation config per layer
  - amp LFO: waveform, rate in Hz, depth as 0 to 1
  - pan LFO: rate and depth
  - tiny detune for beating: cents or Hz drift range
  - filter sweep: lowpass or bandpass cutoff drift
  - on off events: slow fades in and out
- output
  - single stereo WAV
  - stems as separate mono or stereo WAVs
  - optional MIDI outline for inspection

### 4.2 Behaviors

- Engine renders sample buffers to disk in continuous chunks
- Modulations advance based on sample time for determinism
- Long envelopes and fades avoid clicks
- Optional preview mode renders the first 10 minutes with identical seed

### 4.3 Presets

- JSON files stored in repo
- Each preset defines defaults for layers, modulation, and drift ranges
- Examples
  - Deep Flow 136: fundamental 136.1 Hz, sparse, wide stereo drift
  - 528 Harmonic Wash: brighter partials and shimmer feel
  - Night Drift 60: sub heavy, slow amplitude waves

### 4.4 CLI

- `sfe render --freq 136.1 --minutes 120 --preset deep_flow --seed 42 --stems`
- `sfe preview --freq 528 --minutes 10 --preset bright_wash --seed random`
- `sfe list-presets`
- `sfe explain --preset deep_flow`

### 4.5 Optional Web API, local first

- `POST /api/render` with JSON body matching the configuration schema
- `POST /api/preview` same as render but short duration
- `GET /api/presets` returns preset metadata
- All endpoints require authentication

### 4.6 File naming

- `{date}_{preset}_{freq}Hz_{mins}m_seed{seed}_{mix|stems}.wav`
- For stems append `_drone.wav`, `_harm1.wav`, `_noise.wav` and so on

## 5. Non Functional Requirements

- Deterministic rendering when seed and inputs are identical
- Low memory footprint during render
- Render speed acceptable for overnight jobs on a modest CPU
- No external network calls required to create audio
- Code structured for clarity, minimal dependencies, and modular layers
- Testable pure functions for oscillators, envelopes, LFOs, and modulators
- Authenticated API with strong defaults and hardened configuration

## 6. System Architecture

### 6.1 High level components

- Core audio engine in Python
  - Oscillators: sine, triangle, noise pink and brown
  - Envelopes: ADSR and custom long shapes
  - Filters: simple biquad lowpass and bandpass
  - LFOs: sine, triangle, random smooth
  - Mixers and gain staging
- Renderer
  - Chunked buffer synthesis to WAV using `wave` or `soundfile`
  - Stereo or mono bus
  - Stem writer for parallel buses
- Preset Manager
  - Load and validate JSON preset schemas
  - Resolve presets into layer graphs
- CLI using Typer or argparse
- Optional FastAPI service for local web UI
- Authentication module and middleware

### 6.2 Data flow

Inputs go to Preset Manager which produces a Layer Graph. The Engine iterates over time in chunks. Each layer produces a buffer. Buses mix to stereo and optional stems. Writer flushes buffers to disk. Final output is a WAV or a ZIP of stems.

### 6.3 Determinism

- Seed sets Python `random` and a local PRNG for LFO phase starts and on off events
- Modulation phase is derived from absolute sample time only
- All time based decisions rely on sample indices rather than wall clock

## 7. Audio Design

### 7.1 Oscillators

- Sine: `sin(2π f t)`
- Triangle: band limited variant or naive with lowpass
- Pink noise: Voss McCartney or filtered white noise
- Brown noise: integrated white with clamp

### 7.2 Envelopes

- Long attack and release in seconds to minutes
- Optional breathing envelope with gentle periodic rise and fall
- Smoothing to avoid discontinuities at chunk boundaries

### 7.3 Modulation

- Amp LFO: very low rates 0.005 to 0.03 Hz
- Pan LFO: low rates with small depth for stereo drift
- Filter LFO: slow movement of cutoff and Q
- Detune: add or subtract small Hz offsets per layer with drift over minutes
- Density modulation: probabilistic on off with crossfaded transitions

### 7.4 Harmonic structure

- Harmonic set: 1x, 2x, 3x, 4x, 5x, 6x, optionally 8x
- Inharmonic set: 1.414x, 1.618x, 2.236x, 2.618x
- Prevent harsh clustering by spacing gains and registers
- Optional octave wrapping for very high partials

### 7.5 Gain staging and headroom

- Target integrated level before mastering near minus 18 LUFS equivalent
- Leave headroom for YouTube transcode
- Optional gentle highpass at 25 to 30 Hz to avoid sub rumble

### 7.6 Output formats

- 44.1 kHz 16 bit stereo WAV is default
- 48 kHz 24 bit optional
- Stems are separate mono or stereo per layer group

## 8. Configuration Schema

```json
{
  "fundamental_hz": 136.1,
  "duration_minutes": 120,
  "sample_rate": 44100,
  "bit_depth": 16,
  "channels": 2,
  "seed": 42,
  "layers": [
    {
      "type": "drone",
      "ratio": 1.0,
      "gain_db": -12,
      "amp_lfo": { "rate_hz": 0.01, "depth": 0.2, "wave": "sine" },
      "pan_lfo": { "rate_hz": 0.003, "depth": 0.3, "wave": "triangle" },
      "filter": {
        "mode": "lowpass",
        "cutoff_hz": 4000,
        "q": 0.7,
        "lfo": { "rate_hz": 0.002, "depth": 0.2 }
      }
    },
    {
      "type": "harmonic",
      "ratio": 3.0,
      "gain_db": -18,
      "detune_hz": { "min": -0.15, "max": 0.15, "drift_minutes": 5 }
    },
    {
      "type": "noise",
      "color": "pink",
      "gain_db": -30,
      "bandpass": {
        "center_hz": 3000,
        "q": 1.2,
        "lfo": { "rate_hz": 0.004, "depth": 0.4 }
      }
    }
  ]
}
```

Presets store these structures and the CLI merges overrides from flags.

# 9. Web API Draft

All endpoints require authentication. Default binding is localhost only. If exposed over a network, place behind TLS and a reverse proxy.

## 9.1 Routes

### POST /api/render

- Body: configuration JSON matching the engine schema
- Action: renders a full length piece to WAV or a ZIP of stems
- Response:
  - `audio/wav` stream for single mix
  - `application/zip` when `stems=true`
- Server caps:
  - Max duration default 180 minutes
  - Max concurrent renders default 1
  - Rate limits per IP and per session

### POST /api/preview

- Body: same schema as `/api/render`
- Action: renders a short preview with identical seed and settings
- Duration: fixed server side (for example 5 or 10 minutes)
- Response: `audio/wav` stream

### GET /api/presets

- Action: returns preset metadata
- Response: JSON with id, description, default params

### GET /api/health

- Action: readiness check
- Response: JSON status
- May be unauthenticated if bound to localhost only

## 9.2 Request body schema (summary)

The full schema is defined elsewhere. Minimal example:

    {
      "fundamental_hz": 136.1,
      "duration_minutes": 120,
      "sample_rate": 44100,
      "bit_depth": 16,
      "channels": 2,
      "seed": 42,
      "preset": "deep_flow",
      "stems": false,
      "layers": [
        { "type": "drone", "ratio": 1.0, "gain_db": -12 },
        { "type": "harmonic", "ratio": 3.0, "gain_db": -18 },
        { "type": "noise", "color": "pink", "gain_db": -30 }
      ]
    }

## 9.3 Authentication

- Default mode: Basic Auth with bcrypt hashed password stored in environment config
- Optional mode: session login with signed cookies and CSRF on form posts
- Optional mode: Google OAuth restricted to a single allowed email

Requests without valid auth return `401 Unauthorized`.

## 9.4 Transport security

- Bind to `127.0.0.1` by default
- If exposed, require HTTPS via reverse proxy
- Set `Secure`, `HttpOnly`, and `SameSite` cookies where applicable
- Disable CORS unless explicitly needed

## 9.5 Limits and quotas

- Enforce max duration, max sample rate, and bit depth
- Cap file size by duration and format
- One active render per user by default
- Rate limit: for example 5 requests per minute per IP

## 9.6 Errors

- `400 Bad Request` invalid schema or parameters
- `401 Unauthorized` missing or invalid auth
- `413 Payload Too Large` duration or config exceeds limits
- `429 Too Many Requests` rate limit exceeded
- `500 Internal Server Error` unexpected failure

Error body shape:

    { "error": "message", "code": "STRING_CODE" }

## 9.7 Logging

- Access logs: user, route, response status, duration
- Job logs: configuration hash, seed, timing, output path
- No secrets or raw passwords in logs

## 9.8 Example calls

Render full mix:

    curl -u user:pass \
      -X POST http://127.0.0.1:8000/api/render \
      -H "Content-Type: application/json" \
      -o focus_136.wav \
      -d '{"fundamental_hz":136.1,"duration_minutes":120,"preset":"deep_flow","seed":42,"stems":false}'

Preview:

    curl -u user:pass \
      -X POST http://127.0.0.1:8000/api/preview \
      -H "Content-Type: application/json" \
      -o preview.wav \
      -d '{"fundamental_hz":136.1,"preset":"deep_flow","seed":42}'

List presets:

    curl -u user:pass http://127.0.0.1:8000/api/presets

Health:

    curl http://127.0.0.1:8000/api/health

## 9.9 Web UI (optional)

- Minimal HTML form collects frequency, minutes, preset, seed, and layer toggles
- Form POSTs to `/api/render`
- UI is only served to authenticated sessions
- CSRF token included in form if session auth is used

# 10. Authentication and Security

## 10.1 Threat model

- Single user project, but web endpoints must not be exposed without protection
- Risks include disk exhaustion via untrusted requests, resource exhaustion, or exposure of local files

## 10.2 Authentication modes

- Default: Basic Auth with a bcrypt hashed password stored in environment variables or a .env file
- Optional: Session login with signed cookies and CSRF on form posts
- Optional: Google OAuth restricted to a single allowed email

## 10.3 Authorization

- Single role: owner
- All API routes require authentication
- Health endpoint may be unauthenticated if bound to localhost only

## 10.4 Transport security

- Bind server to 127.0.0.1 by default
- If exposed over a network, place behind TLS with Caddy or Nginx
- Enforce HTTPS and secure cookies

## 10.5 Rate limiting and quotas

- Per session and per IP rate limits on render jobs
- Hard cap on concurrent renders, default 1
- Maximum duration and file size limits, defaults 180 minutes and 1.2 GB

## 10.6 File system safety

- All writes confined to a configured output directory
- Sanitize filenames and prevent path traversal
- Optional automatic cleanup policy for older renders

## 10.7 Secrets management

- Use .env for development and environment variables for production
- Never log secrets or full configuration payloads

## 10.8 Logging

- Access logs include user, route, status, and duration
- Job logs include configuration hash, seed, timing, and output path
- No secrets or raw passwords in logs

## 10.9 Backups and recovery

- No automatic uploads
- Optional local snapshot of presets and config with seeds for determinism

## 10.10 Acceptance for security

- All authenticated routes reject unauthenticated requests with 401
- CSRF protection in form based login
- HTTPS enforced when not bound to localhost
- Render duration and size caps enforced server side

# 11. CLI Draft

Commands

    sfe list-presets
    sfe preview --freq 136.1 --minutes 10 --preset deep_flow --seed 42 --stems
    sfe render  --freq 136.1 --minutes 120 --preset deep_flow --seed 42 --stems --sr 44100 --bit 16 --stereo
    sfe explain --preset deep_flow

Notes

- explain prints the resolved layer graph and modulation plan

# 12. Performance and Resource Plan

- Render in chunks of 1 to 10 seconds of audio
- Use NumPy for vectorized synthesis where helpful
- Avoid storing entire output in memory
- Estimated file sizes
  - 2 hours stereo, 44.1 kHz, 16 bit about 600 MB
  - 2 hours mono about 300 MB
- Long renders run as background shell jobs on a local machine or a quiet server

# 13. Quality, Testing, and Validation

- Unit tests for oscillators, LFOs, envelopes, filters, and mixers
- Determinism test: identical inputs and seed produce byte identical output
- Click and pop tests at layer on and off transitions
- Peak level checks to avoid clipping
- Golden sample tests for short renders to guard against regressions
- Security tests for auth, rate limiting, and maximum duration caps

# 14. Security and Privacy

- No external calls during render
- Web API bound to localhost by default
- CORS disabled unless explicitly turned on
- Authentication required for all API routes
- No user uploads in v1

# 15. Tooling and Dependencies

- Python 3.11 or later
- Packages
  - numpy
  - soundfile or wave for writing
  - scipy for filters if preferred over hand rolled biquads
  - typer or argparse for CLI
  - fastapi and uvicorn for optional API
  - passlib for bcrypt hashing
  - python dotenv for local configuration
  - slowapi or equivalent for rate limiting
- No system synths or soundfonts required for v1

# 16. Project Structure

    sfe/
      cli/
        main.py
      core/
        oscillators.py
        envelopes.py
        lfo.py
        filters.py
        mix.py
        layers/
          drone.py
          harmonic.py
          partial.py
          noise.py
        engine.py            # chunk scheduler and stem buses
        presets.py
        seed.py
      io/
        writer.py            # WAV writer, stems, chunk flushing
        naming.py
      web/                   # optional
        api.py               # FastAPI routes
        auth.py              # auth backends and middleware
        templates/           # minimal form if desired
      presets/
        deep_flow_136.json
        bright_wash_528.json
      tests/
    README.md
    LICENSE
    PRD.md

# 17. Roadmap

Milestone 0.1 Prototype

- Single oscillator drone at the fundamental
- Chunked render to mono 44.1 kHz 16 bit WAV
- CLI flags for frequency, minutes, output path

Milestone 0.2 Layers

- Add harmonic layers and gain staging
- Add pink noise layer with bandpass
- Stereo output with fixed pan offsets

Milestone 0.3 Modulation

- Amp LFO and pan LFO per layer
- Simple filter LFO
- Deterministic seed for LFO phase

Milestone 0.4 Evolution

- Long on and off fades for layers
- Detune drift and beating
- Preview command

Milestone 0.5 Stems and Presets

- Separate buses per layer group and ZIP output
- Preset loader and list presets
- Explain command

Milestone 0.6 Web Optional

- FastAPI POST api render and POST api preview
- Minimal HTML form that returns a file
- Authentication middleware enabled by default

Milestone 0.7 Release

- Documentation and examples
- Three starter presets
- First two hour publish to YouTube using the engine

# 18. Future Ideas

- Binaural mode with small left and right offsets to encourage alpha or theta states
- Density envelopes that rise and fall across the piece length
- Nonlinear modulation curves for a more organic feel
- Video pipeline helper that assembles a simple MP4 from a still and the WAV
- Batch generator that renders several seeds at once and retains logs
- Light mastering step: gentle EQ, slow compressor, wide reverb tail
- Simple desktop GUI wrapper using Tauri or Electron if the CLI is not enough
- Optional MIDI export that mirrors the frequency plan at musical approximations
- Hardware controller mapping for live performance

# 19. Risks and Mitigations

- Ear fatigue if spectra are too static  
  Mitigation: ensure slow multi parameter drift and periodic layer swaps

- Beating or detune becomes harsh on headphones  
  Mitigation: clamp depth and rates, provide preset bounds

- Render time is long on laptops  
  Mitigation: allow overnight runs and provide preview renders

- Clipping or unwanted DC offset  
  Mitigation: headroom targets, highpass at 25 to 30 Hz, DC blockers

- Unauthorized access to the web API  
  Mitigation: authentication required by default, local bind, rate limits, TLS when exposed

# 20. Acceptance Criteria for v1

- Running sfe render with a 136.1 Hz fundamental for 120 minutes and a preset named deep_flow with a fixed seed produces a stereo WAV about 600 MB with gentle evolution, no clicks, and levels below 0 dBFS
- Re running the same command yields byte identical output
- sfe preview produces a short segment that matches the first minutes of the full render
- Preset system is documented and ships with at least three audibly distinct presets
- Web API, if enabled, rejects unauthenticated requests and enforces duration caps

# 21. Launch Checklist

- Build and tag v1.0.0
- Commit presets and example commands in README
- Generate one two hour piece and upload to the YouTube channel
- Add the file naming and description template for YouTube
- Update sonicfocusengine.com with links to the first video and the repository
