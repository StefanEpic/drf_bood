import requests
from rest_framework.response import Response
from rest_framework.views import APIView


class UserActivationView(APIView):
    """
    Forwarding a parsed GET request to a POST endpoint
    """

    def get(self, request, uid, token) -> Response:
        protocol = "https://" if request.is_secure() else "http://"
        web_url = protocol + request.get_host()
        post_url = web_url + "/api/v1/users/activation/"
        post_data = {"uid": uid, "token": token}
        result = requests.post(post_url, data=post_data)
        content = result.text
        return Response(content)
