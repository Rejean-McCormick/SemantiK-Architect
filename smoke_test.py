from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
PGF_PATH = ROOT / "runtime" / "semantik_architect.pgf"

REQUIRED_LANGUAGES = ("WikiEng", "WikiFre")

SMOKE_TREES = (
    'mkBioProf (mkEntityStr "Alan Turing") (strProf "computer scientist")',
    'mkBioNat (mkEntityStr "Alan Turing") (strNat "British")',
    'mkBioFull (mkEntityStr "Alan Turing") (strProf "computer scientist") (strNat "British")',
    'mkEvent (mkEntityStr "Alan Turing") (strEvent "WWII")',
)


def main() -> int:
    try:
        import pgf
    except Exception as exc:
        print(f"ERROR: Python PGF binding is unavailable: {exc}")
        return 2

    if not PGF_PATH.is_file():
        print(f"ERROR: Runtime PGF not found: {PGF_PATH}")
        return 3

    try:
        grammar = pgf.readPGF(str(PGF_PATH))
    except Exception as exc:
        print(f"ERROR: Could not load runtime PGF: {exc}")
        return 4

    available = sorted(grammar.languages.keys())
    missing = [name for name in REQUIRED_LANGUAGES if name not in grammar.languages]

    print(f"PGF: {PGF_PATH}")
    print(f"LANGUAGES: {available}")

    if missing:
        print(f"ERROR: Missing required concrete languages: {missing}")
        return 5

    try:
        for source in SMOKE_TREES:
            expr = pgf.readExpr(source)
            print()
            print(f"TREE: {source}")
            for language in REQUIRED_LANGUAGES:
                text = grammar.languages[language].linearize(expr)
                if not text:
                    print(f"ERROR: Empty linearization for {language}")
                    return 6
                print(f"{language}: {text}")
    except Exception as exc:
        print(f"ERROR: Runtime PGF smoke test failed: {exc}")
        return 7

    print()
    print("SEMANTIK_RUNTIME_PGF_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
