#!/usr/bin/env node
/**
 * Example Node.js webhook script with OpenAI + retry
 * Receives JSON payload via stdin
 */

const { OpenAI } = require('openai');
const pRetry = require('p-retry');

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

async function processWithAI(text) {
  return pRetry(
    async () => {
      const response = await openai.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: `Summarize: ${text}` }]
      });
      return response.choices[0].message.content;
    },
    { retries: 3, minTimeout: 1000, factor: 2 }
  );
}

async function main() {
  let payload = '';
  
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => payload += chunk);
  
  await new Promise(resolve => process.stdin.on('end', resolve));
  
  let data;
  try {
    data = JSON.parse(payload);
  } catch {
    data = { raw: payload };
  }
  
  console.log(JSON.stringify({
    status: 'ok',
    received_at: new Date().toISOString(),
    data,
    message: 'Webhook processed successfully'
  }, null, 2));
}

main().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
