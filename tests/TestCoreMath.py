from cito.core.math import find_subranges, overlap_region

__author__ = 'tunnell'

import unittest
import numpy as np

class CoreMathTestCase(unittest.TestCase):
    def test_subrange(self):
        self.assertEqual(find_subranges([2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 20]),
                         [[0, 3], [4, 9], [10, 10]])


    def test_overlap_region(self):
        f = overlap_region

        offset = 1000

        indices = np.arange(offset, offset + 10)

        a = (offset, offset + 2)

        self.assertEqual(f(a, (offset+4, offset+6), indices),
                         (None, None))

        c = f(a, a, indices)
        print(c, indices[c[0]:c[1]])
        for index in indices[c[0]:c[1]]:
            self.assertGreaterEqual(index, a[0])
            self.assertLessEqual(index, a[1])



if __name__ == '__main__':
    unittest.main()
