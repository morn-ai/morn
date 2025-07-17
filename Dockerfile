FROM hezhangjian/base:node AS frontend-builder

WORKDIR /home/morn/web

COPY web/ ./

RUN npm install -g pnpm && pnpm install --frozen-lockfile && pnpm build

FROM hezhangjian/base:python

RUN useradd --create-home --shell /bin/bash morn && chown -R morn:morn /home/morn

USER morn

RUN pip install --no-cache-dir uv

WORKDIR /home/morn

COPY --chown=morn:morn pyproject.toml ./
COPY --chown=morn:morn app/ ./app/
COPY --chown=morn:morn conf/ ./conf/

COPY --from=frontend-builder --chown=morn:morn /home/morn/web/dist ./web/dist

CMD ["uvicorn", "app.app:app"]
