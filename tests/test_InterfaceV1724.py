#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cito
----------------------------------

Tests for `cito` module.
"""

try:
    import numpypy
except:
    pass

import unittest

import numpy as np

from cito.core import InterfaceV1724


class BaseInterfaceV1724():

    def _testGoodData(self):
        #  Not nice to include raw data in a file, but this ensures the test and raw data are in sync.
        #  This data is already unzipped
        data = b'\x0c\x02\x00\xa0\xff\x00\x00\x01\xbd\x1d\x00\x00$\xd6z\x8bA\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x83>\x82>\x84>\x83>\x82>\x82>\x84>\x83>\x81>\x83>\x84>\x83>\x85>\x84>\x83>\x83>\x83>\x82>\x82>\x83>\x83>\x84>\x81>\x81>\x81>\x82>\x84>\x82>\x82>\x82>\x83>\x84>\x80>\x84>\x81>\x83>\x84>\x82>\x83>\x83>\x84>\x82>\x83>\x80>\x83>\x82>\x80>\x82>\x82>\x84>\x82>\x82>\x82>\x82>\x82>\x84>\x83>\x82>\x83>\x84>\x83>\x81>\x82>\x83>\x82>\x83>\x83>\x84>\x82>\x84>\x82>\x83>\x84>\x82>\x82>\x82>\x83>\x84>\x83>\x81>\x83>\x82>\x82>\x82>\x82>\x82>\x84>\x84>\x83>\x83>\x81>\x82>\x84>\x83>\x83>\x83>\x82>\x85>\x82>\x81>y>\xf7,\x10&\xcd$\x99$\x8d$\x83$~$a,\xae:\xf4=s>\x83>\x84>\x84>\x84>\x83>\x82>\x85>\x83>\x82>\x83>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x82>\x83>\x81>\x82>\x82>\x82>\x82>\x82>\x83>\x81>\x80>\x81>\x82>\x83>\x81>\x82>\x81>\x82>\x81>\x82>\x81>\x82>\x81>\x80>\x82>\x81>\x82>\x80>\x82>\x82>\x81>\x82>\x82>\x84>\x81>\x7f>\x81>\x80>\x81>\x80>\x82>\x82>\x82>\x81>\x83>\x82>\x81>\x81>\x81>\x83>\x81>\x81>\x81>\x81>\x82>\x82>\x82>\x81>\x83>\x80>\x83>\x80>\x82>\x81>\x7f>\x80>\x83>\x80>\x82>\x81>\x82>\x81>\x81>\x82>\x80>\x81>\x7f>\x81>\x84>\x81>\x81>\x82>\x82>\x80>\x82>\x80>\x82>\x81>\x80>\x80>\x80>\x81>\x83>\x82>\x80>\x81>\x84>\x82>\x80>\x82>e>\xbb,#&\xee$\xbe$\xb1$\xa8$\xa0$\xf4,\xcd:\xf5=o>|>\x7f>\x81>\x81>\x81>\x81>\x81>\x80>\x82>\x81>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x80>\x81>\x83>\x83>\x82>\x81>\x80>\x81>\x80>\x81>\x80>\x81>\x81>\x7f>\x80>\x81>\x80>\x81>\x7f>\x80>\x81>~>\x80>\x7f>\x81>\x82>\x7f>\x80>\x7f>\x81>\x80>\x7f>\x81>\x83>\x80>\x81>\x82>\x80>\x82>\x83>\x82>\x80>\x80>\x80>\x81>\x80>\x80>~>\x81>\x81>\x81>\x7f>\x80>\x7f>\x80>\x7f>\x81>\x82>\x82>\x81>~>\x7f>\x80>\x81>\x82>\x81>\x80>\x80>\x81>\x7f>\x81>\x82>\x80>\x81>\x80>\x80>\x80>~>\x80>\x81>\x80>\x81>\x82>\x81>\x81>\x81>\x80>\x81>\x7f>\x82>\x80>\x81>\x81>\x7f>\x81>\x81>\x80>\x7f>\x83>\x80>t>\xdc,\x04&\xc3$\x92$\x82${$s$\x80,\xa2:\xf0=p>\x81>\x84>\x83>\x81>\x80>\x82>\x83>\x81>\x81>\x81>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x83>\x83>\x84>\x83>\x83>\x81>\x84>\x83>\x82>\x85>\x84>\x84>\x83>\x82>\x84>\x84>\x82>\x82>\x83>\x83>\x85>\x83>\x84>\x84>\x84>\x84>\x84>\x83>\x83>\x84>\x83>\x84>\x84>\x84>\x83>\x82>\x82>\x85>\x83>\x84>\x82>\x83>\x85>\x85>\x84>\x83>\x84>\x84>\x83>\x84>\x84>\x84>\x83>\x83>\x84>\x84>\x86>\x83>\x84>\x85>\x82>\x84>\x81>\x83>\x85>\x83>\x85>\x83>\x83>\x84>\x84>\x85>\x84>\x84>\x83>\x82>\x83>\x83>\x83>\x84>\x83>\x83>\x83>\x83>\x85>\x84>\x83>\x83>\x84>\x83>\x84>\x83>\x85>\x85>\x86>\x84>\x83>\x83>\x85>\x85>~>\x01-\x1b&\xd4$\x9f$\x94$\x89$\x82$T,\xa6:\xf3=s>\x83>\x85>\x84>\x84>\x83>\x83>\x85>\x82>\x85>\x83>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x81>\x7f>~>\x80>\x80>~>\x81>\x81>~>~>\x81>\x80>\x7f>~>~>\x80>\x81>\x81>\x80>\x7f>\x80>\x81>~>\x7f>\x81>\x80>\x7f>\x80>\x80>\x80>\x81>\x80>\x81>\x80>\x80>\x80>\x81>\x7f>\x81>\x80>\x82>\x81>\x80>\x81>\x7f>\x7f>}>~>\x7f>\x80>\x80>\x80>\x7f>\x80>\x7f>~>\x7f>\x7f>\x80>\x81>\x7f>\x80>\x7f>\x81>}>~>\x7f>\x7f>\x80>\x7f>\x7f>\x7f>\x7f>}>\x7f>\x7f>~>\x80>\x82>\x7f>\x80>\x7f>\x7f>\x81>\x7f>\x7f>\x7f>\x80>\x7f>\x80>\x81>\x80>~>\x81>\x81>\x80>~>\x80>\x7f>~>w>v,8%\xe8#\xb0#\xa5#\x99#\x90#\x00+E:\xdf=l>~>\x81>\x80>\x80>\x80>\x80>\x80>\x7f>~>\x80>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x81>\x81>\x81>\x81>\x80>\x81>\x81>\x7f>\x81>\x80>\x80>\x80>\x81>\x81>~>~>\x7f>\x81>\x81>\x81>\x81>\x80>\x80>\x81>\x80>\x81>\x80>\x7f>\x80>\x80>\x81>\x7f>\x81>\x80>\x80>\x80>\x80>\x81>\x80>\x81>\x80>\x81>\x81>\x7f>\x80>\x81>\x80>\x80>\x81>\x80>\x81>\x81>\x81>\x81>\x82>\x80>\x81>\x82>\x81>\x83>\x80>\x81>\x80>\x81>\x80>\x81>\x80>\x80>\x7f>\x82>\x80>\x80>\x82>~>\x80>\x80>\x81>\x82>\x82>\x80>\x80>\x7f>\x7f>\x81>\x81>\x7f>\x80>\x82>\x80>\x82>\x80>\x80>\x80>\x82>\x81>\x82>\x81>\x81>\x82>\x83>z>\xcf,\xdb%\x98$_$Q$H$@$\xd9+\x87:\xec=n>\x7f>\x82>\x82>\x82>\x83>\x83>\x83>\x7f>\x80>\x82>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x82>\x84>\x85>\x84>\x82>\x85>\x86>\x83>\x81>\x83>\x84>\x84>\x84>\x84>\x84>\x84>\x83>\x85>\x85>\x85>\x86>\x84>\x84>\x83>\x83>\x83>\x83>\x82>\x84>\x85>\x83>\x84>\x83>\x83>\x82>\x85>\x85>\x83>\x84>\x83>\x83>\x82>\x82>\x84>\x85>\x83>\x83>\x82>\x83>\x84>\x82>\x83>\x82>\x85>\x82>\x84>\x81>\x84>\x85>\x82>\x85>\x83>\x84>\x84>\x85>\x86>\x82>\x82>\x82>\x82>\x85>\x86>\x84>\x83>\x83>\x86>\x85>\x83>\x83>\x83>\x83>\x82>\x83>\x84>\x83>\x84>\x86>\x84>\x85>\x84>\x82>\x83>\x83>\x83>\x84>\x83>\x85>\x84>\x85>\x84>v>D,5%\xef#\xbb#\xac#\xa0#\x99#D+l:\xeb=s>\x84>\x84>\x85>\x85>\x89>\x84>\x86>\x84>\x85>\x85>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x89>\x89>\x8a>\x89>\x89>\x87>\x8c>\x89>\x8a>\x8b>\x8a>\x88>\x8a>\x89>\x88>\x8b>\x89>\x89>\x8a>\x89>\x8b>\x89>\x8b>\x8a>\x8a>\x8a>\x89>\x8a>\x88>\x88>\x8a>\x8a>\x88>\x89>\x89>\x8b>\x8b>\x8a>\x88>\x88>\x8a>\x8b>\x8a>\x8a>\x8a>\x8b>\x88>\x89>\x8b>\x89>\x88>\x89>\x8a>\x89>\x8a>\x8a>\x8b>\x8a>\x89>\x8a>\x88>\x8a>\x8a>\x88>\x88>\x8b>\x89>\x8a>\x88>\x89>\x88>\x8a>\x8c>\x8c>\x88>\x8a>\x8b>\x8c>\x8a>\x8a>\x88>\x8a>\x89>\x88>\x8a>\x8b>\x89>\x8b>\x89>\x89>\x8a>\x89>\x8a>\x8a>\x89>\x8a>\x8b>\x8a>\x88>\x89>\x87>\xf6,\xe4%\x9e$i$Y$P$I$\xa8+\x84:\xf2=x>\x87>\x89>\x8a>\x87>\x8a>\x8a>\x8b>\x89>\x8a>\x89>\xd8\x00\x00\x00'

        data = np.fromstring(data,
                             dtype=np.uint32)
        return data

    def _testBadData(self):
        """Return list of bad data
        """

        # This was caused by a channel in the middle having size zero and being
        # corrupted.  Should raise assertion error.
        data = [np.fromstring(b"00000000",dtype=np.uint32),
                np.fromstring(b'\x81>\x80>\x82>\x83>\x81>\x81>\x81>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x83>\x83>\x84>\x83>\x83>\x81>\x84>\x83>\x82>\x85>\x84>\x84>\x83>\x82>\x84>\x84>\x82>\x82>\x83>\x83>\x85>\x83>\x84>\x84>\x84>\x84>\x84>\x83>\x83>\x84>\x83>\x84>\x84>\x84>\x83>\x82>\x82>\x85>\x83>\x84>\x82>\x83>\x85>\x85>\x84>\x83>\x84>\x84>\x83>\x84>\x84>\x84>\x83>\x83>\x84>\x84>\x86>\x83>\x84>\x85>\x82>\x84>\x81>\x83>\x85>\x83>\x85>\x83>\x83>\x84>\x84>\x85>\x84>\x84>\x83>\x82>\x83>\x83>\x83>\x84>\x83>\x83>\x83>\x83>\x85>\x84>\x83>\x83>\x84>\x83>\x84>\x83>\x85>\x85>\x86>\x84>\x83>\x83>\x85>\x85>~>\x01-\x1b&\xd4$\x9f$\x94$\x89$\x82$T,\xa6:\xf3=s>\x83>\x85>\x84>\x84>\x83>\x83>\x85>\x82>\x85>\x83>\xd8\x00\x00\x00A\x00\x00\x00\xeb\x00\x00\x00=\x00\x00\x80\x81>\x7f>~>\x80>\x80>~>\x81>\x81>~>~>\x81>', dtype=np.uint32)]
        return data

    def _get_n_digitizers(self):
        return 8

    def setUp(self):
        raise NotImplementedError()

    def test_trigger_time_tag(self):
        data = self._testGoodData()
        ttt = self.interfaceClass.get_trigger_time_tag(data)
        self.assertEqual(ttt, 192599588)

    def test_check_header(self):
        data = self._testGoodData()
        self.interfaceClass.check_header(data)

    def test_get_size_value(self):
        data = self._testGoodData()
        data_size = self.interfaceClass.get_block_size(data)
        self.assertEqual(data_size, 524)

        #  Crop data so header size isn't data size
        self.assertRaises(AssertionError,
                          self.interfaceClass.get_block_size,
                          data[0:int(len(data) / 2)])

    def test_get_waveform(self):
        data = self._testGoodData()
        result = self.interfaceClass.get_waveform(data, 2 * len(data))
        self.assertEqual(self._get_n_digitizers(),
                         len(result))
        self.assertIsInstance(result,
                              list)

        for i in range(self._get_n_digitizers()):
            self.assertIsInstance(result[i],
                                  tuple)
            self.assertEqual(len(result[i]),
                             3)
            self.assertIsInstance(result[i][0], int)
            self.assertIsInstance(result[i][1], np.ndarray)
            self.assertIsInstance(result[i][2], np.ndarray)

        expected_result = (
            np.array(
                [383,  385,  386,  384,  384,  386,  383,  383,  386,  386,  383,
                 384,  385,  386,  386,  384,  383,  383,  384,  385,  384,  383,
                 386,  385,  383,  384,  385,  384,  384,  384,  383,  384,  383,
                 384,  384,  384,  383,  385,  383,  384,  382,  383,  384,  383,
                 385,  385,  387,  386,  385,  384,  384,  384,  385,  384,  385,
                 386,  385,  385,  384,  383,  385,  384,  385,  383,  387,  386,
                 385,  385,  384,  385,  385,  385,  385,  387,  385,  385,  386,
                 384,  382,  385,  384,  385,  385,  383,  385,  385,  385,  384,
                 385,  384,  383,  384,  386,  383,  383,  384,  386,  384,  385,
                 386,  393, 5002, 6856, 7192, 7248, 7259, 7271, 7280, 5376, 1467,
                 545,  404,  386,  383,  384,  384,  384,  384,  384,  385,  386,
                 384], dtype=np.int16),
            np.array(
                [131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143,
                 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156,
                 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169,
                 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182,
                 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195,
                 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208,
                 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221,
                 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234,
                 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247,
                 248, 249, 250, 251, 252]))

        i, x, y = result[4]
        self.assertEqual(x.size, y.size)

        for i in range(x.size):
            self.assertEqual(x[i], expected_result[0][i])
            self.assertEqual(y[i], expected_result[1][i])

    def tearDown(self):
        pass


class TestInterface1724(unittest.TestCase, BaseInterfaceV1724):

    def setUp(self):
        self.interfaceClass = InterfaceV1724

    def test_bad_data(self):
        bad_data_list = self._testBadData()
        for data in bad_data_list:
            self.assertRaises(AssertionError,
                              self.interfaceClass.get_trigger_time_tag,
                              data)
            self.assertRaises(AssertionError,
                              self.interfaceClass.get_block_size,
                              data)
            self.assertRaises(AssertionError,
                              self.interfaceClass.check_header,
                              data)


if __name__ == '__main__':
    unittest.main()
