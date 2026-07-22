/**
 * Vercel Edge Middleware — cadencia-docs
 *
 * Regra de acesso:
 *   /comercial/programa-revenda/* → member, admin, owner, super_admin
 *   Resto do site               → admin, owner, super_admin
 */
import { next } from "@vercel/edge";

export const config = {
  matcher: ["/((?!assets/|search/|404\\.html|sitemap\\.xml|robots\\.txt).*)"],
};

const SUPABASE_URL = process.env.SUPABASE_URL!;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY!;
const SUPABASE_SERVICE_ROLE = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const PROJECT_REF = process.env.SUPABASE_PROJECT_REF!;
const APP_URL = process.env.CADENCIA_APP_URL ?? "https://cadencia.app.br";

const MEMBER_PATHS = ["/comercial/programa-revenda"];

function isAllowedForMember(pathname: string): boolean {
  return MEMBER_PATHS.some((p) => pathname === p || pathname.startsWith(p + "/"));
}

function getCookieValue(header: string | null, name: string): string | null {
  if (!header) return null;
  for (const part of header.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key.trim() === name) return decodeURIComponent(rest.join("="));
  }
  return null;
}

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

function redirectToLogin(currentUrl: string): Response {
  const loginUrl = new URL(`${APP_URL}/auth/login`);
  loginUrl.searchParams.set("next", currentUrl);
  return new Response(null, {
    status: 302,
    headers: { Location: loginUrl.toString() },
  });
}

export default async function middleware(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const pathname = url.pathname;

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

  const userRes = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
    headers: { Authorization: `Bearer ${accessToken}`, apikey: SUPABASE_ANON_KEY },
  });
  if (!userRes.ok) return redirectToLogin(request.url);
  const user: { id: string } = await userRes.json();

  const rolesIn = isAllowedForMember(pathname)
    ? "member,admin,owner,super_admin"
    : "admin,owner,super_admin";

  // Lookup de role com service_role: RLS de user_tenant_roles tem recursão
  // (policy super_admin faz SELECT na própria tabela). JWT do usuário já foi
  // validado acima via /auth/v1/user — o lookup privilegiado é só p/ ler o role.
  const roleRes = await fetch(
    `${SUPABASE_URL}/rest/v1/user_tenant_roles?user_id=eq.${user.id}&role=in.(${rolesIn})&limit=1&select=role`,
    { headers: { Authorization: `Bearer ${SUPABASE_SERVICE_ROLE}`, apikey: SUPABASE_SERVICE_ROLE } }
  );
  if (!roleRes.ok) return redirectToLogin(request.url);
  const roles: { role: string }[] = await roleRes.json();

  if (!roles || roles.length === 0) {
    return new Response("Acesso negado.", {
      status: 403,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  }

  return next();
}
