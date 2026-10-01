# SemantiK Architect Kristal v6 — overlay 1.2.1

Base exacte : `SmartSnap(20261001-182625).zip`, SemantiK Architect 1.2.0 / Kristal Standard 6.0.0.

Cet overlay **préserve Kristal v6** et ajoute seulement le support fail-closed de `extension_capabilities` dans les bundles candidats multilingues.

## Installation

```powershell
.\Apply-Overlay.ps1
```

Par défaut, la cible est `C:\mycode\SemantiK_Architect\SemantiK_Architect`. Le script vérifie les hashes de la baseline avant d'écraser les fichiers et crée une sauvegarde sous `.overlay-backups`.

## Validation

```powershell
$env:PYTHONPATH = "src;."
python tools\validate_repository.py
```

Résultat validé côté construction : **51 tests PASS + 12 schémas validés**.

Aucune logique grammaticale par langue n'est ajoutée à SA; GF/RGL reste l'autorité de réalisation. Aucun RuntimeSet n'est libéré ou activé par cet overlay.
