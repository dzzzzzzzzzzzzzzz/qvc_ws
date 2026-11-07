import sys
sys.path.append("./MvImport")
from MvCameraControl_class import *
import cv2
import numpy as np
import os

def main():
    # 1. Initialize camera
    deviceList = MV_CC_DEVICE_INFO_LIST()
    ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
    if deviceList.nDeviceNum == 0:
        print("No camera found.")
        return

    stDeviceList = cast(deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
    cam = MvCamera()
    cam.MV_CC_CreateHandle(stDeviceList)
    
    # 2. Set heartbeat timeout to 3 seconds (prevents lock after abnormal exit)
    cam.MV_CC_SetIntValue("GevHeartbeatTimeout", 3000)
    
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print("Open device failed, ret =", ret)
        return

    # 3. Set continuous mode and start grabbing
    cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    cam.MV_CC_StartGrabbing()

    # 4. Create folder for calibration images
    os.makedirs("calib_images", exist_ok=True)
    
    print("=== Calibration image capture mode ===")
    print("Please place the calibration board (checkerboard) in the field of view, move it to different positions and angles.")
    print("Press 's' to save an image, press 'q' to quit.")
    
    # 5. Grab a frame and display
    stParam = MVCC_INTVALUE()
    cam.MV_CC_GetIntValue("PayloadSize", stParam)
    payload_size = stParam.nCurValue
    data_buf = (c_ubyte * payload_size)()
    stFrameInfo = MV_FRAME_OUT_INFO_EX()
    
    img_idx = 0
    while True:
        ret = cam.MV_CC_GetOneFrameTimeout(data_buf, payload_size, stFrameInfo, 1000)
        if ret == 0:
            image = np.frombuffer(data_buf, dtype=np.uint8, count=stFrameInfo.nFrameLen)
            image = image.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
            # Convert to BGR for display (assuming mono8)
            if image.ndim == 2:
                display_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            else:
                display_img = image.copy()
            
            cv2.imshow("Camera View", display_img)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):
                filename = f"calib_images/calib_{img_idx:02d}.png"
                cv2.imwrite(filename, image)
                print(f"Saved: {filename}")
                img_idx += 1
            elif key == ord('q'):
                break
        else:
            print("Grab frame failed, ret =", ret)

    # Cleanup
    cv2.destroyAllWindows()
    cam.MV_CC_StopGrabbing()
    cam.MV_CC_CloseDevice()
    cam.MV_CC_DestroyHandle()

if __name__ == "__main__":
    main()
