# Cloudflare Tunnel — expor Filebrowser via HTTPS público sem abrir porta

## O que é

Serviço da Cloudflare que cria um túnel outbound do CAIXA1 pros edge nodes da CF — sem abrir porta 80/443 no roteador, sem NAT, sem lidar com CGNAT do provedor de internet. TLS gerenciado pela CF edge (Universal SSL). DDoS protection incluso. Grátis (tier free).

No CAIXA1: expõe `http://127.0.0.1:8090` (Filebrowser local) como `https://cloud.cadencia.app.br` público.

## Como funciona conceitualmente

**Modelo:** reverse tunnel outbound-initiated.

1. `cloudflared.exe` roda no CAIXA1 como serviço Windows
2. Ao iniciar, abre 4 conexões QUIC (UDP/443) pros edge nodes CF mais próximos (no caso, São Paulo: gru02, gru07, gru11, gru18)
3. Conexões ficam persistentes (long-poll)
4. Quando cliente externo bate em `https://cloud.cadencia.app.br`:
   - CF edge recebe request HTTPS
   - Termina TLS na edge (com cert Universal SSL)
   - Consulta config do tunnel: hostname `cloud.cadencia.app.br` → serviço `http://127.0.0.1:8090`
   - Encapsula request e manda pela conexão QUIC pro `cloudflared` local
   - `cloudflared` faz HTTP local pro Filebrowser
   - Response volta pelo mesmo caminho reverso

