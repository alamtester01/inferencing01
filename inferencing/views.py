# from django.shortcuts import render
# from django.http import HttpResponse
# from rest_framework.decorators import api_view
# from ultralytics import YOLO
# from django.contrib.staticfiles import finders
# import os
# import pathlib
# from . import serializers
# from io import BytesIO
# from PIL import Image
# from .forms import FileForm
# import base64

# MODULE_DIR = pathlib.Path(__file__).parent
# model = YOLO(f'./yolov8n.pt')

# def index(request):
#     if request.method=='POST':
        
#         # can't save the file with different file extension

#         form = FileForm(request.POST, request.FILES)
#         if form.is_valid():

#             input_file_extension = request.FILES['file'].content_type.split('/')[1]
#             input_file_path = MODULE_DIR / f'file.{input_file_extension}'
            
#             # Get the bytes content
#             with input_file_path.open('wb') as input_file:

#                 file_content = form.cleaned_data['file'].open()
#                 input_file.write(file_content.read())


#             try:
                
#                 model.predict(source=str(input_file_path), conf=0.25, save=True)
#                 runs_dir = pathlib.Path('runs').resolve()
#                 detect_dir = runs_dir / 'detect'
#                 predict_dir = detect_dir / 'predict'
#                 output_path = predict_dir / 'file.jpeg'
#                 with output_path.open('rb') as f:
#                     img_str = base64.b64encode(f.read()).decode()
                    
#                 # order matters (directories can only be deleted when empty)
#                 for path in [output_path, predict_dir, detect_dir, runs_dir]:
#                     if path.is_dir():
#                         os.rmdir(path)
#                     else:
#                         os.remove(path)

#                 return render(request, 'inferencing/index.html', context= {
#                     'form': FileForm(),
#                     'image_data': img_str
#                 })
                    
#             except FileNotFoundError:
#                 # Handle the case where the image file does not exist
#                 return HttpResponse('Image not found', status=404)
#         else:
#             print('invalid')
        
#     form = FileForm()
#     return render(request, 'inferencing/index.html', context={
#         'form': form
#     })

import base64
import shutil
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from ultralytics import YOLO
import os
import pathlib
from .forms import FileForm
from moviepy.editor import VideoFileClip
import logging
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logger = logging.getLogger(__name__)

