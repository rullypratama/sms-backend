import json
from http import HTTPStatus

from django.db.models import Q
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from healthfacility.models import HealthFacility
from sms.helpers import send_notification_email
from sms.models import CaseInformation, MessageInformation, MESSAGE_TYPE_INBOX, MESSAGE_TYPE_SENTBOX


class CaseInformationListAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Gets all case informations based on user's health facility
        """
        # get current health facility
        current_facility = self.request.user.health_facility

        messageinformation = MessageInformation.objects.filter(Q(origin_facility=current_facility) |
                                                               Q(destination_facility=current_facility)
                                                               ).order_by('-created')
        messageinformation = messageinformation[:100]

        resp_json = []
        for c in messageinformation:
            resp_json.append({
                'id': c.case_information.id,
                'name': c.case_information.name,
                'patientContact': c.case_information.patient_contact,
                'diseaseType': c.case_information.get_disease_type_display(),
                'caseReportType': c.case_information.get_case_report_type_display(),
                'classificationCase': c.case_information.get_classification_case_display(),
                'healthFacilityFrom': c.origin_facility.name,
                'healthFacilityTo': c.destination_facility.name,
                'created': c.case_information.created,
                'href': request.build_absolute_uri(
                    reverse('case_information_details', kwargs={'pk': c.case_information.id})
                ),
            })

        return JsonResponse(resp_json, safe=False)

    def post(self, request: HttpRequest) -> HttpResponse:
        ci = CaseInformation.objects.create(
            name=json.loads(request.body)['name'],
            gender=json.loads(request.body)['gender'],
            age=json.loads(request.body)['age'],
            is_pregnant=json.loads(request.body)['is_pregnant'],
            patient_contact=json.loads(request.body)['patient_contact'],
            disease_type=json.loads(request.body)['disease_type'],
            case_report_type=json.loads(request.body)['case_report_type'],
            classification_case=json.loads(request.body)['classification_case'],
            address=json.loads(request.body)['address'],
            province_id=json.loads(request.body)['province'],
            city_id=json.loads(request.body)['city'],
            district_id=json.loads(request.body)['district'],
            sub_district_id=json.loads(request.body)['sub_district'],
            user=self.request.user
        )
        MessageInformation.objects.create(
            case_information=ci,
            origin_facility=self.request.user.health_facility if self.request.user.health_facility else '',
            destination_facility=self.request.user.health_facility.linked_facility if self.request.user.health_facility else '',
            message_type=MESSAGE_TYPE_INBOX
        )

        patient_sub_district_id = json.loads(request.body)['sub_district']
        origin_sub_district_id = self.request.user.health_facility.sub_district_id if self.request.user.health_facility else ''

        if patient_sub_district_id != origin_sub_district_id:
            check_other_hf = HealthFacility.objects.filter(sub_district_id=patient_sub_district_id)
            for other_mi in check_other_hf:
                MessageInformation.objects.create(
                    case_information=ci,
                    origin_facility=self.request.user.health_facility if self.request.user.health_facility else '',
                    destination_facility=other_mi,
                    message_type=MESSAGE_TYPE_INBOX
                )


        # case_information = {
        #     'mi': mi.pk,
        #     'ci': ci.pk,
        #     'name': ci.name,
        #     'gender': f'{ci.get_gender_display()}',
        #     'age': ci.age,
        #     'patient_contact': ci.patient_contact,
        #     'disease_type': f'{ci.get_disease_type_display()}',
        #     'case_report_type': f'{ci.get_case_report_type_display()}',
        #     'classification_case': f'{ci.get_classification_case_display()}',
        #     'address': ci.address,
        #     'is_pregnant': ci.is_pregnant,
        # }
        # send_notification_email(self.request.user, self.request.user, case_information)

        response = HttpResponse(status=HTTPStatus.CREATED)
        response['Location'] = ci.pk
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

    def post(self, request, pk):
        ci = CaseInformation.objects.get(pk=pk)
        mi = MessageInformation.objects.create(
            case_information=ci,
            origin_facility=self.request.user.health_facility if self.request.user.health_facility else '',
            destination_facility=self.request.user.health_facility.linked_facility if self.request.user.health_facility else '',
            message_type=MESSAGE_TYPE_SENTBOX
        )
        case_information = {
            'mi': mi.pk,
            'ci': ci.pk,
            'name': ci.name,
            'gender': f'{ci.get_gender_display()}',
            'age': ci.age,
            'patient_contact': ci.patient_contact,
            'disease_type': f'{ci.get_disease_type_display()}',
            'case_report_type': f'{ci.get_case_report_type_display()}',
            'classification_case': f'{ci.get_classification_case_display()}',
            'address': ci.address,
            'is_pregnant': ci.is_pregnant,
        }
        send_notification_email(self.request.user, self.request.user, case_information)
        return HttpResponse(status=HTTPStatus.OK)

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


class CaseInformationSentListAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Gets sent case informations based on user's health facility
        """
        # get current health facility
        current_facility = self.request.user.health_facility

        messageinformation = MessageInformation.objects.filter(origin_facility=current_facility).order_by('-created')

        messageinformation = messageinformation[:100]

        resp_json = []
        for c in messageinformation:
            resp_json.append({
                'id': c.case_information.id,
                'name': c.case_information.name,
                'patientContact': c.case_information.patient_contact,
                'diseaseType': c.case_information.get_disease_type_display(),
                'caseReportType': c.case_information.get_case_report_type_display(),
                'classificationCase': c.case_information.get_classification_case_display(),
                'healthFacilityFrom': c.origin_facility.name,
                'healthFacilityTo': c.destination_facility.name,
                'created': c.case_information.created,
                'href': request.build_absolute_uri(
                    reverse('case_information_details', kwargs={'pk': c.case_information.id})
                ),
            })

        return JsonResponse(resp_json, safe=False)


class CaseInformationReceivedListAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Gets received case informations based on user's health facility
        """
        # get current health facility
        current_facility = self.request.user.health_facility

        messageinformation = MessageInformation.objects.filter(destination_facility=current_facility).order_by( '-created')

        messageinformation = messageinformation[:100]

        resp_json = []
        for c in messageinformation:
            resp_json.append({
                'id': c.case_information.id,
                'name': c.case_information.name,
                'patientContact': c.case_information.patient_contact,
                'diseaseType': c.case_information.get_disease_type_display(),
                'caseReportType': c.case_information.get_case_report_type_display(),
                'classificationCase': c.case_information.get_classification_case_display(),
                'healthFacilityFrom': c.origin_facility.name,
                'healthFacilityTo': c.destination_facility.name,
                'created': c.case_information.created,
                'href': request.build_absolute_uri(
                    reverse('case_information_details', kwargs={'pk': c.case_information.id})
                ),
            })

        return JsonResponse(resp_json, safe=False)
