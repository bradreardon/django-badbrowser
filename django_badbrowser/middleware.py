import httpagentparser

from django.conf import settings
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from . views import unsupported
from . user_agent_checking import check_user_agent


class BrowserSupportDetection(MiddlewareMixin):
    
    def _user_ignored_warning(self, request):
        """
        :rtype: bool
        :returns: True if the user has opted to ignore the browser warning.
        """

        return request.COOKIES.get("badbrowser_ignore", False)
    
    def process_request(self, request):
        self._clear_cookie = False
        
        if request.path.startswith(settings.MEDIA_URL):
            # no need to test media requests (which sometimes come via 
            # via django during development)
            return None
        
        if "HTTP_USER_AGENT" not in request.META:
            return None
        
        user_agent = request.META["HTTP_USER_AGENT"]
        parsed_user_agent = httpagentparser.detect(user_agent)
        
        # Set the browser information on the request object
        request.browser = parsed_user_agent
        
        if not hasattr(settings, "BADBROWSER_REQUIREMENTS"):
            # no requirements have been setup
            return None
        
        if request.path == reverse("django-badbrowser-ignore"):
            # Allow through any requests for the ignore page
            return None
        
        if check_user_agent(parsed_user_agent, settings.BADBROWSER_REQUIREMENTS):
            # noinspection PyAttributeOutsideInit
            self._clear_cookie = True
            # continue as normal
            return None
        else:
            if self._user_ignored_warning(request):
                return None 
            
            return unsupported(request)
    
    def process_response(self, request, response):
        clear_cookie = getattr(self, "_clear_cookie", False)
        if clear_cookie and self._user_ignored_warning(request):
            # Only attempt to clear the cookie if said cookie is present.
            # Helps to play more nicely with Varnish.
            response.delete_cookie("badbrowser_ignore")
        return response
