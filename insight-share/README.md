# insight-share

Single-click Docker bundle for the **insight-unified** container image. Contains
the prebuilt image, the unified `docker-compose.yaml`, runtime support files,
and a launcher script that brings the whole stack up on `http://127.0.0.1:8080`.

This bundle was built from the `insight` repository at commit with the
following fixes applied:

- `deployment/nginx.conf`: added `location /dashboard` proxy to the dashboard
  module (internal port 8102). Before this fix, browser navigation to
  `/dashboard/admin` or `/dashboard/user` (the redirect targets returned by the
  Authentication login page) fell through to the nginx static root and returned
  `404 /usr/share/nginx/html/dashboard/admin`.
- `Modules/Dashboard-1.2.0/dashboard_backend/main.py`: added a SPA fallback
  route `GET /dashboard/{full_path:path}` that serves `index.html` for unknown
  client-side routes (e.g. `/dashboard/admin`) while still serving real static
  files (`dashboard.js`, `styles.css`) from the mounted StaticFiles root.
- `Modules/Dashboard-1.2.0/test_dashboard_backend.py`: added a regression
  test `test_dashboard_spa_routes_serve_index_html` covering all three SPA
  entry paths plus real static-file serving.

## Bundle contents

| File | Purpose |
| --- | --- |
| `insight-unified.image.tar` | The prebuilt Docker image (`insight-unified:local-build`). |
| `SHA256SUMS` | Integrity checksum for the prebuilt image archive. |
| `docker-compose.yaml` | Unified stack: one container + 9 named volumes; binds `127.0.0.1:8080`. |
| `run.cmd` / `run.ps1` | Windows launcher. Verifies and loads the image, creates a persistent local secret, waits for health, then opens Insight. |
| `run.sh` | Linux/macOS launcher with equivalent startup behavior. |
| `nginx.conf` | In-container nginx gateway (modules on ports 8101-8109). |
| `nginx-vps.conf` | Optional host-edge TLS + security-header nginx config. |
| `supervisor.py` | In-container PID 1 (via `tini`) that runs nginx + all module backends. |
| `manifest.json` | Deployment manifest: ports, volumes, env, per-module command. |
| `Dockerfile` | The Dockerfile used to rebuild the image (already built, included for reference). |
| `insight-unified-container.service` | Optional systemd unit for host reboot recovery. |
| `secrets-empty/` | Empty mount target for `/run/secrets` (read-only). Replace with real secrets in production. |

## Requirements

- Docker 23+ (Compose v2 included)
- ~1 GB free disk for the loaded image
- Linux, macOS, or Windows with Docker Desktop. The container binds to
  `127.0.0.1:8080`; for remote hosts put a TLS-terminating proxy in front
  (see `nginx-vps.conf`).

## Quick start

### Windows

1. Install and start Docker Desktop using Linux containers.
2. Extract `insight-windows-amd64.zip`.
3. Double-click `run.cmd`.

PowerShell alternative:

```powershell
.\run.ps1
```

The first launch verifies and imports the bundled image, starts all services,
waits for readiness, and opens Insight in the default browser. No source build
or network download is required after obtaining the ZIP.

### Linux / macOS

```bash
tar -xzf insight-share.tar.gz
cd insight-share
./run.sh
```

You should see:

```
=== insight-unified is starting ===
Dashboard : http://127.0.0.1:8080/dashboard/
Login     : http://127.0.0.1:8080/modules/authentication  (Admin / Admin)
Readiness : http://127.0.0.1:8080/readyz
```

The launcher waits for startup and health checks to pass. Then:

1. Open http://127.0.0.1:8080/modules/authentication
2. Sign in with `Admin` / `Admin`
3. The app redirects to `/dashboard/admin` and the workspace loads.

The admin password is the seeded default. For anything beyond a local demo,
rotate it via `POST /api/auth/password/change` after first login and set a
real `AUTH_JWT_SECRET` (≥32 bytes) via environment.

## Verifying the fix

The previously failing flow was:

1. Admin logs in at `/modules/authentication`.
2. Auth frontend calls `window.location.assign('/dashboard/admin')` (see
   `Authentication-1.1.0/static/index.html`).
3. Browser GET `/dashboard/admin` → nginx served `/usr/share/nginx/html/dashboard/admin` → `404`.

After this bundle:

```
GET /dashboard/admin  ->  200 OK  (index.html SPA shell)
GET /dashboard/user   ->  200 OK  (index.html SPA shell)
GET /dashboard/styles.css      ->  200 OK  (real static file)
GET /dashboard/dashboard.js  ->  200 OK  (real static file)
```

Reproduced end-to-end:

```bash
JAR=/tmp/cookies.txt
csrf=$(curl -s -c $JAR http://127.0.0.1:8080/api/auth/csrf)
TOKEN=$(echo "$csrf" | sed -E 's/.*"csrf_token":"([^"]+)".*/\1/')
curl -s -b $JAR -c $JAR -X POST http://127.0.0.1:8080/api/auth/login \
  -H "content-type: application/json" -H "x-csrf-token: $TOKEN" \
  -d '{"username":"Admin","password":"Admin","role":"admin"}'
# -> {"ok":true,"next":"/dashboard/admin",...}
curl -s -o /dev/null -w "/dashboard/admin -> HTTP %{http_code}\n" \
  -b $JAR http://127.0.0.1:8080/dashboard/admin
# -> /dashboard/admin -> HTTP 200
```

## Operations

```bash
./run.sh         # start / re-apply
./run.sh logs    # tail container logs (nginx + 9 module Python/Node services)
./run.sh down    # stop and remove container (volumes are preserved)
```

Persistent module data lives in named Docker volumes
(`authentication-data`, `dashboard-data`, …, `treatment-plan-data`). They
survive `./run.sh down`. Wipe with `docker volume ls | awk '/insight-share_/{print $2}' | xargs -r docker volume rm`.

## Customizing runtime

`run.sh` reads these env vars (override before running):

| Variable | Default | Notes |
| --- | --- | --- |
| `AUTH_JWT_SECRET` | generated once in `.env` | MUST be ≥32 bytes and differ from the dev default. |
| `AUTH_BASE_URL` | `http://127.0.0.1:8101` | Auth module base URL seen by the dashboard backend inside the container. |
| `TP_AUTHENTICATION_SESSION_URL` | `$AUTH_BASE_URL/api/auth/session` | Treatment Plan auth session check. |
| `TP_TRUSTED_INTERNAL_ORIGINS` | `http://127.0.0.1:8080` | Treatment Plan trusted origin. |
| `TP_ENV` | `development` | Set to `production` to enable strict modes. |
| `INSIGHT_SECRETS_DIR` | `./secrets-empty` | Mount target for `/run/secrets`. |

## Production notes

This bundle is a local demonstration artifact. Before production:

1. Replace the seeded `Admin`/`Admin` credentials (login then
   `POST /api/auth/password/change`).
2. Set a strong `AUTH_JWT_SECRET` via a secrets manager — do not rely on the
   random default generated by `run.sh`.
3. Put a TLS-terminating host nginx in front, using `nginx-vps.conf` as the
   template (TLSv1.2/1.3, HSTS, CSP, no-sniff, DENY framing).
4. Record the immutable image digest (`docker image inspect
   insight-unified:local-build --format '{{index .Id 0}}'`) and use it with
   the systemd unit (`insight-unified-container.service`) for reboot recovery.
5. Sweep image for HIGH/CRITICAL CVEs before promotion:
   `trivy image insight-unified:local-build --exit-code 1 --severity HIGH,CRITICAL`.
