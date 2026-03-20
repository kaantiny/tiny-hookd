#!/usr/bin/env node
/**
 * Webhook: Classify incoming webhooks and decide action
 * POST /examples/webhook-router.js
 * Body: any JSON payload (GitHub, Stripe, etc.)
 */
const path = require('path');
const { askJson } = require(path.join(__dirname, '..', 'lib', 'llm'));

async function main() {
  let body = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (c) => (body += c));
  await new Promise((r) => process.stdin.on('end', r));

  const result = await askJson(
    `Analyze this webhook payload and classify it:\n\n${body}`,
    {
      system: `Return JSON: source (github/stripe/slack/unknown), event_type, priority (high/medium/low), summary, suggested_actions (array).`,
      temperature: 0.2,
    }
  );

  console.log(JSON.stringify(result, null, 2));
}

main().catch((e) => {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
});
