-- One database and LOGIN role per service. Re-running updates passwords without dropping data.
SELECT format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD %L', role_name, role_password)
FROM (VALUES
  ('jane_handler_runtime', :'handler_runtime_password'),
  ('jane_orchestrator', :'orchestrator_password'),
  ('jane_registry', :'registry_password'),
  ('jane_llm', :'llm_password'),
  ('jane_assistant', :'assistant_password'),
  ('jane_storage_results', :'storage_results_password')
) AS roles(role_name, role_password)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name)
\gexec

SELECT format('ALTER ROLE %I WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD %L', role_name, role_password)
FROM (VALUES
  ('jane_handler_runtime', :'handler_runtime_password'),
  ('jane_orchestrator', :'orchestrator_password'),
  ('jane_registry', :'registry_password'),
  ('jane_llm', :'llm_password'),
  ('jane_assistant', :'assistant_password'),
  ('jane_storage_results', :'storage_results_password')
) AS roles(role_name, role_password)
\gexec

SELECT format('CREATE DATABASE %I OWNER %I', name, name)
FROM (VALUES
  ('jane_handler_runtime'), ('jane_orchestrator'), ('jane_registry'),
  ('jane_llm'), ('jane_assistant'), ('jane_storage_results')
) AS databases(name)
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = name)
\gexec

SELECT format('ALTER DATABASE %I OWNER TO %I', name, name)
FROM (VALUES
  ('jane_handler_runtime'), ('jane_orchestrator'), ('jane_registry'),
  ('jane_llm'), ('jane_assistant'), ('jane_storage_results')
) AS databases(name)
\gexec

-- PostgreSQL grants CONNECT and TEMPORARY to PUBLIC by default. Revoke both, including
-- the bootstrap database, so a service credential cannot inspect another service database.
SELECT format('REVOKE ALL ON DATABASE %I FROM PUBLIC', datname)
FROM pg_database
WHERE datname IN (
  'postgres', 'template1', 'jane', 'jane_handler_runtime', 'jane_orchestrator',
  'jane_registry', 'jane_llm', 'jane_assistant', 'jane_storage_results'
)
\gexec
