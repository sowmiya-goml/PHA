# Codebase Review – PHA (Health Foundary) Backend

Date: 2025-09-23

## Executive Summary
This backend is a FastAPI-based service organized into clear layers (API controllers, services, schemas/models, DB/session, and core config). AWS Bedrock (Anthropic Claude via bedrock-runtime) is used to synthesize SQL (or read-only queries) from natural language, guided by a live-extracted, unified database schema. There are routes to generate queries and optionally execute them against the connected database with safety checks. Overall structure is coherent and test coverage exists via several integration scripts. A few improvements around robustness, security, logging, and Bedrock response handling are recommended.

---

## How “Bedrock -> Execute -> Fetch Data” Works

### 1) Configuration and Environment
- src/core/config.py
  - Loads environment variables from .env (root or config/.env) via python-dotenv
  - Exposes AWS credentials, Bedrock model ID, MongoDB Atlas URL, server ports, and safety limits
  - Key variables:
    - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
    - BEDROCK_MODEL_ID (default: anthropic.claude-3-5-sonnet-20241022-v2:0)
    - MONGODB_URL (stores database connection documents)

### 2) Storing and Resolving Target Database Connection
- MongoDB stores connection records
  - src/db/session.py: DatabaseManager manages Mongo connection and collection
  - src/services/connection_service.py: CRUD for connections; parsing of connection strings; test utilities

### 3) Two-Step Flow (Schema first, then query)
- This aligns with the preferred two-step approach:
  1) Extract schema for the provided connection_id
  2) Use schema + patient_id + query_type to generate a database-specific read-only query

- Schema extraction (src/services/schema_extraction_service.py)
  - Supports PostgreSQL, MySQL/MariaDB, Oracle, SQL Server, MongoDB, Snowflake
  - Produces a “unified_schema” JSON with:
    - database_info (name/type/host/port, extracted-at)
    - tables[] each with name/type/row_count and columns metadata
    - summary totals
  - Uses DB-specific INFORMATION_SCHEMA/data dictionary queries or sampling (MongoDB) to build column metadata and approximate row counts

### 4) Generating the Query with AWS Bedrock
- src/services/bedrock_service.py
  - Initializes a boto3 client for bedrock-runtime using values from settings
  - generate_healthcare_query(connection_id, query_request, patient_id, ...):
    - Step A: Calls ConnectionService.get_database_schema(connection_id), requiring success and presence of unified_schema
    - Step B: Builds a comprehensive prompt tailored to the detected database type, the unified schema, user query request, optional patient_id, and a safety limit
    - Step C: Calls AWS Bedrock via bedrock-runtime.invoke_model with Anthropic messages format ("anthropic_version": "bedrock-2023-05-31"). Model is settings.BEDROCK_MODEL_ID
    - Step D: Parses response JSON from response['body'].read() and extracts:
      - SQL inside a ```sql fenced block when available, else first SELECT... fallback
      - An “Explanation” block when present
    - Step E: Cleans the SQL (strip markdown, remove comments/extra whitespace)
    - Returns status, cleaned query, explanation, and metadata (model_id, region, database_type, etc.)

### 5) Executing the Generated Query (Optional)
- src/api/healthcare.py exposes two routes:
  - GET /healthcare/generate-query-by-connection
    - Generates a query and returns it (no execution)
  - GET /healthcare/generate-and-execute-query
    - Generates the query (same as above) then executes it against the database

- src/services/database_operation_service.py executes queries safely per DB type:
  - validate_query_safety ensures read-only (SQL must start with SELECT; rejects common dangerous keywords)
  - DB-specific execution behavior:
    - PostgreSQL/MySQL/Snowflake: Auto-add LIMIT if missing
    - SQL Server: Rewrites SELECT to SELECT TOP {limit}
    - Oracle: Wraps with ROWNUM <= {limit}
    - MongoDB: Accepts a JSON-like structure or filter; defaults to patients collection if unspecified
  - Returns a list of DatabaseQueryResult with table_name/query/row_count/data/execution_time_ms

### 6) Error Handling and Safety
- Bedrock client initialization gracefully handles missing credentials
- Bedrock request catches NoCredentialsError and ClientError with structured messages
- Query execution layer validates read-only and injects server-side row limits by dialect
- Timeouts and retry settings exist on database connections; Bedrock invocation currently has no retry/backoff

---

## API Surface and Entry Points
- src/main.py
  - Configures CORS, app lifespan, and includes routers:
    - /connections (database connections management)
    - /healthcare (generate and optionally execute AI-generated queries)
    - /dashboard (patient-oriented data APIs using real DB connections)
    - /route (status/reconnect endpoints)

- Key Healthcare endpoints (src/api/healthcare.py)
  - GET /healthcare/generate-query-by-connection
    - Params: connection_id, patient_id, query_type (comprehensive|clinical|billing|basic)
    - Returns: generated_query, metadata
  - GET /healthcare/generate-and-execute-query
    - Same inputs plus limit
    - Returns: generated_query + execution_results (data) or partial_success with errors

---

## Project Structure Review

Top-level (key files):
- src/main.py – FastAPI app wiring
- src/core/config.py – central settings via env
- src/db/session.py – MongoDB connection and manager (stores DB connection docs)
- src/api/ – route controllers (connections, healthcare, dashboard, routes)
- src/services/ – business logic services:
  - bedrock_service.py – AWS Bedrock integration and prompt/response handling
  - connection_service.py – resolve connections, test connectivity, fetch schema via extractor
  - database_operation_service.py – safe execution of read-only queries across multiple DBs
  - schema_extraction_service.py – multi-DB schema extraction -> unified schema JSON
- src/models/, src/schemas/ – data shapes for persistence and API responses
- src/utils/helpers.py – logging setup and helpers
- tests/ and test_*.py – targeted scripts to validate Bedrock init, simple calls, and the healthcare flow
- docs/development – additional architecture notes (including Bedrock snippet examples)

Assessment:
- Layered, readable structure with clear separation of concerns
- Services encapsulate external integrations and core business rules
- API controllers are thin and compose services as intended
- Schemas/models organize cross-file contracts
- Tests exist and are task-focused (Bedrock init/simple/integration/flow)

---

## Strengths
- Clear two-step flow: schema extraction first, then NL->SQL generation
- Bedrock integration isolated in a service with meaningful prompt design and cleaning/parsing helpers
- Multi-database support with unified schema abstraction simplifies prompting and execution
- Safety measures: read-only validation and DB-specific limiting
- Reasonable defaults and configuration via environment

---

## Risks and Opportunities for Improvement

### Bedrock Integration
- Response parsing: current logic assumes content[0].text with ```sql fenced blocks
  - Suggest: add defensive parsing for alternate response shapes (e.g., content with structured blocks) and more robust error details when no SQL is found
