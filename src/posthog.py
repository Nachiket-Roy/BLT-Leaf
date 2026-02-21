"""PostHog integration for Cloudflare Workers using Python"""

import json
from js import fetch, Request, Headers, Response
import traceback

async def capture_event(env, event_name, properties=None, distinct_id="server_side"):
    """Capture an event in PostHog"""
    api_key = getattr(env, "POSTHOG_API_KEY", None)
    host = getattr(env, "POSTHOG_HOST", "https://us.i.posthog.com")
    
    if not api_key or api_key == "YOUR_POSTHOG_API_KEY":
        return
        
    url = f"{host.rstrip('/')}/capture/"
    
    data = {
        "api_key": api_key,
        "event": event_name,
        "properties": {
            "distinct_id": distinct_id,
            **(properties or {})
        }
    }
    
    try:
        headers = Headers.new({
            "Content-Type": "application/json"
        })
        
        request = Request.new(url, {
            "method": "POST",
            "body": json.dumps(data),
            "headers": headers
        })
        
        # Non-blocking fetch (fire and forget as much as possible in Workers)
        # In Cloudflare Workers, we might want to use ctx.waitUntil if we had access to it,
        # but here we'll just await it for simplicity or use the env's context if available.
        await fetch(request)
    except Exception as e:
        # Silently fail to not break the main application flow
        print(f"PostHog capture error: {str(e)}")

async def capture_exception(env, exception, context=None, distinct_id="server_side"):
    """Capture an exception in PostHog"""
    properties = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "stack_trace": traceback.format_exc(),
        "is_exception": True,
        **(context or {})
    }
    
    await capture_event(env, "$exception", properties, distinct_id)
