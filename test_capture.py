import sys
import cv2
import numpy as np
sys.path.append("./MvImport")  # Add MvImport to the Python path
from MvCameraControl_class import *

def main():
    # Enumerate devices
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print(f"Enum devices failed! Error code: {ret}")
        return

    if deviceList.nDeviceNum == 0:
        print("No camera found.")
        return

    print(f"Found {deviceList.nDeviceNum} camera(s).")

    # Create camera object and open the first device
    stDeviceList = cast(deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
    camera = MvCamera()
    ret = camera.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print(f"Create handle failed! Error code: {ret}")
        return

    ret = camera.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print(f"Open device failed! Error code: {ret}")
        return

    # Set continuous acquisition mode
    camera.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)

    # Start grabbing
    ret = camera.MV_CC_StartGrabbing()
    if ret != 0:
        print(f"Start grabbing failed! Error code: {ret}")
        return

    # Grab one frame
    stParam = MVCC_INTVALUE()
    camera.MV_CC_GetIntValue("PayloadSize", stParam)
    payload_size = stParam.nCurValue

    data_buf = (c_ubyte * payload_size)()
    stFrameInfo = MV_FRAME_OUT_INFO_EX()
    ret = camera.MV_CC_GetOneFrameTimeout(data_buf, payload_size, stFrameInfo, 1000)
    
    if ret == 0:
        print(f"Got frame: Width={stFrameInfo.nWidth}, Height={stFrameInfo.nHeight}")
        # Convert to numpy array
        image = np.frombuffer(data_buf, dtype=np.uint8, count=stFrameInfo.nFrameLen)
        image = image.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
        
        # Save image (supports grayscale or BGR depending on pixel format)
        cv2.imwrite("captured_frame.png", image)
        print("Frame saved as captured_frame.png")
    else:
        print(f"Grab frame failed! Error code: {ret}")

    # Stop and close
    camera.MV_CC_StopGrabbing()
    camera.MV_CC_CloseDevice()
    camera.MV_CC_DestroyHandle()

if __name__ == "__main__":
    main()
