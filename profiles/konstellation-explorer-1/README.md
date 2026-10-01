# Konstellation Explorer 1 — profil candidat français

Ce profil ajoute une planification dédiée, un lexique français, un bridge SA↔GF 1.0, les sources GF et une suite de requêtes émises par Konstellation v0.4. Chaque statement est conservé avec ses arguments, identités, qualificatifs, polarité et sources. Plusieurs statements d'une obligation restent dans le même bloc.

La première réalisation est une **présentation structurée avec libellés français et valeurs JSON canoniques**. Elle ne prétend pas fournir une narration fluide ni valider historiquement les assertions. Les métadonnées ne sont pas résumées ou remplacées par une assertion de vérité.

Le profil s'appelle `konstellation-explorer-1`, avec un RuntimeSet d'exemple `konstellation-fr-1` et la concrète `KonstellationFre`. Les prédicats inconnus, rôles manquants/dupliqués, polarités non positives, contraintes de discours non prises en charge et collections cycliques sont refusés. Les autres profils SA continuent d'utiliser leur planificateur existant.

## Compilation et publication

1. Installer GF et les bindings Python PGF compatibles avec SA (`pip install -e '.[gf]'`).
2. Construire la grammaire dans le dépôt GF/Wordbench autoritaire et obtenir une release READY vérifiée contenant `Konstellation.pgf`. Les sources `.gf` ne résident plus dans SemantiK Architect.
3. Utiliser `examples/konstellation-fr.json` du dépôt runtime-orchestrator, avec le chemin de cette release Wordbench. Installer les deux packages Python depuis leurs dépôts.
4. L'orchestrateur prépare un candidat isolé, vérifie les hashes, exécute SA avec `conformance --suite … --runtime-set-id konstellation-fr-1 --candidate-dir … --output …`, puis valide, promeut et active seulement après succès.
5. Démarrer le serveur SA sur le runtime publié et configurer Konstellation avec ce runtime, ce profil, la langue `fr` et le contrat `1.0`.

La commande de conformité candidate n'est pas accessible au serveur HTTP. Elle n'écrit aucun manifeste RELEASED ni activation. Les assertions de tests utilisent un interpréteur de fixture, identifié dans les tests; elles ne constituent pas une preuve de compilation GF. Aucun PGF ou faux rapport de publication n'est livré.

La suite inclut critères, page, entité et filtres négatifs. Toute nouvelle famille de prédicats ou transformation linguistique doit ajouter des cas avant publication. Le budget d'expansion des collections est borné; les IDs restent visibles pour distinguer des labels homonymes.
