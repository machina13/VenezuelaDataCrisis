-- Issue #200: Grants mínimos para que el rol anon (via publishable key de Supabase)
-- pueda escribir directo a Supabase desde el scraper en GitHub Actions.
--
-- ADR 0001 define Supabase como plano interno (nunca recibe tráfico público).
-- El público se sirve desde Cloudflare Worker + D1; el riesgo queda acotado
-- solo si se cumplen las preconditions de abajo.
--
-- Preconditions operativas:
-- - SUPABASE_PUBLISHABLE_KEY vive solo como variable protegida de GitHub Actions; no se
--   distribuye a clientes públicos ni se embebe en el Worker/API pública.
-- - Si el proyecto habilita RLS en estas tablas, deben existir policies que
--   permitan exactamente estas operaciones al rol anon usado por el scraper.
-- - Si la publishable key se expone fuera de CI, NO aplicar este modelo: usar
--   un rol/JWT dedicado para ingest antes de habilitar escritura.
--
-- Verificación post-deploy sugerida:
--   SELECT grantee, table_name, privilege_type
--   FROM information_schema.role_table_grants
--   WHERE grantee = 'anon'
--     AND table_name IN ('aportes','source_watermarks','sources')
--   ORDER BY table_name, privilege_type;
--
-- Ejecutar en el SQL Editor de Supabase antes del primer deploy del PR.

GRANT INSERT, UPDATE ON public.aportes TO anon;
GRANT INSERT, UPDATE ON public.source_watermarks TO anon;
GRANT SELECT ON public.sources TO anon;
