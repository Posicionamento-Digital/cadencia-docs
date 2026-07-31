# Runbook — recuperar compose files perdidos

> **Contexto:** o `userdel -r luiz` em 30/07 apagou 2 compose files físicos (Lara GCI-GO em `/home/luiz/projetos/gci-go/lara/` e Cadencia Agenda em `/tmp/claude-*/scratchpad/agenda-spike/`).
> **Containers continuam rodando** (Docker daemon guarda config em `/var/lib/docker/`), mas se qualquer um cair não há como `docker compose up`.
> Este runbook mostra como (a) reconstituir o compose file a partir de `docker inspect`, (b) validar, (c) salvar em local seguro.

## Por que fazer

Sem o compose file, você fica dependente do estado atual do container. Se cair:
- `docker restart <container>` funciona (Docker daemon lembra a config).
- Mas se a imagem for removida (`docker image prune`) ou o volume perder (`docker volume rm`), você não tem como rebuild.
- Backup do compose file é o único jeito de reproduzir o stack em outra máquina (ou migrar pra Master).

## Passo a passo

### 1. Identificar o "project" do stack

Cada compose file tem `name:` no topo. Docker rastreia via label `com.docker.compose.project`. Descobrir:

```bash
sudo docker ps --format '{{.Names}}\t{{.Label "com.docker.compose.project"}}' | sort -u
```

Exemplo real na VPS Dev (2026-07-31):
```
cadencia-agenda-app     cadencia-agenda
cadencia-agenda-mysql   cadencia-agenda
lara-api                lara
lara-worker             lara
lara-redis              lara
lara-postgres           lara
pd-motor                pd-motor
```

3 projects: `cadencia-agenda`, `lara`, `pd-motor` (este último tem compose salvo em `/home/felipe/pd-framework/_core/deploy/motor/`).

### 2. Coletar todas as info de cada service

Pra cada container do project, extrair via `docker inspect`:

```bash
# Substituir NOME_CONTAINER
sudo docker inspect NOME_CONTAINER --format '
image: {{.Config.Image}}
command: {{.Config.Cmd}}
entrypoint: {{.Config.Entrypoint}}
restart: {{.HostConfig.RestartPolicy.Name}}
networks: {{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}
ports: {{range $p, $b := .NetworkSettings.Ports}}{{$p}}={{range $b}}{{.HostPort}}{{end}} {{end}}
volumes:{{range .Mounts}}
  {{if eq .Type "volume"}}- {{.Name}}:{{.Destination}}{{else}}- {{.Source}}:{{.Destination}}{{end}}{{end}}
env_count: {{len .Config.Env}}
depends_on: {{index .Config.Labels "com.docker.compose.depends_on"}}
service_name: {{index .Config.Labels "com.docker.compose.service"}}
'
```

### 3. Extrair ENV vars (mascarados)

```bash
sudo docker inspect NOME_CONTAINER --format '{{range .Config.Env}}{{println .}}{{end}}' \
  | sed -E 's/(PASSWORD|SECRET|TOKEN|KEY|_PWD|CREDENTIAL)=.{4,}/\1=***MASK***/g'
```

**Cuidado:** ao escrever o compose reconstituído, NÃO deixar valores reais dos secrets no arquivo. Referenciar via `${VAR_NAME}` e criar `.env` sibling com valores buscados do 1P.

### 4. Descobrir volumes e networks externos

```bash
sudo docker volume ls
sudo docker network ls
```

Se o volume tem nome tipo `<project>-<name>-data` (ex: `lara-postgres-data`), foi criado pelo compose. Se é hash sha256, é anônimo — cuidado.

Marcar volumes e networks como `external: true` no compose reconstituído (já existem, não recriar).

### 5. Montar `docker-compose.yml`

Template:

```yaml
name: <project>

services:
  <service_name>:
    image: <image>
    container_name: <container_name>
    restart: unless-stopped
    ports:
      - "<host>:<container>"
    depends_on:
      <outro_service>:
        condition: service_healthy | service_started
    networks:
      - <network>
    environment:
      VAR1: value_ou_${DEFAULT}
      SECRET_KEY: ${SECRET_KEY}     # buscar do .env
    volumes:
      - <vol_name>:<container_path>
      - <host_path>:<container_path>

  # ... outros services

networks:
  <network>:
    external: true    # se já existir

volumes:
  <vol_name>:
    external: true    # se já existir
```

### 6. Validar (compose config)

```bash
cd /caminho/do/compose/dir
sudo docker compose config    # parse + valida YAML + resolve interpolações
```

Se houver erro de sintaxe, `docker compose config` reclama. Passar aqui não garante que sobe corretamente (envs pode faltar), mas garante que o YAML tá válido.

### 7. Testar rebuild

Simular queda + recover num container. Rodar em horário calmo:

```bash
cd /caminho/do/compose/dir
sudo docker compose stop <service>
sudo docker compose up -d <service>       # deve resubir usando o compose novo
sudo docker logs <container> --tail 20    # verificar que subiu
```

Se falhou, ajustar compose e retentar. Volumes persistentes (`external: true`) NÃO são apagados pelo `stop` — dados preservados.

### 8. Salvar em local seguro

**Recomendo estrutura:**
```
/home/felipe/compose/
├── lara-gci-go/
│   ├── docker-compose.yml    (compose reconstituído)
│   ├── .env                  (secrets carregados do 1P, chmod 600)
│   └── README.md             (contexto: origem, quando reconstituído, gotchas)
├── cadencia-agenda/
│   ├── docker-compose.yml
│   ├── .env
│   └── README.md
```

**Não commitar** os `.env` no framework. Apenas o `docker-compose.yml` (sem valores reais) + o `README.md` podem ser commitados como referência histórica em `times/infra/docs/vps-dev/composes/` se fizer sentido.

## Compose files já reconstituídos neste doc

- **Lara GCI-GO:** ver `stack-lara-gci-go.md` §"Compose file — RECONSTITUÍDO"
- **Cadencia Agenda:** ver `stack-cadencia-agenda.md` §"Compose file — RECONSTITUÍDO"
- **PD Motor:** vivo em `/home/felipe/pd-framework/_core/deploy/motor/compose.yml` (nunca sumiu — sobreviveu pq vive dentro do repo do framework do Felipe, não em `/home/luiz/`)

## Prevenção — evitar perder compose de novo

1. **Nunca guardar compose de stack persistente em `/home/<user>/` ou `/tmp/`** — usar `/opt/<stack>/` (owned by root) ou `/home/felipe/compose/` (mais durável que /home/luiz/ agora que só Felipe é dev).
2. **Se stack é da PD, commitar o compose no framework** — `_core/deploy/<stack>/compose.yml` (padrão do Motor). Aí perde local = clone do framework restaura.
3. **Backup diário automático** dos composes vivos:
   ```bash
   # cron root
   0 3 * * * for c in $(docker ps --format '{{.Label "com.docker.compose.project.config_files"}}' | sort -u); do \
              [ -f "$c" ] && cp "$c" "/root/compose-backups/$(basename $(dirname $c))-$(date +\%Y\%m\%d).yml"; \
             done
   ```

## Refs

- `docs/vps-dev/README.md` — visão geral VPS Dev
- `docs/vps-dev/stack-lara-gci-go.md` — compose reconstituído Lara
- `docs/vps-dev/stack-cadencia-agenda.md` — compose reconstituído Agenda
- `_core/deploy/motor/compose.yml` — exemplo de compose persistido no framework
