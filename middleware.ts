/**
 * Vercel Edge Middleware — cadencia-docs
 *
 * Protege todas as rotas: só admin/super_admin do Cadencia pode acessar.
 *
 * Dois fluxos de entrada:
 *  1. ?access_token=<supabase_jwt>  → valida, seta cookie docs_session, redireciona limpo
 *  2. Cookie docs_session presente   → valida, passa
 *
 * Env vars necessárias:
 *   SUPABASE_URL             = https://<ref>.supabase.co
 *   SUPABASE_ANON_KEY        = chave anon do projeto
 *   CADENCIA_APP_URL         = https://cadencia.app.br
 */
import { next } from "@vercel/edge";

export const config = {
  matcher: ["/((?!assets/|search/|404\\.html|sitemap\\.xml|robots\\.txt).*)"],
};

const SUPABASE_URL = process.env.SUPABASE_URL!.trim();
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY!.trim();
const APP_URL = (process.env.CADENCIA_APP_URL ?? "https://cadencia.app.br").trim();

function getCookieValue(header: string | null, name: string): string | null {
  if (!header) return null;
  for (const part of header.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key.trim() === name) return decodeURIComponent(rest.join("="));
  }
  return null;
}

async function validateTokenAndRole(accessToken: string): Promise<boolean> {
  const userRes = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      apikey: SUPABASE_ANON_KEY,
    },
  });
  if (!userRes.ok) return false;
  const user: { id: string } = await userRes.json();

  const roleRes = await fetch(
    `${SUPABASE_URL}/rest/v1/user_tenant_roles?user_id=eq.${user.id}&role=in.(admin,super_admin)&limit=1&select=role`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        apikey: SUPABASE_ANON_KEY,
      },
    }
  );
  if (!roleRes.ok) return false;
  const roles: { role: string }[] = await roleRes.json();
  return roles.length > 0;
}

export default async function middleware(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const accessToken = url.searchParams.get("access_token");

  // Fluxo 1: token via URL (vindo do cadencia-app /api/app/admin/docs-token)
  if (accessToken) {
    const ok = await validateTokenAndRole(accessToken);
    if (!ok) return redirectToLogin(request.url);

    // Redireciona para URL limpa (sem token) e seta cookie próprio
    url.searchParams.delete("access_token");
    const cleanUrl = url.toString();
    const res = Response.redirect(cleanUrl, 302);
    res.headers.set(
      "Set-Cookie",
      `docs_session=${encodeURIComponent(accessToken)}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=3600`
    );
    return res;
  }

  // Fluxo 2: cookie docs_session (sessão já estabelecida)
  const cookieHeader = request.headers.get("cookie");
  const sessionToken = getCookieValue(cookieHeader, "docs_session");

  if (sessionToken) {
    const ok = await validateTokenAndRole(sessionToken);
    if (ok) return next();
  }

  return redirectToLogin(request.url);
}

function redirectToLogin(currentUrl: string): Response {
  const loginUrl = new URL(`${APP_URL}/auth/login`);
  loginUrl.searchParams.set("next", currentUrl);
  return Response.redirect(loginUrl.toString(), 302);
}
