# SemantiK Architect ↔ diK — précontrôle sémantique candidat

**Statut : contrat d'ingénierie à qualifier, pas un changement des locks existants.**

L'ADR-0013 *Wikidata primary generic lexical authority* reste applicable au
lexique générique : Wikidata L/S/F ≠ Wikidata Q/P ≠ KQ/KP des Kristals.
Le nouveau registre diK référence des `Q/P` exacts et revus en provenance du
Framework ; il ne sert ni de grammaire, ni de réalisation textuelle, ni de
preuve d'acceptation de candidat lexical.

`python tools/dik_federation_preflight.py --dir <dossier diK>` vérifie le
manifeste et la base dérivée **en lecture seule**. Une réponse
`validation=INTEGRITY_ONLY` n'équivaut pas à une disponibilité dans
`LexicalKnowledgePort`, ne crée pas de LexicalBinding, ne contourne pas le
policy order `demande > domaine > projet > Wikidata > GF générique`, ne valide
aucun RuntimeSet et n'active aucun fallback linguistique.

Le périmètre diK cible 13 langues (`en fr es de nl sv da nn fi et af it pt`),
mais les anciens artefacts 14 langues (y compris `no`) demeurent historiques.
Le domaine de SemantiK ne doit ni remplacer `no` par `nb`, ni déclarer une
langue supportée sur la simple présence d'une entrée de registre.

Une intégration ultérieure exige contrat propriétaire de port, conformance,
sens lexical vérifié, provenance/licence et tests d'intégration explicites.
