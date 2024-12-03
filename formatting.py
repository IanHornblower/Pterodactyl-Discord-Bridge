def get_circle(text):
    match text:
        case 'running':
            return '🟢'
        case 'starting':
            return '🟡'
        case 'stopping':
            return '🟠'
        case 'offline':
            return '🔴'
        case _:
            return f"ERROR: missing case: {text}"
        
def format_uptime(uptime):
    return f"Days: {int(uptime[0])}  Hours: {int(uptime[1])}  Minutes: {int(uptime[2])}"