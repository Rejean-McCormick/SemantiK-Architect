from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import unesco_candidate_probe as probe

class CandidateProbeTests(unittest.TestCase):
    def test_unknown_candidate_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'requests').mkdir();(root/'results').mkdir()
            with self.assertRaises((OSError,ValueError)):
                probe.run(root/'missing',root/'requests',root/'results',None)

    def test_nonempty_results_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for n in ('candidate','requests','results'):(root/n).mkdir()
            (root/'results'/'should-not-overwrite.json').write_text('{}')
            with self.assertRaises(ValueError):
                probe.run(root/'candidate',root/'requests',root/'results',None)

if __name__=='__main__':unittest.main()
