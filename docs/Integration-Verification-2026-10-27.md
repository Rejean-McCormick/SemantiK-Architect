# Vérification des intégrations satellites — 27 octobre 2026

**Portée :** vérification statique des instantanés de code et de documentation datés du 27 octobre 2026. **Aucune qualification runtime, CI distante, publication ni autorisation de production n’est déduite de cet audit.**

## Release RuntimeSet : séparation de l'autorité

- `SemantiK_Runtime_Orchestrator` **1.2.0** est compatible par plage de versions avec `SemantiK-Architect` **1.3.0-alpha.2** (`>=1.0,<2.0` selon son contrat). Cette compatibilité déclarée ne vaut pas attestation d'une release effective.
- L'orchestrateur contrôle les manifests Wordbench, les empreintes, les gates de conformance SA, l'activation et le rollback. Il **n'importe pas** le moteur `semantik_architect` : il consomme ses commandes et preuves explicites.
- Le contrat lexical accepte les schémas **1.0 et 1.1** et un ordre explicite de priorités. Les entrées Wikidata utilisées comme connaissance ne deviennent pas automatiquement des expressions GF exécutables.
- `Kristal-Framework` **v11 draft.4** décrit une autorité sémantique séparée; ni un contexte DaaT/IK ni une projection Kristal portable ne deviennent un signal d'admission de RuntimeSet par transitivité.
- Éléments examinés : `SemantiK_Runtime_Orchestrator/README.md`, `SemantiK_Runtime_Orchestrator/docs/CONTRACTS.md`, `SemantiK_Runtime_Orchestrator/src/semantik_runtime_orchestrator/`, `SemantiK_Architect/README.md`, `Kristal-Framework/contracts/release.json`.

**Qualification restante :** campagne isolée avec un Wordbench réellement épinglé, les commandes SA effectives, les preuves de conformance et les gates choisies; aucun environnement de release déployé n'a été audité.

## Mise à jour et preuve

Cette page décrit un état vérifié **sur fichiers**. Si le code, les contrats ou les captures de tests ont évolué depuis le snapshot, réexécuter les tests et réviser cette page avant publication.
