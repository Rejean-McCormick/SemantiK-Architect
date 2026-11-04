# SemantiK Architect — overlay de conformité UNESCO candidate

Racine : `C:\mycode\SemantiK_Architect\SemantiK_Architect`.

Ajoute `tools/unesco_candidate_probe.py`, qui utilise **les classes existantes** `CandidateConformance`, `ConformanceHarness`, `CommunicationRequest`, `RequestValidator` et `GfBridgeRealizer/PgfRuntime`. Le backend est Python `pgf` s'il fonctionne, ou l'exécutable **réel** fourni via `--gf-exe` (configuration limitée au sous-processus).

Après la compilation dans Wordbench, la fabrique appelle automatiquement :

```powershell
py -3.12 tools/unesco_candidate_probe.py --candidate "C:\...\candidates\fr" --requests-dir "C:\...\requests\fr" --results-dir "C:\...\results\fr" --gf-exe "C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe"
```

Les résultats `CommunicationResult/1.0` sont créés par **SemantiK** et vérifiés par la fabrique/Spek, jamais assemblés à la main. Ne lancez pas sur un candidat manquant de `pipeline.lock.json` ; l'opération refusera. Pas d'activation de RuntimeSet, pas de release, pas de publication.

Test : `py -3.12 -m unittest discover -s tests -p test_unesco_candidate_probe.py -v`.
