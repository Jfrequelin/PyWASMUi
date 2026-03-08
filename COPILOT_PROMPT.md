# Prompt pour Copilot (VS Code) - Demarrage du projet

## Contexte du projet
Nous construisons un framework UI server-driven ou :

- le serveur Python pilote entierement l'interface utilisateur,
- le client est un moteur WASM (Rust) generique et fixe,
- un wrapper JS minimal sert uniquement de pont WebSocket,
- le DOM est manipule exclusivement par le WASM,
- la communication utilise un protocole JSON securise.

Le navigateur agit comme un terminal graphique, sans logique metier.

## Objectifs pour Copilot
Copilot doit generer :

- la structure du projet,
- le squelette du moteur WASM (Rust + wasm-bindgen),
- le wrapper JS minimal,
- le serveur Python (FastAPI + WebSocket),
- les structures JSON du protocole,
- le systeme de widgets cote WASM,
- le systeme de widgets cote Python,
- le mecanisme de securite (HMAC + nonce + session_token).

## Architecture

### Client (navigateur)

#### 1. WASM (Rust)
- Maintient un arbre de widgets (`HashMap<String, Widget>`).
- Applique les patchs JSON recus du serveur.
- Manipule le DOM via `web_sys`.
- Capture les evenements DOM.
- Genere un `nonce` monotone.
- Calcule un `HMAC(client_secret, event_json)` pour chaque evenement.
- Envoie les evenements signes au serveur via le wrapper JS.

#### 2. Wrapper JS minimal
- Ouvre le WebSocket.
- Transmet les messages serveur -> WASM.
- Transmet les messages WASM -> serveur.
- Ne contient aucune logique metier.

### Serveur (Python)
- Framework : FastAPI + WebSocket.
- Maintient un arbre de widgets Python.
- Genere des patchs JSON envoyes au client.
- Recoit des evenements signes.
- Verifie :
  - `session_token`,
  - `mac` (HMAC),
  - `nonce` monotone,
  - validite du schema JSON.
- Execute les callbacks Python.
- Renvoie les mises a jour UI.

## Securite

1. TLS obligatoire (HTTPS/WSS)
2. `session_token` signe : identifie la session WebSocket.
3. `client_secret` :
   - genere par le serveur,
   - envoye au WASM dans un message `init`,
   - stocke dans la memoire WASM,
   - jamais expose au JS.
4. HMAC sur chaque evenement :

```text
mac = HMAC(client_secret, canonical_json(event))
```

5. `nonce` monotone (anti-replay).
6. Validation stricte cote client et serveur.

## Format JSON du protocole

### Message generique
```json
{
  "protocol": 1,
  "session": { "token": "session_id.signature" },
  "type": "create",
  "widget": {
    "id": "btn1",
    "kind": "Button",
    "parent": "root",
    "props": {
      "text": "OK",
      "enabled": true,
      "classes": ["primary"]
    }
  },
  "meta": {
    "timestamp": 1710000000
  }
}
```

### Evenement client -> serveur
```json
{
  "protocol": 1,
  "type": "event",
  "session": { "token": "session_id.signature" },
  "event": {
    "kind": "click",
    "id": "btn1",
    "value": null,
    "nonce": 42
  },
  "mac": "base64-hmac"
}
```

## Widgets (MVP)
- `Window`
- `Container`
- `Label`
- `Button`
- `TextInput`
- `ListView`

Chaque widget possede :
- `id`
- `kind`
- `parent`
- `props` (dictionnaire libre)
- `children`

## MVP minimal a implementer
1. Le serveur envoie un `Label` et un `Button`.
2. Le WASM cree les elements dans le DOM.
3. L'utilisateur clique le bouton.
4. Le WASM capture l'evenement, signe le message (HMAC), puis envoie l'evenement.
5. Le serveur verifie la signature, met a jour le label, puis renvoie un patch.
6. Le WASM applique le patch.

## Instructions pour Copilot
Copilot doit :

- generer du code Rust, Python et JS conforme a cette architecture,
- respecter le protocole JSON defini,
- implementer le systeme de widgets,
- implementer le mecanisme HMAC + nonce,
- produire un code clair, modulaire et extensible.
