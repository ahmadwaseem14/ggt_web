from .models import SiteNumber

def site_number(request):
    number = None
    try:
        number = SiteNumber.objects.first()
    except:
        number = None
    return {'site_number': number.number if number else ''} 