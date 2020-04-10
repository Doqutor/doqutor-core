import os
from app_lib import *

    
def main(event, context):
    log_event(event)
    
    return send_response(200, "Hello World!")