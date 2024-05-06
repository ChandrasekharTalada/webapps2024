from .models import Notif

def notif_count(request):
    if request.user.is_authenticated:
        notif_count = Notif.objects.filter(
            user=request.user,viewed=False
        ).count()
        notifications = Notif.objects.filter(user=request.user)[:3]
    else:
        notif_count = 0
        notifications = None
    return {"notif_count": notif_count, "notif_user": notifications}
