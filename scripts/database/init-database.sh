#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE EXTENSION IF NOT EXISTS age;
	CREATE EXTENSION IF NOT EXISTS pg_trgm;

	-- Load AGE extension
	LOAD 'age';
	SET search_path = ag_catalog, "\$user", public;

	-- Create graph if it doesn't exist
	DO \$\$
	BEGIN
		IF NOT EXISTS (SELECT * FROM ag_catalog.ag_graph WHERE name = 'business_graph') THEN
			PERFORM create_graph('business_graph');
		END IF;
	END
	\$\$;

	-- Create a Business node with properties (sample data)
	SELECT * FROM cypher('business_graph', \$\$
		CREATE (n:Business {name: 'Intuit', category: 'Financial Software'})
		RETURN n
	\$\$) as (node agtype);

	-- Check data with a sample query
	SELECT * FROM cypher('business_graph', \$\$
		MATCH (n:Business) 
		WHERE n.name = 'Intuit'
		RETURN n
	\$\$) as (node agtype);

	-- Create GIN index for full text search
	CREATE INDEX IF NOT EXISTS business_name_gin_idx 
	ON business_graph."Business"
	USING GIN (
		to_tsvector('english', ag_catalog.agtype_access_operator(properties, '"name"'::ag_catalog.agtype)::text)
	);

	CREATE INDEX IF NOT EXISTS business_category_gin_idx 
	ON business_graph."Business"
	USING GIN (
		to_tsvector('english', ag_catalog.agtype_access_operator(properties, '"category"'::ag_catalog.agtype)::text)
	);

	-- Test GIN index for full text search
	SELECT *
	FROM business_graph."Business"
	WHERE to_tsvector('english', ag_catalog.agtype_access_operator(properties, '"name"'::ag_catalog.agtype)::text) @@ plainto_tsquery('Intuit')
	OR to_tsvector('english', ag_catalog.agtype_access_operator(properties, '"category"'::ag_catalog.agtype)::text) @@ plainto_tsquery('Financial');

	-- Create trigram index for fuzzy matching
	CREATE INDEX IF NOT EXISTS business_name_trgm_idx 
	ON business_graph."Business" 
	USING GIN (
		(ag_catalog.agtype_access_operator(properties, '"name"'::ag_catalog.agtype)::text) gin_trgm_ops
	);

	CREATE INDEX IF NOT EXISTS business_category_trgm_idx 
	ON business_graph."Business" 
	USING GIN (
		(ag_catalog.agtype_access_operator(properties, '"category"'::ag_catalog.agtype)::text) gin_trgm_ops
	);

	-- Test the trigram index for fuzzy matching
	SELECT *
	FROM business_graph."Business"
	WHERE ag_catalog.agtype_access_operator(properties, '"name"'::ag_catalog.agtype)::text % 'Intit'
	OR similarity(ag_catalog.agtype_access_operator(properties, '"name"'::ag_catalog.agtype)::text, 'Intit') > 0.3;
EOSQL