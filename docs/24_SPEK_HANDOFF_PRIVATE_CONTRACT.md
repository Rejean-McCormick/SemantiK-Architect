# Spek private discourse handoff — SemantiK Architect

`tools/verify_spek_handoff.py` lit le paquet privé
`spek.private-editorial-handoff/1.0` et les fichiers de requêtes existants.
Il réutilise `CommunicationRequest.from_dict` et `RequestValidator` de
SemantiK Architect. Aucune extension incompatible de
`CommunicationRequest/1.0` n'est introduite dans cette passe.

Il vérifie l'identité du fichier (SHA256), les sources des obligations,
la force communicative, les formes de blocs et la langue. Il n'infère aucune
relation rhétorique, ne modifie aucun graphe et ne garantit pas que les
opérations GF sont disponibles. La grammaire compilée et les lexiques restent
à produire et à qualifier indépendamment.

Commande dans le répertoire `SemantiK_Architect` (avec `src` sur
`PYTHONPATH` ou le package installé) :

`py -3 tools/verify_spek_handoff.py --lock <private-lock.json> --requests-dir <requests>`

Ce paquet ne sert ni de validation scientifique ni d'autorisation Wiki.
