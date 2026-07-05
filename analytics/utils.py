def get_device_info(request):
    """Get device information from the request."""
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return user_agent


def get_ip_info(request):
    """Get IP address information from the request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
