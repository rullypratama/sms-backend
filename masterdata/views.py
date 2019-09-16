from django.http import JsonResponse
from rest_framework.views import APIView

from masterdata.models import Province, City, District, SubDistrict


class ProvinceListAPI(APIView):

    def get(self, request):
        """ Gets all province
        """
        if request.GET.get('name'):
            province = Province.objects.filter(name=request.GET.get('name'))
        else:
            province = Province.objects.all()

        resp_json = []
        for c in province:
            resp_json.append({
                'id': c.id,
                'name': c.name,
                'code': c.code
            })

        return JsonResponse(resp_json, safe=False)


class CityListAPI(APIView):

    def get(self, request):
        """ Gets all city
        """

        if request.GET.get('province'):
            city = City.objects.filter(province_id=request.GET.get('province'))
        else:
            city = City.objects.all()

        resp_json = []
        for c in city:
            resp_json.append({
                'id': c.id,
                'name': c.name,
                'code': c.code,
                'province': c.province.name if c.province else ''
            })

        return JsonResponse(resp_json, safe=False)


class DistrictListAPI(APIView):

    def get(self, request):
        """ Gets all district
        """

        if request.GET.get('city'):
            district = District.objects.filter(city_id=request.GET.get('city'))
        else:
            district = District.objects.all()

        resp_json = []
        for c in district:
            resp_json.append({
                'id': c.id,
                'name': c.name,
                'code': c.code,
                'city': c.city.name if c.city else ''
            })

        return JsonResponse(resp_json, safe=False)


class SubDistrictListAPI(APIView):

    def get(self, request):
        """ Gets all sub district
        """

        if request.GET.get('district'):
            sub_district = SubDistrict.objects.filter(district_id=request.GET.get('district'))
        else:
            sub_district = SubDistrict.objects.all()

        resp_json = []
        for c in sub_district:
            resp_json.append({
                'id': c.id,
                'name': c.name,
                'code': c.code,
                'district': c.district.name if c.district else ''
            })

        return JsonResponse(resp_json, safe=False)