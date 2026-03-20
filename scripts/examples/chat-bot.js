#!/usr/bin/env node
/**
 * Webhook: Stateless chatbot with persona
 * POST /examples/chat-bot.js
 * Body: { "message": "Hi!", "persona": "pirate", "history": [] }
 */
const path = require('path');
const { chat } = require(path.join(__dirname, '..', 'lib', 'llm'));

const PERSONAS = {
  pirate:      "You are a friendly pirate. Respond with pirate slang, say 'arr' a lot.",
  shakespeare: "You are Shakespeare. Respond in Elizabethan English with dramatic flair.",
  chef:        "You are a world-class chef. Relate everything to cooking and food.",
  detective:   "You are a noir detective. Be mysterious and dramatic.",
  default:     "You are a helpful assistant.",
};

async function main() {
  let body = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (c) => (body += c));
  await new Promise((r) => process.stdin.on('end', r));

  const data = JSON.parse(body);
  const persona = PERSONAS[data.persona] || PERSONAS.default;
  const history = data.history || [];

  const messages = [
    { role: 'system', content: persona },
    ...history,
    { role: 'user', content: data.message || '' },
  ];

  const reply = await chat(messages);

  console.log(JSON.stringify({
    reply,
    persona: data.persona || 'default',
    history: [...history, { role: 'user', content: data.message }, { role: 'assistant', content: reply }],
  }, null, 2));
}

main().catch((e) => {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
});
