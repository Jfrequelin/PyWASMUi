# Architecture

## Vue globale

`pyWasm` implemente un modele **server-driven UI**:

- Le serveur Python pilote la structure et les mises a jour UI.
- Le runtime WASM Rust rend le DOM et applique les patchs.
- Le bridge JavaScript est minimal (transport WebSocket uniquement).

## Composants

### Serveur Python

- Emplacement: `server/` et `python_lib/pywasm_ui/`
- Roles:
  - gestion des sessions (`PyWasmSession`)
  - creation des widgets
  - reception des evenements
  - execution des callbacks metier
  - emission de commandes (`create`, `update`, `delete`)

### Bridge JavaScript

- Emplacement: `client/src/main.js`
- Roles:
  - connexion WebSocket
  - forward serveur -> WASM
  - forward WASM -> serveur via `wsSend`
  - etat pending des widgets interactifs
  - gestion `ack` (client -> serveur) et `receipt` (serveur -> client)
  - gestion des statuts de connexion

### Runtime WASM Rust

- Emplacement: `client/wasm_ui/src/`
- Roles:
  - parsing messages JSON
  - rendu widgets dans le DOM
  - application des patchs (`text`, `value`, `enabled`, `classes`, `attrs`, `style`)
  - capture des evenements utilisateur

## Flux d'execution

1. Connexion a `/ws`.
2. Reception `init` puis widgets initiaux (`create`).
3. Rendu DOM dans le navigateur.
4. Interaction utilisateur -> message `event`.
5. Traitement serveur -> reponse `update/create/delete`.
6. Le client renvoie `receipt` pour confirmer la reception des commandes serveur.

## Fiabilite transport

- client -> serveur: evenement avec `nonce` puis reponse `ack` apres traitement
- serveur -> client: commandes taguees avec `meta.command_id`
- client -> serveur: accusé `receipt` pour confirmer la bonne reception de la commande

## Reprise de session

- Le client stocke le `session_token` en `localStorage`.
- Apres refresh, la reconnexion utilise `/ws?session_token=...`.
- Le serveur peut reattacher la session existante et rejouer l'etat UI.

## Securite

- Le mode wrapper accepte les events non signes.
- Si `mac` est present, verification MAC + nonce monotone.
