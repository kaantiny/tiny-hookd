/**
 * llm.js - Battery-included LLM wrapper
 *
 * Usage:
 *   const { ask, chat, stream, askJson, embed } = require('./lib/llm');
 *
 *   // One-liner
 *   const answer = await ask("What is 2+2?");
 *
 *   // With system prompt
 *   const answer = await ask("Summarize this", { system: "You are a summarizer" });
 *
 *   // Override model per-call
 *   const answer = await ask("Hello", { model: "gpt-4o" });
 *
 *   // Multi-turn conversation
 *   const answer = await chat([
 *     { role: "system", content: "You are helpful" },
 *     { role: "user", content: "Hi" },
 *   ]);
 *
 *   // Streaming
 *   for await (const chunk of stream("Tell me a story")) {
 *     process.stdout.write(chunk);
 *   }
 *
 *   // JSON mode
 *   const data = await askJson("List 3 colors as JSON array");
 *
 *   // Embeddings
 *   const vec = await embed("Hello world");
 *
 * Env vars:
 *   OPENAI_API_KEY                    - API key (required)
 *   LLM_BASE_URL   / OPENAI_BASE_URL  - Base URL (optional, for proxies/local)
 *   LLM_MODEL      / OPENAI_MODEL     - Default model (default: gpt-4o-mini)
 *   LLM_TEMPERATURE                   - Default temperature (default: 0.7)
 *   LLM_MAX_TOKENS                    - Default max tokens (default: 4096)
 */

const { OpenAI } = require('openai');
const pRetry = require('p-retry'); // pinned to v4 (CommonJS)

// --------------- Config from env ---------------

const API_KEY = process.env.OPENAI_API_KEY;
const BASE_URL = process.env.LLM_BASE_URL || process.env.OPENAI_BASE_URL || undefined;
const DEFAULT_MODEL = process.env.LLM_MODEL || process.env.OPENAI_MODEL || 'gpt-4o-mini';
const DEFAULT_TEMP = parseFloat(process.env.LLM_TEMPERATURE || '0.7');
const DEFAULT_MAX_TOKENS = parseInt(process.env.LLM_MAX_TOKENS || '4096', 10);

// --------------- Client (singleton) ---------------

let _client = null;

function getClient() {
  if (!_client) {
    const opts = {};
    if (API_KEY) opts.apiKey = API_KEY;
    if (BASE_URL) opts.baseURL = BASE_URL;
    _client = new OpenAI(opts);
  }
  return _client;
}

function resetClient() {
  _client = null;
}

// --------------- Retry config ---------------

const RETRY_OPTS = {
  retries: 3,
  minTimeout: 2000,
  factor: 2,
  onFailedAttempt: (err) => {
    // Only retry on 429 (rate limit) and 5xx (server errors)
    const status = err?.status || err?.response?.status;
    if (status && status !== 429 && status < 500) {
      throw err; // Don't retry client errors (4xx except 429)
    }
  },
};

// --------------- Core functions ---------------

/**
 * Ask a single question, get a string answer.
 */
async function ask(prompt, opts = {}) {
  const { system, model, temperature, maxTokens, ...rest } = opts;
  const messages = [];
  if (system) messages.push({ role: 'system', content: system });
  messages.push({ role: 'user', content: prompt });
  return chat(messages, { model, temperature, maxTokens, ...rest });
}

/**
 * Send a full conversation, get a string answer.
 */
async function chat(messages, opts = {}) {
  const { model, temperature, maxTokens, ...rest } = opts;
  return pRetry(async () => {
    const resp = await getClient().chat.completions.create({
      model: model || DEFAULT_MODEL,
      messages,
      temperature: temperature ?? DEFAULT_TEMP,
      max_tokens: maxTokens || DEFAULT_MAX_TOKENS,
      ...rest,
    });
    return resp.choices[0].message.content;
  }, RETRY_OPTS);
}

/**
 * Ask and parse the response as JSON.
 */
async function askJson(prompt, opts = {}) {
  const { system, model, ...rest } = opts;
  const sysMsg = ((system || '') + '\nAlways respond with valid JSON.').trim();
  const messages = [
    { role: 'system', content: sysMsg },
    { role: 'user', content: prompt },
  ];
  return pRetry(async () => {
    const resp = await getClient().chat.completions.create({
      model: model || DEFAULT_MODEL,
      messages,
      response_format: { type: 'json_object' },
      temperature: rest.temperature ?? DEFAULT_TEMP,
      max_tokens: rest.maxTokens || DEFAULT_MAX_TOKENS,
    });
    return JSON.parse(resp.choices[0].message.content);
  }, RETRY_OPTS);
}

/**
 * Stream a response token-by-token (async generator).
 */
async function* stream(prompt, opts = {}) {
  const { system, model, temperature, maxTokens, ...rest } = opts;
  const messages = [];
  if (system) messages.push({ role: 'system', content: system });
  messages.push({ role: 'user', content: prompt });

  const resp = await getClient().chat.completions.create({
    model: model || DEFAULT_MODEL,
    messages,
    temperature: temperature ?? DEFAULT_TEMP,
    max_tokens: maxTokens || DEFAULT_MAX_TOKENS,
    stream: true,
    ...rest,
  });

  for await (const chunk of resp) {
    const delta = chunk.choices[0]?.delta?.content;
    if (delta) yield delta;
  }
}

/**
 * Get embedding vector(s).
 */
async function embed(text, opts = {}) {
  const { model = 'text-embedding-3-small' } = opts;
  const input = Array.isArray(text) ? text : [text];
  return pRetry(async () => {
    const resp = await getClient().embeddings.create({ model, input });
    const vectors = resp.data.map((d) => d.embedding);
    return Array.isArray(text) ? vectors : vectors[0];
  }, RETRY_OPTS);
}

module.exports = {
  ask,
  chat,
  stream,
  askJson,
  embed,
  getClient,
  resetClient,
  DEFAULT_MODEL,
};
