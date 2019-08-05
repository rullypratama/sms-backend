from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from healthfacility.models import HealthFacility


class HealthFacilityListAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Gets all health facility exists.
        """
        healthfacility = HealthFacility.objects.all()

        healthfacility = healthfacility[:100]

        resp_json = []
        for h in healthfacility:
            resp_json.append({
                'name': h.name,
                'code': h.code,
                'level': h.facility_level,
                'address': h.address,
                'linked': h.linked_facility.name if h.linked_facility else ''
                # 'href': request.build_absolute_uri(
                #     reverse('shipping_details', kwargs={'warehouse': warehouse, 'pk': s.id})
                # ),
            })

        return JsonResponse(resp_json, safe=False)