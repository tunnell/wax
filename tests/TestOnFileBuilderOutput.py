"""Example of how to use cito to analyze data
"""
import pickle
import numpy as np
import gzip


import unittest


class SumDataTestCase(unittest.TestCase):

    def setUp(self):
        # Load the wax output file
        self.f = gzip.open('tests/cito_file.pklz', 'rb')

    def test_type(self):
        """Check indices type"""
        self.f.seek(0)
        pickle.load(self.f)  # version

        while 1:
            try:
                doc = pickle.load(self.f)
            except EOFError:
                break

            for channel, data2 in doc['data'].items():
                self.assertEqual(data2['indices'].dtype, np.int32)

    def test_indices(self):
        """Test that sum waveform indecies are also seen by PMTs, and vice versa"""

        self.f.seek(0)
        pickle.load(self.f)  # version
        while 1:
            try:
                doc = pickle.load(self.f)
            except EOFError:
                break

            channel_indices = np.array([], dtype=np.int32)
            sum_indices = doc['data']['sum']['indices']

            for channel, data2 in doc['data'].items():
                if type(channel) == str and ('sum' in channel or 'smooth' in channel):
                    continue

                channel_indices = np.concatenate((data2['indices'],
                                                  channel_indices))

            channel_indices = np.unique(channel_indices)
            self.assertEqual(len(channel_indices), len(sum_indices))
            self.assertTrue((channel_indices == sum_indices).all())


if __name__ == '__main__':
    unittest.main()
