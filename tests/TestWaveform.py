__author__ = 'tunnell'

import unittest
from cito.core import Waveform


class WaveformTestCase(unittest.TestCase):
    def test_empty_value_error(self):
        with self.assertRaises(ValueError):
            Waveform.get_samples(b'')



if __name__ == '__main__':
    unittest.main()
