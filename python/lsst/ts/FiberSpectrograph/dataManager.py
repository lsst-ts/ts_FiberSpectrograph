# This file is part of ts_FiberSpectrograph.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["SpectrographData", "DataManager"]

import dataclasses
import os.path

import astropy.io.fits
import astropy.time
import astropy.table
import astropy.units as u
import numpy as np


# The version of the FITS file format produced by this class.
FORMAT_VERSION = 1


@dataclasses.dataclass
class SpectrographData:
    """Class to hold data and metadata from a fiber spectrograph.
    """
    wavelength: astropy.units.Quantity
    """The wavelength array produced by the instrument."""
    spectrum: np.ndarray
    """The flux array in instrumental units."""
    duration: float
    """The duration of the exposure in seconds."""
    date_begin: astropy.time
    """The start time of the exposure."""
    date_end: astropy.time
    """The end time of the exposure."""
    type: str
    """The measurement type (see the XML `expose.type` field)."""
    source: str
    """The light source that was measured (see the XML `expose.source` field).
    """
    temperature: astropy.units.Quantity
    """The internal spectrograph temperature."""
    temperature_setpoint: astropy.units.Quantity
    """The internal spectrograph temperature set point."""
    n_pixels: int
    """The number of pixels in the detector."""


class DataManager:
    """A data packager and uploader for output from the Fiber Spectrograph CSC.

    Attributes
    ----------
    instrument : `str`
        The name of the instrument taking the data.
    origin : `str`
        The name of the program that produced this data.
    outpath : `str`, optional
        A path to write the FITS files to.
        **WARNING**: this argument will be removed once the API for writing
        to the LFA becomes available in salobj; do not rely on it.
    """
    def __init__(self, instrument, origin, outpath=None):
        self.instrument = instrument
        self.origin = origin
        self.outpath = outpath

    def __call__(self, data):
        """Generate a FITS hdulist built from SpectrographData.

        Parameters
        ----------
        data : `SpectrographData`
            The data to build the FITS output with.

        Returns
        -------
        uri : `str`
            The file path or other identifier (e.g. s3 store) for where the
            data was sent.
        """
        hdu1 = self.make_primary_hdu(data)
        hdu2 = self.make_wavelength_hdu(data)
        hdulist = astropy.io.fits.HDUList([hdu1, hdu2])
        # TODO: this writeto(file) block should be removed once we have a
        # working LFA API to send data to.
        if self.outpath is not None:
            filename = os.path.join(self.outpath, f"{self.instrument}_{data.date_begin.tai.fits}.fits")
            hdulist.writeto(filename, checksum=True)
            return filename
        else:
            return None

    def make_fits_header(self, data):
        """Return a FITS header built from SpectrographData."""
        hdr = astropy.io.fits.Header()
        # TODO: it would be good to include the dataclass docstrings
        # as comments on each of these, but pydoc can't see them.
        hdr['FORMAT_V'] = FORMAT_VERSION
        hdr['INSTRUME'] = self.instrument
        hdr['ORIGIN'] = self.origin
        hdr['DETSIZE'] = data.n_pixels
        hdr['DATE-BEG'] = astropy.time.Time(data.date_begin).tai.fits
        hdr['DATE-END'] = astropy.time.Time(data.date_end).tai.fits
        hdr['EXPTIME'] = data.duration
        hdr['TIMESYS'] = 'TAI'
        hdr['IMGTYPE'] = data.type
        hdr['SOURCE'] = data.source
        hdr['TEMP_SET'] = data.temperature_setpoint.to_value(u.deg_C)
        hdr['CCDTEMP'] = data.temperature.to_value(u.deg_C)
        return hdr

    def make_primary_hdu(self, data):
        """Return the primary HDU built from SpectrographData."""

        hdu = astropy.io.fits.PrimaryHDU(data=data.spectrum, header=self.make_fits_header(data))
        return hdu

    def make_wavelength_hdu(self, data):
        """Return the wavelength HDU built from SpectrographData."""

        table = astropy.table.QTable([data.wavelength], names=["wavelength"])
        hdu = astropy.io.fits.BinTableHDU(table)
        return hdu