from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
import traceback
import logging


class ErrorHandlerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if not settings.DEBUG:
            if exception:
                # Format your message here
                message = "START ERROR \nOccured at: {time}\n**{url}**\n\n{error}\n\n````{tb}````".format(
                    time=datetime.now(),
                    url=request.build_absolute_uri(),
                    error=repr(exception),
                    tb=traceback.format_exc()
                )
                log_error(message)
                
            return HttpResponse("Error processing the request. (500)", status=500)
    
def log_error(error_message):
    logging.basicConfig(filename="logs/server_errors.log",
                    format='%(message)s',
                    filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.error(error_message + "\nEND ERROR\n")