/**
 * Vercel Edge Middleware — cadencia-docs
 *
 * Protege todas as rotas: só admin/super_admin do Cadencia pode acessar.
 * Fluxo: lê cookie Supabase → valida JWT → checa role → passa ou redireciona pro login.
 *
 * Env vars necessárias (configurar no Vercel dashboard):
 *   SUPABASE_URL             = https://<ref>.supabase.co
 *   SUPABASE_ANON_KEY        = chave anon do projeto
 *   SUPABASE_PROJECT_REF     = ref do projeto (parte do nome do cookie)
 *   CADENCIA_APP_URL         = https://app.cadencia.app.br
 */
import { next } from "@vercel/edge";

export const config = {
  // Protege tudo exceto assets estáticos do MkDocs
  matcher: ["/((?!assets/|search/|404\\.html|sitemap\\.xml|robots\\.txt).*)"],
};

const SUPABASE_URL = process.env.SUPABASE_URL!;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY!;
const PROJECT_REF = process.env.SUPABASE_PROJECT_REF!;
const APP_URL = process.env.CADENCIA_APP_URL ?? "https://app.cadencia.app.br";

/** Lê cookie por nome do header Cookie. */
function getCookieValue(header: string | null, name: string): string | null {
  if (!header) return null;
  for (const part of header.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key.trim() === name) return decodeURIComponent(rest.join("="));
  }
  return null;
}

/**
 * Supabase SSR fragmenta o cookie em partes (.0, .1, …) quando o JWT é grande.
 * Esta função reconstrói o valor completo.
 */
function readSupabaseCookie(header: string | null): string | null {
  const base = `sb-${PROJECT_REF}-auth-token`;
  const direct = getCookieValue(header, base);
  if (direct) return direct;

  const chunks: string[] = [];
  for (let i = 0; i < 10; i++) {
    const chunk = getCookieValue(header, `${base}.${i}`);
    if (!chunk) break;
    chunks.push(chunk);
  }
  return chunks.length > 0 ? chunks.join("") : null;
}

export default async function middleware(request: Request): Promise<Response> {
  const cookieHeader = request.headers.get("cookie");
  const raw = readSupabaseCookie(cookieHeader);

  if (!raw) return redirectToLogin(request.url);

  let accessToken: string;
  try {
    const session = JSON.parse(raw);
    accessToken = session.access_token;
    if (!accessToken) return redirectToLogin(request.url);
  } catch {
    return redirectToLogin(request.url);
  }

  // Valida o token e obtém o user via Supabase Auth API
  const userRes = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      apikey: SUPABASE_ANON_KEY,
    },
  });

  if (!userRes.ok) return redirectToLogin(request.url);
  const user: { id: string } = await userRes.json();

  // Checa role em user_tenant_roles (RLS retorna só as linhas do próprio usuário)
  const roleRes = await fetch(
    `${SUPABASE_URL}/rest/v1/user_tenant_roles?user_id=eq.${user.id}&role=in.(admin,super_admin)&limit=1&select=role`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        apikey: SUPABASE_ANON_KEY,
      },
    }
  );

  if (!roleRes.ok) return redirectToLogin(request.url);
  const roles: { role: string }[] = await roleRes.json();

  if (!roles || roles.length === 0) {
    return new Response(
      "Acesso negado. Apenas administradores Cadencia podem acessar esta área.",
      { status: 403, headers: { "content-type": "text/plain; charset=utf-8" } }
    );
  }

  return next();
}

function redirectToLogin(currentUrl: string): Response {
  const loginUrl = new URL(`${APP_URL}/auth/login`);
  loginUrl.searchParams.set("next", currentUrl);
  return Response.redirect(loginUrl.toString(), 302);
}
