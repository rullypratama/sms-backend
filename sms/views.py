import json
from http import HTTPStatus

from django.db.models import Q
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from healthfacility.models import HealthFacility
from sms.models import CaseInformation


class CaseInformationListAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Gets all case informations based on user's health facility and subs
        """
        # get current health facility
        current_facility = self.request.user.health_facility
        # get linked health facility
        linked_facility = HealthFacility.objects.filter(linked_facility=current_facility)

        caseinformation = CaseInformation.objects.order_by('-created').filter(Q(user__health_facility=current_facility) |
                                                         Q(user__health_facility__in=linked_facility))

        caseinformation = caseinformation[:100]

        resp_json = []
        for c in caseinformation:
            resp_json.append({
                'id': c.id,
                'name': c.name,
                'patientContact': c.patient_contact,
                'diseaseType': c.get_disease_type_display(),
                'caseReportType': c.get_case_report_type_display(),
                'classificationCase': c.get_classification_case_display(),
                'health_facility': c.user.health_facility.name if c.user.health_facility else '',
                'created': c.created,
                'href': request.build_absolute_uri(
                    reverse('case_information_details', kwargs={'pk': c.id})
                ),
            })

        return JsonResponse(resp_json, safe=False)

    def post(self, request: HttpRequest) -> HttpResponse:
        caseinformation = CaseInformation.objects.create(
            name=json.loads(request.body)['name'],
            gender=json.loads(request.body)['gender'],
            age=json.loads(request.body)['age'],
            is_pregnant=json.loads(request.body)['is_pregnant'],
            patient_contact=json.loads(request.body)['patient_contact'],
            disease_type=json.loads(request.body)['disease_type'],
            case_report_type=json.loads(request.body)['case_report_type'],
            classification_case=json.loads(request.body)['classification_case'],
            address=json.loads(request.body)['address'],
            user=self.request.user
        )
        response = HttpResponse(status=HTTPStatus.CREATED)
        response['Location'] = caseinformation.pk
        return response


class CaseInformationDetailAPI(APIView):

    def get(self, request, pk):
        c = CaseInformation.objects.get(pk=pk)
        return JsonResponse({
            'name': c.name,
            'gender': c.get_gender_display(),
            'age': c.age,
            'address': c.address,
            'isPregnant': c.is_pregnant,
            'patientContact': c.patient_contact,
            'diseaseType': c.get_disease_type_display(),
            'caseReportType': c.get_case_report_type_display(),
            'classificationCase': c.get_classification_case_display(),
            'reporter': f'{c.user.first_name} {c.user.last_name}'
        })

    def put(self, request, pk):
        c = CaseInformation.objects.get(pk=pk)
        c.name = json.loads(request.body)['name']
        c.gender = json.loads(request.body)['gender']
        c.age = json.loads(request.body)['age']
        c.is_pregnant = json.loads(request.body)['is_pregnant']
        c.patient_contact = json.loads(request.body)['patient_contact']
        c.disease_type = json.loads(request.body)['disease_type']
        c.case_report_type = json.loads(request.body)['case_report_type']
        c.classification_case = json.loads(request.body)['classification_case']
        c.address = json.loads(request.body)['address']
        c.save()
        return HttpResponse(status=HTTPStatus.OK)
