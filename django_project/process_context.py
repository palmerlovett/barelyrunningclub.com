from django.conf import settings
def public_settings(request):
  return {
    "SETTINGS": { 
    	"SITE_URL": settings.SITE_URL,
      "CO_NAME": settings.CO_NAME
    },
  }