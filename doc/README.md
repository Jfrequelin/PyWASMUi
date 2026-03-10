# PyWASMui Documentation

Ce dossier contient deux versions completes de la documentation:

- Francais: `doc/fr/README.md`
- English: `doc/en/README.md`

## Arborescence

- `doc/fr/` : documentation complete FR
- `doc/en/` : complete EN documentation

## Notes

- Les deux versions couvrent le meme perimetre (setup, architecture, API, protocole, widgets/style, tests/dev).
- Utiliser la version FR ou EN selon l'equipe cible.

## Nouveautes recentes

- Protocole WebSocket enrichi avec acquittement serveur -> client (`meta.command_id` + `receipt`).
- Catalogue de widgets standard etendu (form controls, layout, feedback, content).
- Quick start apres clone documente pour un demarrage sans rebuild WASM.
- Suite Selenium dediee avec un test d'integration par widget (`tests/integration/test_selenium_widgets_catalog.py`).
