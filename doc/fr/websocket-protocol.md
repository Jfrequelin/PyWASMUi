# Protocole WebSocket

## Regles generales

- transport: WebSocket
- version: `protocol = 1`
- format: JSON

## `init` (serveur -> client)

```json
{
  "protocol": 1,
  "type": "init",
  "session": { "token": "session_id.signature" },
  "client_secret": "..."
}
```

## `create` (serveur -> client)

```json
{
  "protocol": 1,
  "type": "create",
  "meta": {
    "command_id": "4f9425f6e8d44674adf02f91af0c95f1"
  },
  "widget": {
    "id": "btn1",
    "kind": "Button",
    "parent": "root",
    "props": {
      "__tag": "button",
      "__event": "click",
      "text": "Click me",
      "enabled": true,
      "classes": ["primary"],
      "style": { "font-size": "16px" }
    },
    "children": []
  }
}
```

## `update` (serveur -> client)

```json
{
  "protocol": 1,
  "type": "update",
  "meta": {
    "command_id": "8b25243d9d5f47d6b7ffdb44fc6806fc"
  },
  "patch": {
    "id": "label1",
    "text": "Clicks: 2",
    "style": {
      "color": "#0f172a",
      "font-weight": "700"
    }
  }
}
```

## `delete` (serveur -> client)

```json
{
  "protocol": 1,
  "type": "delete",
  "meta": {
    "command_id": "1045ca95f59a42fbbf1b9298f18bb87f"
  },
  "widget": {
    "id": "old_widget",
    "kind": "Unknown",
    "parent": "root",
    "props": {},
    "children": []
  }
}
```

## `receipt` (client -> serveur)

Acquitte explicitement la reception d'une commande serveur (`create`, `update`, `delete`).

```json
{
  "protocol": 1,
  "type": "receipt",
  "session": { "token": "session_id.signature" },
  "receipt": {
    "command_id": "8b25243d9d5f47d6b7ffdb44fc6806fc",
    "status": "received"
  }
}
```

## `event` (client -> serveur)

```json
{
  "protocol": 1,
  "type": "event",
  "session": { "token": "session_id.signature" },
  "event": {
    "kind": "click",
    "id": "btn1",
    "value": null,
    "nonce": 3
  },
  "mac": "base64-hmac-optional"
}
```

## Contraintes de validation

- `session.token` doit etre valide.
- `mac` est optionnel en mode wrapper.
- si `mac` est present, verification de signature et nonce.
- les commandes serveur sont taguees avec `meta.command_id`.
- le client renvoie un `receipt` pour confirmer la reception de la commande.
