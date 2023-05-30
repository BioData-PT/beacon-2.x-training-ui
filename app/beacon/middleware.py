# Makes a user logged in by default
# TODO : remove this middleware when the login is implemented on Beacon
class BeaconMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.set_cookie('loggedIn', 'True')
        return response
