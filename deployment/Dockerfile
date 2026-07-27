FROM node:22.17.0-bookworm-slim AS node-dependencies

RUN apt-get update \
    && apt-get install --no-install-recommends -y python3 make g++ \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build

COPY Modules/Severity-1.1.0/package.json Modules/Severity-1.1.0/package-lock.json /build/severity/
COPY Modules/Medical-History-1.0.0/package.json Modules/Medical-History-1.0.0/package-lock.json /build/medical-history/
COPY Modules/DDI-Checker-1.2.0/package.json Modules/DDI-Checker-1.2.0/package-lock.json /build/ddi-checker/
RUN npm ci --omit=dev --prefix /build/severity \
    && npm ci --omit=dev --prefix /build/medical-history \
    && npm ci --omit=dev --prefix /build/ddi-checker

FROM python:3.13.5-slim-bookworm AS python-dependencies

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    bcrypt \
    PyJWT \
    pydantic \
    httpx \
    lxml \
    "psycopg[binary]"

FROM python:3.13.5-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NGINX_ENTRYPOINT_QUIET_LOGS=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl nginx tini \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-dependencies /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=python-dependencies /usr/local/bin /usr/local/bin
COPY --from=node-dependencies /usr/local/bin/node /usr/local/bin/node
COPY --from=node-dependencies /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

WORKDIR /opt
COPY deployment /opt/deployment
COPY contracts /opt/contracts
ENV PYTHONPATH=/opt:/opt/modules/treatment-plan
COPY Modules/Authentication-1.1.0 /opt/modules/authentication
COPY Modules/Dashboard-1.2.0 /opt/modules/dashboard
COPY Modules/Add-New-Patient-1.1.0 /opt/modules/add-new-patient
COPY Modules/Diagnosis-1.2.0 /opt/modules/diagnosis
COPY Modules/Severity-1.1.0 /opt/modules/severity
COPY Modules/Medical-History-1.0.0 /opt/modules/medical-history
COPY Modules/DDI-Checker-1.2.0 /opt/modules/ddi-checker
COPY Modules/BN-Manager-v.1.1.0/BN-Manager-v.1.1.0 /opt/modules/bn-manager
COPY Modules/Treatment-Plan /opt/modules/treatment-plan
COPY Modules/Suicide-Risk-1.0.0 /opt/modules/suicide-risk

COPY --from=node-dependencies /build/severity/node_modules /opt/modules/severity/node_modules
COPY --from=node-dependencies /build/medical-history/node_modules /opt/modules/medical-history/node_modules
COPY --from=node-dependencies /build/ddi-checker/node_modules /opt/modules/ddi-checker/node_modules

RUN mkdir -p /var/lib/insight/authentication \
    /var/lib/insight/dashboard \
    /var/lib/insight/add-new-patient \
    /var/lib/insight/diagnosis \
    /var/lib/insight/severity \
    /var/lib/insight/medical-history \
    /var/lib/insight/ddi-checker \
    /var/lib/insight/bn-manager \
    /var/lib/insight/treatment-plan \
    /var/lib/insight/suicide-risk \
    /var/cache/nginx \
    /var/log/nginx \
    /run/nginx

EXPOSE 8080
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=10s --timeout=3s --start-period=30s --retries=6 \
    CMD curl --fail --silent --show-error http://127.0.0.1:8080/readyz >/dev/null || exit 1
# tini -- python /opt/deployment/supervisor.py
ENTRYPOINT ["tini", "--", "python", "/opt/deployment/supervisor.py"]
