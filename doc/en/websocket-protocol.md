# WebSocket Protocol

## General Rules

- transport: WebSocket
- version: `protocol = 1`
- format: JSON

## `init` (server -> client)

```json
{
  "protocol": 1,
  "type": "init",
  "session": { "token": "session_id.signature" },
  "client_secret": "..."
}
```

## `create` (server -> client)

```json
{
  "protocol": 1,
  "type": "create",
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

## `update` (server -> client)

```json
{
  "protocol": 1,
  "type": "update",
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

## `delete` (server -> client)

```json
{
  "protocol": 1,
  "type": "delete",
  "widget": {
    "id": "old_widget",
    "kind": "Unknown",
    "parent": "root",
    "props": {},
    "children": []
  }
}
```

## `event` (client -> server)

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

## Validation Constraints

- `session.token` must be valid.
- `mac` is optional in wrapper mode.
- if `mac` is provided, signature and nonce are verified.
