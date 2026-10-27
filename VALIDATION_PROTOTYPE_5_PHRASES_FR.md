# Rapport — SemantiK Architect et prototype 5 phrases

Date : 2026-10-27
Base : `znapshot_SemantiK_Architect_10271345.zip` ; version déclarée `1.3.0-alpha.2` inchangée.

## Portée

- Le prototype autonome a été intégré comme fixture dans **Architect**, sans création d'un second moteur.
- Profil GF, lexique, bridge, cinq requêtes et suite de conformance **déjà identiques** à Phrase Ops : réutilisés sans modification.
- Grammaire Architect avec `flags unlexer = text ;` conservée, contrairement à une vieille copie autonome sans ce flag ; compilation GF réelle non effectuée.
- Les cinq seeds sources et le rapport de prototype historique sont inclus. Quatre sont explicitement issus de lectures/paraphrases assistées par IA et requièrent une revue des sources.
- Le faux `grammar.pgf` n'est ni livré ni activé. Le contrôle dynamique crée un candidat temporaire et détruit le contenu après test.
- Aucun corpus ou RuntimeSet n'est modifié. Phrase Ops et Runtime Orchestrator ne sont pas changés.

## Contrôles vérifiés

- `PYTHONPATH=src:. python tools/validate_repository.py` : **68 tests réussis**, **16 schémas validés**.
- Contrôle de projection seeds → cinq requêtes canoniques, conformance structurée, validation de provenance optionnelle, refus de mutation de candidat, empreintes contrôlées.
- Le résultat reste **EXPRESSION_LEVEL_FIXTURE_ONLY**. Aucune conformance PGF ou promotion de release réelle n'est démontrée.

## Diff du snapshot

- **272** fichiers sources existants strictement inchangés.
- Modifiés : `profiles/konstellation-explorer-3/README.md`, `README.md`.
- Ajoutés : `docs/23_FIVE_PHRASE_PROTOTYPE_CONSOLIDATION.md`, `examples/phrase-prototype/PROTOTYPE_REPORT_SOURCE.md`, `examples/phrase-prototype/README.md`, `examples/phrase-prototype/semantic-seeds.json`, `tests/integration/test_phrase_prototype.py`, `tools/phrase_prototype.py`.
- Aucun fichier original supprimé.
- `SNAPSHOT_INDEX.txt` est l'index historique du snapshot; `INTEGRATION_MANIFEST_SHA256.json` est le nouvel index après consolidation.

## Installer

Sauvegarder le dépôt `SemantiK-Architect`, extraire ce ZIP à sa racine (sans sous-dossier supplémentaire), préserver `.git`, tout RuntimeSet ou donnée locale non présente dans l'archive, puis exécuter `python tools/validate_repository.py`. Ne pas supprimer automatiquement la console Phrase Ops ni les dossiers autonomes s'ils contiennent des résultats locaux.
