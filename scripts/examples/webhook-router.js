#!/usr/bin/env node
/**
 * Webhook: Classify incoming webhooks and decide action
 * POST /examples/webhook-router.js
 * Body: any JSON payload (GitHub, Stripe, etc.)
 * 
 * Uses AI to understand the webhook and suggest routing.
 */
const { askJson } = require('../lib/llm');

async function main() {
  let payload = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (c) => (payload += c));
  await new Promise((r) => process.stdin.on('end', r));

  const result = await askJson(
    `Analyze this webhook payload and classify it:\n\n${payload}`,
    {
      system: `You analyze webhook payloads. Return JSON with:
- source (e.g. "github", "stripe", "slack", "unknown")
- event_type (e.g. "push", "payment_success", "message")
- priority ("high", "medium", "low")
- summary (one sentence)
- suggested_actions (array of action strings)`,
      temperature: 0.2,
    }
  );

  console.log(JSON.stringify(result, null, 2));
}

main().catch((e) => {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
});