- Retries/backoff: introduce exponential backoff on transient AWS errors; consider timeout control on invoke_model
- Telemetry: structured logging of prompt tokens, response size, and latencies (without leaking PHI or secrets)
- Parameterization: Encourage Bedrock to output parameterized SQL with named placeholders and a separate parameter object

### Security and Query Safety
- SQL validation is pattern-based and may be bypassed; consider a SQL parser (sqlglot/sqlparse) for stronger guarantees
- Whitelist tables/columns from the unified schema; optionally block dangerous functions
- For Mongo, avoid defaulting to patients collection; derive intent from schema/context; validate collection names against schema
- Sanitize and log with care: avoid printing secrets or PHI; ensure logs are structured and scrubbed

### Schema Extraction
- Row counts: fetching COUNT(*) for every table can be expensive; consider making row counts optional or sampled
- Sampling strategy for Mongo: expose knobs for sample size/timeouts; capture top field distributions more efficiently
- Normalize column metadata consistently (e.g., fields vs columns naming between services)

### Configuration and Secrets
- Avoid printing the .env path and configuration summary in production logs by default
- Consider AWS credentials via role-based auth (IRSA/EC2/ECS roles) instead of static keys

### Architecture and DX
- Dependency injection: provide a factory for Bedrock client and DB clients to improve testability (mocking/stubbing)
- Shared error model: standardize error payloads across services; bubble context with error codes
- Add typed return models in bedrock_service to match API schemas directly
- Extend tests: add unit tests for prompt creation, response parsing, and SQL cleaning; add golden tests for various DB types

---

## Quick Usage Notes
- To generate a query only:
  - GET /healthcare/generate-query-by-connection?connection_id=...&patient_id=...&query_type=comprehensive
- To generate and execute:
  - GET /healthcare/generate-and-execute-query?connection_id=...&patient_id=...&query_type=clinical&limit=100
- Ensure settings:
  - MongoDB connection for storing/finding the target DB connection by ID
  - AWS credentials and BEDROCK_MODEL_ID set; AWS_DEFAULT_REGION aligns with the chosen model

---

## Conclusion
The codebase is well-structured, with a clean separation between API, services, and configuration. The Bedrock-driven query generation over a unified schema is a solid approach and aligns with best practices for reducing hallucinations and controlling output. Strengthening response parsing, adding retries and metrics, hardening query validation, and tightening logging/secrets handling will increase reliability and safety for healthcare use cases.