**Consequências:**
- Zero porta aberta no roteador (nada listening publicamente na CAIXA1)
- Zero exposição de IP público
- HTTPS "grátis" (cert é da CF, sem Let's Encrypt local)
- Cliente cai em POP CF mais próximo dele → latência baixa
- Se CAIXA1 desligar → tunnel morre → CF retorna 502 (não expõe erro do backend)

## Config atual

| Campo | Valor |
|---|---|
| Binário | `C:\Tools\cloudflared\cloudflared.exe` (v2026.7.3) |
| Nome tunnel | `caixa1-cloud` |
| ID tunnel | `447af324-a26d-4698-a8ac-231560fa1280` |
| Hostname público | `cloud.cadencia.app.br` |
| CNAME target | `447af324-a26d-4698-a8ac-231560fa1280.cfargotunnel.com` (proxied) |
| Serviço backend | `http://127.0.0.1:8090` (Filebrowser) |
| Serviço Windows | `CloudflaredTunnel` (nssm, start automatic) |
| Logs | `C:\Tools\cloudflared\{stdout,stderr}.log` |
| Tunnel token | 1P vault `Hosts` item `Cloudflare Tunnel caixa1-cloud` (regerável via API) |

## API Cloudflare — 2 tokens complementares

**Descoberta operacional importante (DEV-1732):** um único API token não cobre tudo. Precisa **2 tokens** com permissões complementares:

| Token 1P | Vault | Campo | Permissão | Uso |
|---|---|---|---|---|
| `Cloudfare` (typo intencional preservado) | Hosts | `credencial` | Account > Cloudflare Tunnel > Edit | Criar/gerenciar tunnel + ingress + token de runtime |
| `Cloudflare - API Token + Zones` | Hosts | `api_token` | Zone > DNS > Edit | Criar/atualizar CNAME `cloud.cadencia.app.br` |

Se tentar usar só `api_token` pra criar tunnel: **403 Forbidden** (sem permissão Account.Tunnel). Se tentar usar só `credencial` pra DNS: **401 Authentication error** (sem permissão Zone).

Script `install-cloudflared-tunnel.ps1` lê os dois separadamente e usa cada um no endpoint apropriado.

## Fluxo do install (idempotente)

`install-cloudflared-tunnel.ps1` faz tudo via API — sem `cloudflared tunnel login` (não precisa browser interativo):

1. **Le 2 tokens** do 1P (sem imprimir valor)
2. **Descobre account ID** via `GET /zones/<zoneId>` (metadata da zone tem account.id)
3. **Lista tunnels** — se `caixa1-cloud` já existe, reusa; senão cria com `POST /accounts/<id>/cfd_tunnel`
4. **Gera tunnel run token** via `GET /accounts/<id>/cfd_tunnel/<id>/token`
5. **Salva token no 1P** (item `Cloudflare Tunnel caixa1-cloud`)
6. **Configura ingress** via `PUT /accounts/<id>/cfd_tunnel/<id>/configurations`:
   ```json
   {
     "config": {
       "ingress": [
         {"hostname": "cloud.cadencia.app.br", "service": "http://127.0.0.1:8090"},
         {"service": "http_status:404"}
       ]
     }
   }
   ```
7. **DNS CNAME** via `POST /zones/<zoneId>/dns_records` (proxied=true)
8. **Registra serviço Windows** via nssm apontando pra `cloudflared.exe tunnel run --token <tokenRuntime>`
9. **Start service** + espera ~15s + testa `https://cloud.cadencia.app.br`

## Operação

### Verificar status

```powershell
Get-Service CloudflaredTunnel
# Status esperado: Running

Get-Content C:\Tools\cloudflared\stderr.log -Tail 30
# Esperado: "Registered tunnel connection connIndex=X ... location=gruXX protocol=quic"
```

### Reiniciar tunnel

```powershell
Restart-Service CloudflaredTunnel
```

Reconecta as 4 conexões QUIC em ~5s. Não interrompe ingress se rebalance rápido.

### Rotacionar tunnel token (não invalida hostname)

```powershell
powershell -File _shared\backup-caixa1\install-cloudflared-tunnel.ps1
```

Script é idempotente — regenera token, atualiza 1P + serviço, mantém tunnel/hostname/DNS. Cliente externo não percebe.

### Testar HTTPS externo

```powershell
curl -sSL -o NUL -w "http: %{http_code}\n" https://cloud.cadencia.app.br
# Esperado: http: 200
```

Se der TLS handshake failed logo após criar hostname novo: aguarda 5-15 min (Universal SSL propagação).

## Gotchas conhecidos

### API 403 mesmo com token "válido"
Token `api_token` de `Cloudflare - API Token + Zones` NÃO tem permissão Account.Tunnel. Precisa o token do item `Cloudfare` (typo, vault Hosts, campo `credencial`). Documentado no script.

### Universal SSL propagação
Novo hostname (via `dns_records` CNAME) leva 5-15 min pra ter cert emitido na edge CF. Antes disso: HTTPS falha com TLS handshake failed OU 404 do próprio CF.

### PowerShell 5.1 + Cloudflare edge
`Invoke-WebRequest` no PS 5.1 default usa TLS 1.0/1.1 → CF rejeita. Se precisar testar de dentro da CAIXA1, use `curl` (que faz TLS 1.3) ou force `[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12`.

### QUIC vs HTTP/2 fallback
`cloudflared` tenta QUIC primeiro (UDP/443). Se firewall/roteador bloquear UDP, cai automático pra HTTP/2 sobre TCP/443. No CAIXA1: QUIC funciona (config verificada em `Get-Content stdout.log` — "protocol=quic").

### 1 tunnel, N hostnames
Um único tunnel `caixa1-cloud` pode servir N hostnames (`cloud.cadencia.app.br`, `admin.cadencia.app.br`, etc). Basta adicionar entries no ingress + criar CNAMEs. Não precisa criar tunnel separado por serviço.

## Adicionar hostname novo (ex: expor outro serviço)

1. Edit ingress no dashboard CF OU via API: adicionar `{"hostname": "outro.cadencia.app.br", "service": "http://127.0.0.1:8091"}`
2. Criar DNS CNAME `outro.cadencia.app.br` → `447af324-...cfargotunnel.com` (mesmo do atual)
3. Serviço `outro` na porta 8091 tem que estar rodando
4. Aguardar Universal SSL (5-15 min)

## Tokens vazados durante debug (follow-up conhecido)

Durante F5 (2026-08-09), 2 tokens foram expostos no log por comando `Format-Table` de item 1P que revelou campos STRING (não CONCEALED). Felipe ciente, rotação fica pro final:
- `api_token` de `Cloudflare - API Token + Zones` — expôs `cfut_jJq...`
- `credencial` de `Cloudfare` — expôs (indireto via test script)
- notesPlain de `Cloudfare` — expõe exemplo `cfat_kQ3jx...` que pode ser real

Rotacionar via dashboard Cloudflare + atualizar 1P + rodar `install-cloudflared-tunnel.ps1` pra regenerar tunnel token com novo CF token.

## Refs

- Docs Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
- Script install: `_shared/backup-caixa1/install-cloudflared-tunnel.ps1`
- Filebrowser (backend do tunnel): `_shared/backup-caixa1/docs/filebrowser.md`
- Issue F5: DEV-1732
