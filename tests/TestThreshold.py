__author__ = 'tunnell'

import unittest

from cito.Trigger import PeakFinder


class ThresholdTestCase(unittest.TestCase):
    def test_subrange(self):
        self.assertEqual(PeakFinder.subranges([2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 20]),
                         [[0, 3], [4, 9], [10, 10]])


if __name__ == '__main__':
    unittest.main()
