#!/usr/bin/env node
/**
 * Webhook: Natural language to SQL
 * POST /examples/generate-sql.js
 * Body: { "question": "How many users signed up last week?", "schema": "users(id, name, email, created_at)" }
 */
const path = require('path');
const { askJson } = require(path.join(__dirname, '..', 'lib', 'llm'));

async function main() {
  let body = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (c) => (body += c));
  await new Promise((r) => process.stdin.on('end', r));

  const data = JSON.parse(body);
  const question = data.question || '';
  const schema = data.schema || 'No schema provided';
  const dialect = data.dialect || 'PostgreSQL';

  const result = await askJson(
    `Database schema:\n${schema}\n\nQuestion: ${question}`,
    {
      system: `You are a SQL expert. Convert natural language to ${dialect} SQL. Return JSON: sql, explanation, tables_used (array).`,
      temperature: 0.1,
    }
  );

  console.log(JSON.stringify(result, null, 2));
}

main().catch((e) => {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
});
