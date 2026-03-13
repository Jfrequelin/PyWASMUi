/* tslint:disable */
/* eslint-disable */

export function wasm_boot(): void;

export function wasm_handle_server_message(message: string): void;

export function wasm_on_websocket_open(): void;

export function wasm_set_connection_status(status: string): void;

export function wasm_set_incoming_message_handler(_handler: Function): void;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
    readonly memory: WebAssembly.Memory;
    readonly wasm_boot: () => void;
    readonly wasm_handle_server_message: (a: number, b: number) => void;
    readonly wasm_on_websocket_open: () => void;
    readonly wasm_set_connection_status: (a: number, b: number) => void;
    readonly wasm_set_incoming_message_handler: (a: any) => void;
    readonly wasm_bindgen__closure__destroy__h91773a5ae191ced5: (a: number, b: number) => void;
    readonly wasm_bindgen__convert__closures_____invoke__h92e87cc08a86197c: (a: number, b: number, c: any) => void;
    readonly __wbindgen_exn_store: (a: number) => void;
    readonly __externref_table_alloc: () => number;
    readonly __wbindgen_externrefs: WebAssembly.Table;
    readonly __wbindgen_free: (a: number, b: number, c: number) => void;
    readonly __wbindgen_malloc: (a: number, b: number) => number;
    readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
    readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;

/**
 * Instantiates the given `module`, which can either be bytes or
 * a precompiled `WebAssembly.Module`.
 *
 * @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
 *
 * @returns {InitOutput}
 */
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
 * If `module_or_path` is {RequestInfo} or {URL}, makes a request and
 * for everything else, calls `WebAssembly.instantiate` directly.
 *
 * @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
 *
 * @returns {Promise<InitOutput>}
 */
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
