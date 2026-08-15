import logging
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate unique ID for this request
        request_id = f"req-{str(uuid.uuid4())[:8]}"
        request.state.request_id = request_id
        
        # Record start time using perf_counter for accurate duration measurement
        start_time = time.perf_counter()
        
        # Let the request pass to the router
        response = await call_next(request)
        
        # Record end time and calculate duration
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        # Log the request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} {response.status_code} {duration:.2f}s"
        )
        
        return response