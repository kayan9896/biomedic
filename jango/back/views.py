from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
import os
import logging
from logging.handlers import RotatingFileHandler
import time
from .code.controller import Controller  
from .code.config_manager import ConfigManager   
from .code.calibrate import Calibrate
from .code.panel import Panel       

class Filter(logging.Filter):
    def filter(self, record):  
        return "api/states" not in record.getMessage()

logger = None
# Configure logging
def setup_logging():
    global logger
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up the logger
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)  # Set the logging level
    logger.addFilter(Filter())
    
    # Create a file handler
    file_handler = RotatingFileHandler(f'logs/{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))}.log', maxBytes=10000000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    

# Call this function at the start of your script
setup_logging()

controller = None

config = ConfigManager()
calibrate = Calibrate()
panel = Panel(config, logger) if config.get('on_simulation') else None


carm_folder = config.get("carm_folder", "./Calibration")
select = {}

@api_view(['GET'])
def get_carms(request):
    """Endpoint to retrieve C-arm data from JSON file"""
    global panel
    global controller
    global logger

    if panel and panel.jumpped:
        controller = panel.controller
        return Response({'jump': True})
    try:
        carm_data = calibrate.get_carms(carm_folder)
        return Response(carm_data)
    except Exception as e:
        logger.error(f"Error fetching C-arm data: {str(e)}")
        return Response({"error": str(e)}), 500

@api_view(['GET'])
def serve_carm_image(request, filename):
    """Endpoint to serve C-arm images"""
    global select
    global controller
    global logger

    if controller: 
        controller = None
    try:
        select = calibrate.serve_carm_select(carm_folder, filename)
        image_base64 = calibrate.serve_carm_image(carm_folder, filename)
        
        return Response({
            'image': f'data:image/jpeg;base64,{image_base64}',
            'imu_on': select['IMU']['imu_on']
        })
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return Response({"error": str(e)}), 404


@api_view(['GET'])
def check_video_connection(request):
    """Endpoint to simulate checking video connection"""
    global controller
    global select
    global panel
    global logger
    
    if controller is None:
        controller = Controller(config, select, panel, logger)
    
    # Get the connection result
    result = controller.connect_video()
    
    return Response(result)
    
@api_view(['GET'])
def check_tilt_sensor(request):
    global controller
    if controller is None:
        controller = Controller(config)
    return Response(controller.imu_handler.sensor.check_tilt_sensor())

@api_view(['POST'])
def start_processing(request):
    global controller
    if controller is None:
        controller = Controller(config)
    result = controller.start_processing()
    if not result:
        return Response({"error": "Processing is already running"}, status=400)
    templates = controller.load()
    return Response({"message": "Started processing on device", "templates": templates})

@api_view(['GET'])
def get_states(request):
    global controller
    try:
        return Response(controller.get_states())
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
def set_ai_autocollect_modes(request):
    global controller
    if controller is None:
        controller = Controller()
    controller.set_ai_autocollect_modes(request.data)
    return Response({'success': True})

@api_view(['GET'])
def get_image_with_metadata(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    return Response(controller.get_image_with_metadata())

@api_view(['POST'])
def save_landmarks(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    data = request.data
    controller.update_landmarks(
        data.get("leftMetadata"), data.get("rightMetadata"),
        data.get("limgside"), data.get("rimgside"),
        data.get("brightness"), data.get("contrast"),
        data.get("stage")
    )
    return Response({"message": "update landmarks"})

@api_view(['POST'])
def manual_framecap(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    controller.do_capture = request.data.get("cap")
    return Response({"message": "do capture"})

@api_view(['POST'])
def switch_side(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    controller.active_side = request.data.get("label")
    return Response({"message": "click label switch active side"})

@api_view(['POST'])
def edit(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    controller.pause_states = request.data.get("uistates")
    return Response({"message": "pause_states updated"})

@api_view(['POST'])
def next(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    controller.next(request.data.get("uistates"), request.data.get("stage"))
    return Response({"message": "uistates updated"})

@api_view(['POST'])
def restart(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    controller.restart()
    return Response({"message": "uistate restart"})

@api_view(['POST'])
@parser_classes([MultiPartParser])
def save_screen(request, stage):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    image = request.FILES.get("image")
    if not image:
        return Response({"error": "No file part"}, status=400)
    controller.save_screen(stage, image)
    return Response({"message": "screenshot saved successfully"})

@api_view(['GET'])
def get_screen(request, stage):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    return Response(controller.get_screen(stage))

@api_view(['GET'])
def get_stitch(request, stage):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    return Response(controller.get_stitch(stage))

@api_view(['POST'])
def patient(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    controller.patient(request.data)
    return Response({"message": "patient saved successfully"})

@api_view(['GET'])
def pdf(request):
    global controller
    if controller is None:
        return Response({"error": "Controller not initialized"}, status=404)
    controller.savepdf()
    return Response({"message": "pdf saved successfully"})