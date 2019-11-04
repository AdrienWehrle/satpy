#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2019 Satpy developers
#
# This file is part of satpy.
#
# satpy is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# satpy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# satpy.  If not, see <http://www.gnu.org/licenses/>.

"""Unittesting the  SEVIRI L2 Bufr reader."""

import sys

import numpy as np

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

try:
    from unittest import mock
except ImportError:
    import mock


class TestMSGBufr(unittest.TestCase):
    """Test NativeMSGBufrHandler."""

    @unittest.skipIf(sys.platform.startswith('win'), "'eccodes' not supported on Windows")
    def msg_bufr_test(self,):
        """Test the MSG Bufr Handler."""
        from satpy.readers.seviri_l2_bufr import MSGBUFRFileHandler
        import eccodes as ec
        buf1 = ec.codes_bufr_new_from_samples('BUFR4_local_satellite')
        ec.codes_set(buf1, 'unpac'
                           'k', 1)
        samp1 = np.random.uniform(low=250, high=350, size=(128,))
        samp2 = np.random.uniform(low=-60, high=60, size=(128,))
        samp3 = np.random.uniform(low=10, high=60, size=(128,))
        # write the bufr test data twice as we want to read in and the concatenate the data in the reader
        ec.codes_set_array(buf1, '#1#brightnessTemperature', samp1)
        ec.codes_set_array(buf1, '#1#brightnessTemperature', samp1)
        ec.codes_set_array(buf1, 'latitude', samp2)
        ec.codes_set_array(buf1, 'latitude', samp2)
        ec.codes_set_array(buf1, 'longitude', samp3)
        ec.codes_set_array(buf1, 'longitude', samp3)
        info = {'satellite': 'meteosat9', 'subsat': 'E0000',
                'start_time': '201909180000',
                'key': '#1#brightnessTemperature', 'units': 'm',
                'wavelength': 10, 'standard_name': 'met9',
                'fill_value': 0
                }
        info2 = {'file_type':  'seviri_l2_bufr_csr'}

        fh = MSGBUFRFileHandler(None, info, info2)
        m = mock.mock_open()
        with mock.patch('satpy.readers.seviri_l2_bufr.open', m, create=True):
            with mock.patch('eccodes.codes_bufr_new_from_file',
                            side_effect=[buf1, buf1, None, buf1, buf1, None, buf1, buf1, None]) as ec1:
                ec1.return_value = ec1.side_effect
                with mock.patch('eccodes.codes_set') as ec2:
                    ec2.return_value = 1
                    with mock.patch('eccodes.codes_release') as ec5:
                        ec5.return_value = 1
                        z = fh.get_dataset(None, info)
                        # concatenate the original test arrays as
                        # get dataset will have read and concatented the data
                        x1 = np.concatenate((samp1, samp1), axis=0)
                        x2 = np.concatenate((samp2, samp2), axis=0)
                        x3 = np.concatenate((samp3, samp3), axis=0)
                        np.testing.assert_array_equal(z.values, x1)
                        np.testing.assert_array_equal(z.coords['latitude'].values, x2)
                        np.testing.assert_array_equal(z.coords['longitude'].values, x3)
                        self.assertEqual(z.attrs['satellite'], info['satellite'])
                        self.assertEqual(z.attrs['standard_name'], info['standard_name'])

    def test_msg_bufr(self):
        """Call the test function."""
        self.msg_bufr_test()


def suite():
    """Test suite for test_scene."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestMSGBufr))
    return mysuite


if __name__ == "__main__":
    # So you can run tests from this module individually.
    unittest.main()