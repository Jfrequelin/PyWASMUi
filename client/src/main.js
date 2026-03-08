import initWasm, {
  wasm_set_incoming_message_handler as wasmSetIncomingMessageHandler,
  wasm_handle_server_message as wasmHandleServerMessage,
  wasm_boot as wasmBoot,
  wasm_on_websocket_open as wasmOnWebSocketOpen,
  wasm_set_connection_status as wasmSetConnectionStatus
} from '../wasm_ui/pkg/wasm_ui.js';

const RUNTIME_CONFIG_URL = '/config/pywasm.runtime.json';
const INLINE_RUNTIME_CONFIG_GLOBAL = '__PYWASM_RUNTIME_CONFIG__';

function loadInlineRuntimeConfig() {
  if (typeof window === 'undefined') {
    return {};
  }
  const cfg = window[INLINE_RUNTIME_CONFIG_GLOBAL];
  return cfg && typeof cfg === 'object' ? cfg : {};
}

async function loadRuntimeConfig() {
  const inlineConfig = loadInlineRuntimeConfig();

  try {
    const response = await fetch(RUNTIME_CONFIG_URL, { cache: 'no-store' });
    if (!response.ok) {
      return inlineConfig;
    }
    const fetchedConfig = await response.json();
    return {
      ...fetchedConfig,
      ...inlineConfig,
      websocket: {
        ...(fetchedConfig?.websocket ?? {}),
        ...(inlineConfig?.websocket ?? {})
      },
      mount: {
        ...(fetchedConfig?.mount ?? {}),
        ...(inlineConfig?.mount ?? {})
      }
    };
  } catch {
    return inlineConfig;
  }
}

function resolveMountElementId(runtimeConfig) {
  const elementId = runtimeConfig?.mount?.elementId;
  if (typeof elementId === 'string' && elementId.trim().length > 0) {
    return elementId.trim();
  }
  return 'app';
}

function ensureMountElement(runtimeConfig) {
  if (typeof document === 'undefined') {
    return;
  }

  const desiredId = resolveMountElementId(runtimeConfig);
  const appExisting = document.getElementById('app');
  if (appExisting) {
    return;
  }

  const target = document.getElementById(desiredId);
  if (target) {
    if (target.id !== 'app') {
      target.setAttribute('data-pywasm-original-id', desiredId);
      target.id = 'app';
    }
    return;
  }

  const created = document.createElement('div');
  created.id = 'app';
  created.setAttribute('data-pywasm-root', 'true');
  document.body.appendChild(created);
}

function resolveWebSocketUrl(runtimeConfig) {
  const ws = runtimeConfig?.websocket ?? {};
  const hasWindowLocation = typeof window !== 'undefined' && !!window.location;

  const defaultProtocol = hasWindowLocation && window.location.protocol === 'https:' ? 'wss' : 'ws';
  const protocol = typeof ws.protocol === 'string' && ws.protocol.length > 0
    ? ws.protocol.replace(':', '')
    : defaultProtocol;

  const host = typeof ws.host === 'string' && ws.host.length > 0
    ? ws.host
    : hasWindowLocation
      ? window.location.hostname
      : '127.0.0.1';

  const port = Number.isInteger(ws.port)
    ? String(ws.port)
    : hasWindowLocation
      ? window.location.port
      : '8000';

  const pathRaw = typeof ws.path === 'string' && ws.path.length > 0 ? ws.path : '/ws';
  const path = pathRaw.startsWith('/') ? pathRaw : `/${pathRaw}`;

  const hostPort = port ? `${host}:${port}` : host;
  return `${protocol}://${hostPort}${path}`;
}

function appendSessionToken(wsUrl) {
  const token = getStoredSessionToken();
  if (!token) {
    return wsUrl;
  }
  const url = new URL(wsUrl);
  url.searchParams.set('session_token', token);
  return url.toString();
}

function resolveConfiguredWebSocketUrl(runtimeConfig) {
  return appendSessionToken(resolveWebSocketUrl(runtimeConfig));
}

