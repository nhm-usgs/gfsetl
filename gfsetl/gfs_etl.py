"""Main module."""
from pathlib import Path
import requests
import xarray
from datetime import datetime

class GFSEtl:

    def __init__(self, period=None, prefix=None, inpath=None, outpath=None, weightsfile=None):
        self._start_date = period[0]
        self._end_date = period[1]
        self._fileprefix = prefix
        self._iptpath = inpath
        self._optpath = outpath
        self._wghts_file = weightsfile
        if self._start_date > self._end_date:
            raise ValueError(
                "start date ({0}) must be before end date ({1})".format(
                    self.start_date, self.end_date
                )
            )
        if self._end_date > datetime.now():
            raise ValueError(
                "end date cannot be a future date ({0} > {1}".format(
                    self.end_date, datetime.date.today()
                )
            )

