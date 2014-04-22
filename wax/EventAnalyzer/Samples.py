__author__ = 'tunnell'

import snappy
import numpy as np

from wax.core.Configuration import SAMPLE_TYPE


def get_samples_from_doc(doc, is_compressed):
    """From a mongo document, fetch the data payload and decompress if
    necessary

    Args:
       doc (dictionary):  Document from mongodb to analyze

    Returns:
       bytes: decompressed data

    """
    data = doc['data']
    assert len(data) != 0

    if is_compressed:
        data = snappy.uncompress(data)

    data = np.fromstring(data,
                         dtype=SAMPLE_TYPE)
    if len(data) == 0:
        raise IndexError("Data has zero length")

    return data
