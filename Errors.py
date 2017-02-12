from printstyle import *
class ExperimentalError(Exception):
    pass
class NoExtinction(ExperimentalError):
    pass
class FailLocking(ExperimentalError):
    pass
class FailSpectrumScan(ExperimentalError):
    #printstyle_warning("Fail Spectrum Scanning")
    pass
class HighVoltage(ExperimentalError):
    pass
