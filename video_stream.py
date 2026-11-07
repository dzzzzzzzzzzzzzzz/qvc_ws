import sys
import cv2
import numpy as np
sys.path.append("./MvImport")
from MvCameraControl_class import *

def main():
    # 1. Initialize and open the camera
    deviceList = MV_CC_DEVICE_INFO_LIST()
    ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
    if deviceList.nDeviceNum == 0:
        print("No camera found.")
        return

    stDeviceList = cast(deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
    cam = MvCamera()
    cam.MV_CC_CreateHandle(stDeviceList)
    
    # Set heartbeat to prevent 60-second lock
    cam.MV_CC_SetIntValue("GevHeartbeatTimeout", 3000)
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print("Open device failed, ret =", ret)
        return

    # 2. Set continuous acquisition mode
    cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    cam.MV_CC_StartGrabbing()

    # Prepare buffer
    stParam = MVCC_INTVALUE()
    cam.MV_CC_GetIntValue("PayloadSize", stParam)
    payload_size = stParam.nCurValue
    data_buf = (c_ubyte * payload_size)()
    stFrameInfo = MV_FRAME_OUT_INFO_EX()

    print("Streaming... Press 'q' to quit.")
    
    try:
        while True:
            # 3. Pull a frame
            ret = cam.MV_CC_GetOneFrameTimeout(data_buf, payload_size, stFrameInfo, 1000)
            if ret == 0:
                # Convert to numpy array
                image = np.frombuffer(data_buf, dtype=np.uint8, count=stFrameInfo.nFrameLen)
                image = image.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
                
                # 4. Display
                # Note: If the image is too large (3072x2048), cv2.imshow may be slow.
                # You can use cv2.resize to zoom out for display.
                display_img = cv2.resize(image, (768, 512)) 
                cv2.imshow("Hikrobot Stream", display_img)
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("Grab frame failed, ret =", ret)
    finally:
        # 5. Ensure safe release
        cv2.destroyAllWindows()
        cam.MV_CC_StopGrabbing()
        cam.MV_CC_CloseDevice()
        cam.MV_CC_DestroyHandle()

if __name__ == "__main__":
    main()
