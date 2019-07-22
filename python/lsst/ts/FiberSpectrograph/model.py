# import time
import asyncio

from lsst.ts.FiberSpectrograph.fibspec import MeasConfigType, DeviceConfigType, \
    AVS


class FiberSpec(object):

    def __init__(self):
        """Setup FiberSpectrograph
        Get information of the FiberSpectrograph: serial number, handle of the
        connected instrument. On start this method is executed.
        """
        self.serialNumber = 0
        self.configuration = MeasConfigType
        self.devCon = DeviceConfigType
        self.dev_handle = 0
        self.pixels = 4095
        self.spectralData = [0.0] * 4096
        self.waveLength = [0.0] * 4096
        self.f = AVS()
        self.f.init(0)
        print(f"init(0) -> {self.f.init(0)}")
        # Number of usb FiberSpectrograph connected
        NumDevices = self.f.getNumberOfDevices()
        print(f"getNumberOfDevices() -> {NumDevices}")
        # List of FiberSpectrograph
        a, b = self.f.getList()
        print(f"getList() -> {a} {b}")
        # Serial Number of 1st FiberSpectrograph from the list
        self.serialNumber = str(b[0].SerialNumber.decode("utf-8"))
        print(f"SerialNumber -> {self.serialNumber}")
        # Activate 1st FiberSpectrograph and get the handle of the device
        self.dev_handle = self.f.activate(b[0])
        print(f"devHandle -> {self.dev_handle}")
        self.devcon = DeviceConfigType
        ret = self.f.getParameter(self.dev_handle, 0)
        print(f"AVS_GetParameter(self.dev_handle, 0) -> {ret}")

    def closeComm(self):
        """Close communication and release all internal data storage
        The close function (AVS_Done()) closes the communication port(s) and
        releases all internal data storage.
        Return SUCCESS
        """
        self.f.done()
        return

    async def captureSpectImage(self, m_IntegrationTime):
        """Capture Spectrum for the integration time specified.
        Capture Spectrum for the integration time specified.
        """
        ret = self.f.useHighResADC(self.dev_handle, True)
        print(f"useHighResADC(self.dev_handle, True) -> {ret}")
        measconfig = MeasConfigType()
        measconfig.m_StartPixel = 0
        measconfig.m_StopPixel = 2047
        measconfig.m_IntegrationTime = m_IntegrationTime
        measconfig.m_IntegrationDelay = 0
        measconfig.m_NrAverages = 1
        measconfig.m_CorDynDark_m_Enable = 0  # nesting of types does NOT work!!
        measconfig.m_CorDynDark_m_ForgetPercentage = 0
        measconfig.m_Smoothing_m_SmoothPix = 0
        measconfig.m_Smoothing_m_SmoothModel = 0
        measconfig.m_SaturationDetection = 0
        measconfig.m_Trigger_m_Mode = 0
        measconfig.m_Trigger_m_Source = 0
        measconfig.m_Trigger_m_SourceType = 0
        measconfig.m_Control_m_StrobeControl = 0
        measconfig.m_Control_m_LaserDelay = 0
        measconfig.m_Control_m_LaserWidth = 0
        measconfig.m_Control_m_LaserWaveLength = 0.0
        measconfig.m_Control_m_StoreToRam = 0
        # Prepares measurement on the spectrometer using the specified
        # measurement configuration.
        ret = self.f.prepareMeasure(self.dev_handle, measconfig)
        print(f"prepareMeasure({self.dev_handle}, measconfig) -> {ret}")
        # Prepares measurement on the spectrometer using the specified
        # measurement configuration.
        ret = self.f.measure(self.dev_handle, 1)
        print(f"measure({(self.dev_handle,1)} -> {ret}")
        dataready = False
        while (dataready is False):
            dataready = (self.f.pollScan(self.dev_handle) is True)
            print(f"dataready is -> {dataready}")
            await asyncio.sleep(0.1)
        if (dataready is True):
            self.handle_newdata()

        return

    def stopMeas(self):
        """Stops the measurement
        Stops the measurements (needed if Nmsr = infinite), can also be used to
        stop a pending measurement with long integration time and/or
        high number of averages
        Returns
        -------
        integer
            0 for success
            error code as defined in AVAReturnCodes in fibSpec.py
        """
        ret = self.f.stopMeasure(self.dev_handle)
        return ret

    def handle_newdata(self):
        """After Capturing spectrum this method is used to get Wavelength data
        and intensity data
        PollScan is used to determine if the capture spectrum is complete.
        Once pollscan=1, data is ready and can be retrieved from the
        FiberSpectrograph instrument.
        getLambda and getScopeData is used to get the wavelength data and
        intensity of light respectively.
        """
        print("In handle_newdata")
        # Get Wavelength data for pixel index 0 to 4095
        ret, measurement = self.f.getLambda(self.dev_handle, 4096)
        print(f"AVS_getLambda data -> {ret}")
        print("The first 10 measurement points are %s." % measurement[:10])
        # Get intensity of measured light for pixel index 0 to 4095
        ret, self.spectralData, intensity = self.f.getScopeData(self.dev_handle, 4096)
        print("The first 10 intensity points are %s." % intensity[:10])

        return
