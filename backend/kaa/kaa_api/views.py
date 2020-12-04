from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from kaa_api.tra import main


@api_view(('GET',))
def valuate(request):
    # https://www.beforward.jp/toyota/coaster/bh621851/id/2153824/ working
    url = request.query_params['url']
    result = main(url)
    return Response(result)
