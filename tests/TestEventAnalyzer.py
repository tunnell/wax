"""Place holder
"""
import unittest

from wax.EventAnalyzer import Samples


class SamplesTestCase(unittest.TestCase):

    def test_single_pulse(self):
        doc = {}
        doc['data'] = b''
        self.assertRaises(AssertionError,
                          Samples.get_samples_from_doc,
                          doc, False)


if __name__ == '__main__':
    unittest.main()
