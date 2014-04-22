from wax.core.math import find_subranges, overlap_region, speed_in1d_continous

__author__ = 'tunnell'

import unittest
import numpy as np


class CoreMathTestCase(unittest.TestCase):
    def setUp(self):
        self.testcases = []
        max = 10

        for a in range(max):
            for b in range(max):
                for x in range(max):
                    for y in range(max):
                        if b < a:
                            continue
                        elif y < x:
                            continue
                        else:
                            self.testcases.append([a, b, x, y])

    def test_subrange(self):
        self.assertEqual(find_subranges([2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 20]),
                         [[0, 3], [4, 9], [10, 10]])

    def test_overlap_region(self):
        f = overlap_region

        offset = 1000

        a = (offset, offset + 2)

        self.assertEqual(f(a, (offset + 4, offset + 6)),
                         (None, None))

    def in1d_helper(self, a, b, x, y):
        array1 = np.arange(a, b)
        array2 = np.arange(x, y)

        answer = np.in1d(array1, array2)
        my_answer = speed_in1d_continous(a, b, x, y)
        if not (my_answer == answer).all():
            print('fail.')
            print('answer:', answer)
            print('my answer:', my_answer)
        self.assertEqual(my_answer.size, answer.size)
        self.assertTrue((my_answer == answer).all())

    def test_all_before(self):
        self.in1d_helper(0, 10, 100, 200)

    def test_all_after(self):
        self.in1d_helper(100, 200, 0, 10)

    def test_equal(self):
        self.in1d_helper(3, 15, 3, 15)

    def test_test_all(self):
        """Test all permutations"""
        for a, b, x, y in self.testcases:
            self.in1d_helper(a, b, x, y)

if __name__ == '__main__':
    unittest.main()
