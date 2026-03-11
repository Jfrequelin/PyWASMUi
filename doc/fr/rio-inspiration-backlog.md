# Backlog Inspiration Rio (PyWASMui)

Objectif: ameliorer l'ergonomie developpeur facon Rio sans perdre l'architecture PyWASMui (server-driven + runtime WASM + protocole explicite).

## Ticket 1 - Migration package widgets `standard` -> `html`
- Priorite: P0
- Statut: done
- But:
  - package canonique `pywasm_ui.widgets.html`
  - compat retroactive `pywasm_ui.widgets.standard`
  - docs alignees sur la nouvelle terminologie
- Criteres d'acceptation:
  - imports `from pywasm_ui.widgets import ButtonWidget` OK
  - imports legacy `from pywasm_ui.widgets.standard import ButtonWidget` OK
  - imports legacy module `from pywasm_ui.widgets.standard.ButtonWidget import ButtonWidget` OK
  - tests unitaires + integration verts

## Ticket 2 - Contrat d'exports widgets stable
- Priorite: P0
- Statut: done
- But:
  - verifier que le catalogue exporte reste coherent et complet
- Criteres d'acceptation:
  - test unitaire qui compare `__all__` au set de classes widgets detectees

## Ticket 3 - API composant declarative (MVP)
- Priorite: P1
- Statut: done
- But:
  - introduire une couche Python `Component` avec `build()` au-dessus des widgets
- Criteres d'acceptation:
  - exemple minimal compose fonctionne sans changer le runtime

## Ticket 4 - Events types cote Python
- Priorite: P1
- Statut: done
- But:
  - ajouter des classes event (ex: TextInputChangeEvent) pour handlers plus lisibles
- Criteres d'acceptation:
  - au moins 2 widgets utilises avec events types dans les examples/tests

## Ticket 5 - Theme tokens unifies
- Priorite: P2
- Statut: done
- But:
  - theme central (colors, spacing, radius, typo) applique aux widgets html
- Criteres d'acceptation:
  - 1 theme par defaut + 1 surcharge custom documentee

## Ticket 6 - Routing leger inspire Rio
- Priorite: P2
- Statut: done
- But:
  - pages Python optionnelles sans forcer un framework complet
- Criteres d'acceptation:
  - exemple multipage simple + guard basique
