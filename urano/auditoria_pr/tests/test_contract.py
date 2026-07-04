import hashlib
import unittest

from urano.auditoria_pr.core import KairosUranoPipeline, RawObservation


class ContractTests(unittest.TestCase):
    def test_observation_uses_full_hash(self):
        value = "interface boa"
        record = RawObservation(raw_content=value, source_ref="sample:1")
        self.assertEqual(record.content_sha256, hashlib.sha256(value.encode("utf-8")).hexdigest())
        self.assertEqual(len(record.content_sha256), 64)

    def test_pipeline_preserves_a_single_raw_record(self):
        result = KairosUranoPipeline().run([("design lindo mas atendimento péssimo", "sample:2")])
        self.assertEqual(len(result["observations"]), 1)


if __name__ == "__main__":
    unittest.main()