function resolveFallbackWebSocketUrl() {
  if (typeof window !== 'undefined' && window.location) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/ws`;
  }

  return null;
}

const TAB_NAME_PREFIX = 'pywasm-tab:';
const SESSION_TOKEN_STORAGE_KEY_PREFIX = 'pywasm.session_token.';
let socket;
const pendingCommands = new Map();
const widgetPendingCounts = new Map();
const PENDING_COMMAND_TIMEOUT_MS = 10000;

function generateTabId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function getTabId() {
  if (typeof window === 'undefined') {
    return 'server';
  }

  if (typeof window.name === 'string' && window.name.startsWith(TAB_NAME_PREFIX)) {
    return window.name.slice(TAB_NAME_PREFIX.length);
  }

  const id = generateTabId();
  window.name = `${TAB_NAME_PREFIX}${id}`;
  return id;
}

function sessionTokenStorageKey() {
  return `${SESSION_TOKEN_STORAGE_KEY_PREFIX}${getTabId()}`;
}

function getStoredSessionToken() {
  try {
    return localStorage.getItem(sessionTokenStorageKey());
  } catch {
    return null;
  }
}

function persistSessionTokenFromMessage(message) {
  try {
    const parsed = JSON.parse(message);
    const token = parsed?.type === 'init' ? parsed?.session?.token : null;
    if (typeof token === 'string' && token.length > 0) {
      localStorage.setItem(sessionTokenStorageKey(), token);
    }
  } catch {
    // Ignore non-JSON payloads.
  }
}

function wsSend(message) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    return;
  }
  if (isWidgetCommandBlocked(message)) {
    return;
  }
  trackOutgoingCommand(message);
  socket.send(message);
}

function isWidgetCommandBlocked(rawMessage) {
  try {
    const parsed = JSON.parse(rawMessage);
    if (parsed?.type !== 'event') {
      return false;
    }
    const widgetId = parsed?.event?.id;
    if (typeof widgetId !== 'string' || widgetId.length === 0) {
      return false;
    }
    return (widgetPendingCounts.get(widgetId) || 0) > 0;
  } catch {
    return false;
  }
}

function resolvePendingClassForWidget(widgetId) {
  if (typeof document === 'undefined') {
    return 'widget-pending';
  }
  const el = document.getElementById(widgetId);
  if (!el) {
    return 'widget-pending';
  }
  return el.getAttribute('data-pending-class') || 'widget-pending';
}

function setWidgetPendingVisual(widgetId, isPending) {
  if (typeof document === 'undefined') {
    return;
  }
  const el = document.getElementById(widgetId);
  if (!el) {
    return;
  }
  const pendingClass = resolvePendingClassForWidget(widgetId);
  if (isPending) {
    el.classList.add(pendingClass);
  } else {
    el.classList.remove(pendingClass);
  }
}

function trackOutgoingCommand(rawMessage) {
  try {
    const parsed = JSON.parse(rawMessage);
    if (parsed?.type !== 'event') {
      return;
    }
    const nonce = parsed?.event?.nonce;
    const widgetId = parsed?.event?.id;
    if (Number.isInteger(nonce)) {
      const nonceKey = String(nonce);
      const timeoutId = setTimeout(() => {
        consumePendingCommand(nonceKey);
      }, PENDING_COMMAND_TIMEOUT_MS);
      pendingCommands.set(nonceKey, { widgetId, timeoutId });
      if (typeof widgetId === 'string' && widgetId.length > 0) {
        const nextCount = (widgetPendingCounts.get(widgetId) || 0) + 1;
        widgetPendingCounts.set(widgetId, nextCount);
        setWidgetPendingVisual(widgetId, true);
      }
    }
  } catch {
    // Ignore non-JSON payloads.
  }
}

function consumeAckIfPresent(rawMessage) {
  try {
    const parsed = JSON.parse(rawMessage);
    if (parsed?.type !== 'ack') {
      return false;
    }
    const nonce = parsed?.meta?.nonce;
    if (Number.isInteger(nonce)) {
      const nonceKey = String(nonce);
      consumePendingCommand(nonceKey);
    }
    return true;
  } catch {
    return false;
  }
}

function consumePendingCommand(nonceKey) {
  const pending = pendingCommands.get(nonceKey);
  if (!pending) {
    return;
  }
  clearTimeout(pending.timeoutId);
  pendingCommands.delete(nonceKey);

  const widgetId = pending.widgetId;
  if (typeof widgetId !== 'string' || widgetId.length === 0) {
    return;
  }

  const currentCount = widgetPendingCounts.get(widgetId) || 0;
  const nextCount = Math.max(0, currentCount - 1);
  if (nextCount === 0) {
    widgetPendingCounts.delete(widgetId);
    setWidgetPendingVisual(widgetId, false);
  } else {
    widgetPendingCounts.set(widgetId, nextCount);
  }
}

// Expose only the transport bridge to WASM. No business logic here.
globalThis.wsSend = wsSend;

async function start() {
  const runtimeConfig = await loadRuntimeConfig();
  ensureMountElement(runtimeConfig);

  await initWasm();
  wasmBoot();
  wasmSetConnectionStatus('connecting');

  wasmSetIncomingMessageHandler((payload) => {
    wasmHandleServerMessage(payload);
  });

  const wsUrl = resolveConfiguredWebSocketUrl(runtimeConfig) || resolveFallbackWebSocketUrl();
  if (!wsUrl) {
    console.error('[pyWASM] Unable to resolve websocket URL.');
    return;
  }
  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    wasmOnWebSocketOpen();
  };

  socket.onmessage = (event) => {
    const text = typeof event.data === 'string' ? event.data : '';
    if (text) {
      persistSessionTokenFromMessage(text);
      if (consumeAckIfPresent(text)) {
        return;
      }
      wasmHandleServerMessage(text);
    }
  };

  socket.onerror = (err) => {
    wasmSetConnectionStatus('error');
    console.error('WebSocket error', err);
  };

  socket.onclose = () => {
    wasmSetConnectionStatus('closed');
    for (const pending of pendingCommands.values()) {
      clearTimeout(pending.timeoutId);
    }
    for (const widgetId of widgetPendingCounts.keys()) {
      setWidgetPendingVisual(widgetId, false);
    }
    pendingCommands.clear();
    widgetPendingCounts.clear();
    console.warn('WebSocket closed');
  };
}

start().catch((err) => {
  console.error('Failed to start client', err);
});
