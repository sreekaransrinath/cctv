from face_recognition.api import face_locations
from fastapi import FastAPI
import cv2
import face_recognition
from fastapi import Request, Response
from fastapi import Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

CHUNK_SIZE = 1024*1024
app = FastAPI()

app.mount("/view", StaticFiles(directory="view"), name="view")

video_capture = cv2.VideoCapture("/dev/video0")

xml_template = """
<annotation>
  <folder>abcd</folder>
  <filename>abcd.jpg</filename>
  <path>/pqrs/abcd/</path>
  <source>
    <database>Unknown</database>
  </source>
  <segmented>0</segmented>
  <object>
    <name>person</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <bndbox>
      <width>{}</width>
      <height>{}</height>
    </bndbox>
  </object>
</annotation>
"""


@app.get("/")
async def root():
    width, height = get_obj_data()
    if (width == None) or (height == None):
        return {}
    return {
        "dimensions": {
            "width": width,
            "height": height
        },
        "object_name": "person",
        # "message": "SUCCESS",
        # "status_code": 200
    }


@app.get("/xml")
async def xml():
    width, height = get_obj_data()
    if (width == None) or (height == None):
        return ""
    return xml_template.format(width, height)


# @app.get("/video")
def gen_frames():  
    while True:
        success, frame = video_capture.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video')
def video_feed(_):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
# async def video_endpoint(range: str = Header(None)):
#     # print(range)
#     start, end = range.replace("bytes=", "").split("-")
#     start = int(start)
#     end = int(end) if end else start + CHUNK_SIZE
#     # with open(video_capture, "rb") as video:
#     # video.seek(start)
#     data = video_capture.read(end - start)
#     filesize = str(video_capture.stat().st_size)
#     headers = {
#         'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
#         'Accept-Ranges': 'bytes'
#     }
#     return Response(data, status_code=206, headers=headers, media_type="video/mp4")


def get_obj_data():
    # Grab a single frame of video
    ret, frame = video_capture.read()
    ret, frame = video_capture.read()
    # ret, frame = video_capture.read()
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]
    # Find all the faces in the current frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    if len(face_locations) == 0:
        return (None, None)
    top, left, bottom, right = face_locations[0]
    return (right - left, bottom - top)


# @app.get("/view")
# async def view():
#     return templates.TemplateResponse("index.htm", {"request": request, "id": id})