MODULE_DIR = pathlib.Path(__file__).resolve().parent
# model = YOLO(f'./yolov8n.pt')
@csrf_exempt
def index(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            input_file = request.FILES['file']
            input_file_extension = input_file.name.split('.')[-1]
            input_file_path = MODULE_DIR / f'file.{input_file_extension}'
            print(MODULE_DIR)
            
            # Save the file
            with input_file_path.open('wb') as f:
                for chunk in input_file.chunks():
                    f.write(chunk)

            # Get the model weights file
            model_weights = request.FILES['model_weights']
            # Save the model weights file to disk
            with open(MODULE_DIR / 'model_weights.pt', 'wb') as model_file:
                model_file.write(model_weights.read())

            base_dir = r'/home/admin1/shared/SEU/inferencing/alam-backend-beta/runs/detect/predict'

            if os.path.exists(base_dir):
                shutil.rmtree(base_dir)
            

            try:
                # Load the YOLO model with the provided weights
                model = YOLO(str(MODULE_DIR / 'model_weights.pt'))
                # Perform inference
                if input_file_extension in ['mp4', 'avi', 'mov']:
                    model.predict(source=str(input_file_path), conf=0.25, save=True)
                    video_path = str(input_file_path.parent / 'output.mp4')
                    return render(request, 'inferencing/index.html', context={'video_path': video_path})
                else:
                    model.predict(source=str(input_file_path), conf=0.25, save=True)
                    predict_dir = MODULE_DIR.parent.parent / 'alam-backend-beta' / 'runs' / 'detect' / 'predict' # palitan mo na lang kun anung dir nag save iyong prediction mo
                    output_path = predict_dir / f'file.{input_file_extension}'
                    print('predict_dir', predict_dir)
                    with output_path.open('rb') as f:
                        img_str = base64.b64encode(f.read()).decode()
                        
                    # order matters (directories can only be deleted when empty)
                    for path in [output_path, predict_dir]:
                        if path.is_dir():
                            os.rmdir(path)
                        else:
                            os.remove(path)
    
                    return render(request, 'inferencing/index.html', context= {
                        'form': FileForm(),
                        'image_data': img_str
                    })
                    
            except FileNotFoundError:
                return HttpResponse('File not found', status=404)
            finally:
                # Clean up temporary files
                os.remove(input_file_path)
                
        else:
            print('Invalid form')
        
    form = FileForm()
    return render(request, 'inferencing/index.html', context={'form': form})

def serve_video(request, filename):
    base_dir = r'/home/admin1/shared/SEU/inferencing/alam-backend-beta/runs/detect/predict' # palitan mo na lang kun anung dir nag save iyong prediction mo
    avi_path = os.path.join(base_dir, filename)
    mp4_path = os.path.join(base_dir, 'file.mp4')
    print("settings.BASE_DIR", settings.BASE_DIR)
    # Convert AVI to MP4
    if not os.path.exists(mp4_path):
        clip = VideoFileClip(avi_path)
        clip.write_videofile(mp4_path)
        clip.close()
    
    # Construct the full path to the video file
    # video_path = os.path.join(settings.BASE_DIR, 'runs', 'detect', 'predict', filename)
    if os.path.exists(mp4_path):
        # Serve the video file
        with open(mp4_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='video/mp4')
        return response
    else:
        # Return 404 if the file does not exist
        return HttpResponse('File not found', status=404)

    

# from django.shortcuts import render
# from django.http import HttpResponse
# from ultralytics import YOLO
# import os
# import pathlib
# from .forms import FileForm
# import base64

# # Get the directory where this Python file is located
# MODULE_DIR = pathlib.Path(__file__).resolve().parent

# def index(request):
#     if request.method == 'POST':
#         form = FileForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Get the file extension of the uploaded file
#             input_file_extension = request.FILES['file'].content_type.split('/')[1]
#             # Create a path for the uploaded file
#             input_file_path = MODULE_DIR / f'file.{input_file_extension}'
#             # Save the uploaded file to disk
#             with input_file_path.open('wb') as input_file:
#                 file_content = form.cleaned_data['file'].open()
#                 input_file.write(file_content.read())

#             # Get the model weights file
#             model_weights = request.FILES['model_weights']
#             # Save the model weights file to disk
#             with open(MODULE_DIR / 'model_weights.pt', 'wb') as model_file:
#                 model_file.write(model_weights.read())

#             try:
#                 # Load the YOLO model with the provided weights
#                 model = YOLO(str(MODULE_DIR / 'model_weights.pt'))

#                 # Determine if the uploaded file is a video
#                 if input_file_extension == 'video/mp4':
#                     is_video = True
#                     output_path = MODULE_DIR / 'output.mp4'
#                 else:
#                     is_video = False
#                     output_path = MODULE_DIR / 'output.jpg'

#                 # Perform object detection on the uploaded file
#                 model.predict(source=str(input_file_path), conf=0.25, save=True, save_dir=str(MODULE_DIR), save_txt=False)

#                 # Read the output file after object detection
#                 with open(output_path, 'rb') as f:
#                     img_str = base64.b64encode(f.read()).decode()

#                 # Remove the uploaded file
#                 os.remove(input_file_path)

#                 # Determine video type
#                 video_type = 'video/mp4' if is_video else ''

#                 # Render the HTML template with the results
#                 return render(request, 'inferencing/index.html', context={
#                     'form': FileForm(),
#                     'image_data': img_str,
#                     'is_video': is_video,
#                     'video_type': video_type,  # Pass video type to template
#                 })

#             except FileNotFoundError:
#                 # Handle the case where the uploaded file does not exist
#                 return HttpResponse('File not found', status=404)
#         else:
#             print('Form is invalid')

#     # Render the HTML template with the file upload form
#     form = FileForm()
#     return render(request, 'inferencing/index.html', context={'form': form})

