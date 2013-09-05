__author__ = 'tunnell'
__version__ = (0, 0, 1)

from pint import UnitRegistry
ureg = UnitRegistry()
ureg.define('sample =  10 * nanosecond')
Q_ = ureg.Quantity