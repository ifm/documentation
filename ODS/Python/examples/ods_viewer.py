import cv2
import numpy as np

class OCVWindow:
    def __init__(self, window_name: str):
        self.window_name = window_name
        self.window_created = False
       
    def create_window(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self.window_created = True

    def draw_text(
        self,
        img,
        *,
        text,
        uv_top_left,
        color=(255, 255, 255),
        fontScale=0.6,
        thickness=1,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        outline_color=(0, 0, 0),
        line_spacing=1.5,
    ):
        """
        Draws multiline with an outline.
        """
        assert isinstance(text, str)

        uv_top_left = np.array(uv_top_left, dtype=float)
        assert uv_top_left.shape == (2,)

        for line in text.splitlines():
            (w, h), _ = cv2.getTextSize(
                text=line,
                fontFace=fontFace,
                fontScale=fontScale,
                thickness=thickness,
            )
            uv_bottom_left_i = uv_top_left + [0, h]
            org = tuple(uv_bottom_left_i.astype(int))

            if outline_color is not None:
                cv2.putText(
                    img,
                    text=line,
                    org=org,
                    fontFace=fontFace,
                    fontScale=fontScale,
                    color=outline_color,
                    thickness=thickness * 3,
                    lineType=cv2.LINE_AA,
                )
            cv2.putText(
                img,
                text=line,
                org=org,
                fontFace=fontFace,
                fontScale=fontScale,
                color=color,
                thickness=thickness,
                lineType=cv2.LINE_AA,
            )

            uv_top_left += [0, h * line_spacing]

    def update_image(self, image: np.ndarray = np.zeros((100, 100), np.uint8), text=[]):
        keypress = -1
        if self.window_created:
            if image is not None:           
                self.draw_text(
                        img=image,
                        text=text,
                        uv_top_left=(10,10))
                cv2.imshow(self.window_name, image)
                keypress = cv2.waitKey(1)
        else:
            raise Exception("Window not created yet. Call create_window() first")
        return keypress

    def destroy(self):
        try:
            cv2.destroyWindow(self.window_name)
        except Exception as err:
            # recurrent issues with closing windows:
            if "578" in str(err): # on linux
                # OpenCV(4.7.0) /io/opencv/modules/highgui/src/window_QT.cpp:578:
                # error: (-27:Null pointer) NULL guiReceiver
                # (please create a window) in function 'cvDestroyWindow'
                pass
            elif "window_w32.cpp:1261" in str(err): # on Win10
                pass
            else:
                raise err
        self.window_created = False