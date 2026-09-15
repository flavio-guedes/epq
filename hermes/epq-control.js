#!/usr/bin/env node
/*
 * EPQ Control Server — autoriza e executa controle de automações EPQ
 * pelo painel central (central.html#epq). Ações reais via CLI sancionado:
 *   hermes cron pause|resume|edit|run <job_id>
 * Somente leitura do estado vem de ~/.hermes/cron/jobs.json.
 *
 * Uso:  node epq-control.js [--port 7687]
 * Auth: gera ~/.hermes/control.token na 1ª execução; exige header
 *       `x-control-token` nos POSTs (e tolera em GETs se o panel enviar).
 */
const http = require('http');
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const HERMES_HOME = process.env.HERMES_HOME || path.join(os.homedir(), '.hermes');
const JOBS = path.join(HERMES_HOME, 'cron', 'jobs.json');
const TOKEN_FILE = path.join(HERMES_HOME, 'control.token');
const PY = '/Users/mac/.hermes/hermes-agent/venv/bin/python';

const PORT = parseInt(process.argv.filter((a, i, arr) => arr[i-1] === '--port')[0] || process.env.EPQ_CONTROL_PORT || '7687', 10);

function token() {
  try {
    if (fs.existsSync(TOKEN_FILE)) return fs.readFileSync(TOKEN_FILE, 'utf8').trim();
  } catch (_) {}
  const t = require('crypto').randomBytes(18).toString('hex');
  try {
    fs.writeFileSync(TOKEN_FILE, t, { mode: 0o600 });
    console.log('[epq-control] token criado em ' + TOKEN_FILE);
  } catch (e) {
    console.warn('[epq-control] nao consegui gravar token: ' + e.message);
    return null;
  }
  return t;
}

const TOKEN = token();

function readJobs() {
  try {
    return JSON.parse(fs.readFileSync(JOBS, 'utf8')).jobs || [];
  } catch (e) {
    return { __error: String(e.message) };
  }
}

function shape(job) {
  return {
    id: job.id,
    name: job.name,
    enabled: !!job.enabled,
    state: job.state || null,
    schedule: (job.schedule_display || (job.schedule && job.schedule.display) || null),
    next_run_at: job.next_run_at || null,
    last_run_at: job.last_run_at || null,
    last_status: job.last_status || null,
    last_error: job.last_error || null,
    paused_at: job.paused_at || null,
  };
}

function runCli(args) {
  return spawnSync(PY, ['-m', 'hermes_cli.main', 'cron'].concat(args), {
    encoding: 'utf8',
    timeout: 60000,
    env: Object.assign({}, process.env, {
      HERMES_HOME,
      HOME: os.homedir(),
      PATH: `${path.dirname(PY)}:${process.env.PATH || ''}`,
    }),
  });
}

function send(res, code, body, extra) {
  res.writeHead(code, Object.assign({
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, x-control-token',
    'Cache-Control': 'no-store',
  }, extra || {}));
  res.end(JSON.stringify(body));
}

function auth(req, res) {
  if (!TOKEN) return true;
  const got = req.headers['x-control-token'];
  if (got === TOKEN) return true;
  send(res, 401, { ok: false, error: 'Não autorizado. Cole o token do servidor de controle.' });
  return false;
}

function validId(jobs, id) {
  return Array.isArray(jobs) && jobs.some(j => j.id === id);
}

function cronExprValid(expr) {
  if (typeof expr !== 'string') return false;
  const parts = expr.trim().split(/\s+/);
  if (parts.length !== 5) return false;
  const re = /^(\*|(\d+)(-\d+)?(\/\d+)?|\*\/\d+)$/;
  const m = [/(^(\*|\d+|\*\/\d+)$)/, /(\d+)|(\*)/, /(\d+)|(\*)/, /(\d+)|(\*)/, /(\d+)|(\*)/];
  if (parts[0] === '*' || parts[0].startsWith('*/') || /^\d+$/.test(parts[0])) { /* min ok */ } else return false;
  return parts.slice(1).every(p => p === '*' || /^\d+$/.test(p) || /^(\d+)-(\d+)$/.test(p) || /^\*\/(\d+)$/.test(p));
}

const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  if (req.method === 'OPTIONS') { send(res, 204, ''); return; }

  if (req.method === 'GET' && url === '/api/control/jobs') {
    if (!auth(req, res)) return;
    const jobs = readJobs();
    if (jobs.__error) return send(res, 500, { ok: false, error: jobs.__error });
    return send(res, 200, { ok: true, server: 'online', count: jobs.length, jobs: jobs.map(shape) });
  }

  if (req.method === 'GET' && url === '/api/control/health') {
    return send(res, 200, { ok: true, requiresToken: !!TOKEN });
  }

  if (req.method === 'POST' && url.startsWith('/api/control/jobs/')) {
    if (!auth(req, res)) return;
    const rest = url.slice('/api/control/jobs/'.length).split('/');
    const id = decodeURIComponent(rest[0]);
    const action = rest[1];
    const jobs = readJobs();
    if (jobs.__error) return send(res, 500, { ok: false, error: jobs.__error });
    if (!validId(jobs, id)) return send(res, 404, { ok: false, error: 'Job não encontrado: ' + id });
    if (!['pause', 'resume', 'edit', 'run'].includes(action)) return send(res, 400, { ok: false, error: 'Ação inválida: ' + action });

    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      let data = {};
      try { data = body ? JSON.parse(body) : {}; } catch (_) {}

      if (action === 'edit') {
        const expr = String(data.schedule || '').trim();
        if (!cronExprValid(expr)) return send(res, 400, { ok: false, error: 'Expressão cron inválida (use 5 campos, ex: "0 8 * * *"): ' + expr });
        const r = runCli(['edit', id, '--schedule', expr]);
        const ok = r.status === 0 && !/error|error:/i.test(r.stdout || '');
        const jobs2 = readJobs();
        const updated = (jobs2.__error ? null : jobs2.find(j => j.id === id)) || null;
        return send(res, ok ? 200 : 500, {
          ok, action, id, message: ok ? ('Agenda atualizada p/ ' + expr) : (r.stderr || r.stdout || 'falha'),
          job: updated ? shape(updated) : null,
        });
      }

      if (action === 'run') {
        const child = spawn(PY, ['-m', 'hermes_cli.main', 'cron', 'run', id], {
          detached: true,
          stdio: 'ignore',
          env: Object.assign({}, process.env, { HERMES_HOME, HOME: os.homedir() }),
        });
        child.unref();
        return send(res, 200, { ok: true, action, id, message: 'Execução disparada em background.' });
      }

      const r = runCli([action, id]);
      const ok = r.status === 0 && !/error|error:/i.test(r.stdout || '');
      const jobs2 = readJobs();
      const updated = (jobs2.__error ? null : jobs2.find(j => j.id === id)) || null;
      return send(res, ok ? 200 : 500, {
        ok,
        action,
        id,
        message: ok ? ('OK · ' + action + ' ' + id) : (r.stderr || r.stdout || 'falha'),
        job: updated ? shape(updated) : null,
      });
    });
    return;
  }

  send(res, 404, { ok: false, error: 'Rota não encontrada' });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('[epq-control] online em http://127.0.0.1:' + PORT);
  console.log('[epq-control] use o token em ~/.hermes/control.token para autorizar pelo painel');
});