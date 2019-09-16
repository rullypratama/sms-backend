from django.db import models, router
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from app import settings
from healthfacility.models import HealthFacility
from masterdata.models import Province, City, District, SubDistrict
from sms.helpers import send_notification_email
from users.models import User


GENDER_TYPE_MEN = '1'
GENDER_TYPE_WOMEN = '2'
GENDER_TYPES = (
    (GENDER_TYPE_MEN, 'Pria'),
    (GENDER_TYPE_WOMEN, 'Wanita')
)

DISEASE_TYPE_PF = 'pf'
DISEASE_TYPE_PV = 'pv'
DISEASE_TYPE_PM = 'pm'
DISEASE_TYPE_PO = 'po'
DISEASE_TYPES = (
    (DISEASE_TYPE_PF, 'Plasmodium Falciparum'),
    (DISEASE_TYPE_PV, 'Plasmodium Vivax'),
    (DISEASE_TYPE_PM, 'Plasmodium Malariae'),
    (DISEASE_TYPE_PO, 'Plasmodium Ovale')
)

IMPORTED_CASE = 'imp'
INDIGENOUS_CASE = 'ind'
CLASSIFICATION_TYPES = (
    (IMPORTED_CASE, 'Imported Case'),
    (INDIGENOUS_CASE, 'Indigenous Case'),
)

PASSIVE_CASE_DETECTION = 'pcd'
ACTIVE_CASE_DETECTION = 'acd'
CASE_TYPES = (
    (PASSIVE_CASE_DETECTION, 'Passive Case Detection'),
    (ACTIVE_CASE_DETECTION, 'Active Case Detection'),
)

MESSAGE_TYPE_INBOX = 'inbox'
MESSAGE_TYPE_SENTBOX = 'sentbox'
MESSAGE_TYPES = (
    (MESSAGE_TYPE_INBOX, 'Inbox'),
    (MESSAGE_TYPE_SENTBOX, 'Sentbox'),
)


class CaseInformation(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    gender = models.CharField(max_length=15, blank=True, choices=GENDER_TYPES)
    age = models.IntegerField(null=True, blank=True)
    patient_contact = models.CharField(max_length=16, null=True, blank=True)

    disease_type = models.CharField(max_length=15, default=DISEASE_TYPE_PF, choices=DISEASE_TYPES)
    case_report_type = models.CharField(max_length=15, default=PASSIVE_CASE_DETECTION, choices=CASE_TYPES)
    classification_case = models.CharField(max_length=15, blank=True,  choices=CLASSIFICATION_TYPES)

    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=15, decimal_places=9, default=0)
    longitude = models.DecimalField(max_digits=15, decimal_places=9, default=0)

    is_pregnant = models.BooleanField(default=False)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='user',
        blank=True,
        null=True
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.SET_NULL,
        related_name='province_info',
        blank=True,
        null=True
    )

    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        related_name='city_info',
        blank=True,
        null=True
    )

    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        related_name='district_info',
        blank=True,
        null=True
    )

    sub_district = models.ForeignKey(
        SubDistrict,
        on_delete=models.SET_NULL,
        related_name='sub_district_info',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'case_information'

    def get_absolute_url(self):
        return reverse('case_information_details', kwargs={'pk': self.pk})

    def delete(self, using=None, keep_parents=False):
        """
        Override delete, just set is_active = False
        :param using:
        :param keep_parents:
        :return:
        """
        using = using or router.db_for_write(self.__class__, instance=self)
        self.is_active = False
        return self.save(using=using)


class MessageInformation(models.Model):
    case_information = models.ForeignKey(
        CaseInformation,
        on_delete=models.CASCADE,
        related_name='case_information',
        blank=True,
        null=True
    )
    origin_facility = models.ForeignKey(
        HealthFacility,
        on_delete=models.SET_NULL,
        related_name='origin_facility',
        blank=True,
        null=True
    )
    destination_facility = models.ForeignKey(
        HealthFacility,
        on_delete=models.SET_NULL,
        related_name='destination_facility',
        blank=True,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    message_type = models.CharField(max_length=15, default=MESSAGE_TYPE_INBOX, choices=MESSAGE_TYPES)

    def __str__(self):
        return f'{self.message_type}'

    class Meta:
        db_table = 'message_information'
        unique_together = ('case_information', 'origin_facility', 'destination_facility', 'message_type')


# @receiver(post_save, sender=MessageInformation)
# def create_queue_message(sender, instance: MessageInformation, created, **kwargs):
#     if created:
#         notification_message = {
#             'name': instance.case_information.name,
#             'gender': f'{instance.case_information.get_gender_display()}',
#             'age': instance.case_information.age,
#             'patient_contact': instance.case_information.patient_contact,
#             'disease_type': f'{instance.case_information.get_disease_type_display()}',
#             'case_report_type': f'{instance.case_information.get_case_report_type_display()}',
#             'classification_case': f'{instance.case_information.get_classification_case_display()}',
#             'address': instance.case_information.address,
#             'is_pregnant': instance.case_information.is_pregnant,
#             'email': instance.case_information.user.email,
#             'from_facility_code': instance.origin_facility.code,
#             'to_facility_code': instance.destination_facility.code
#         }
#         from kombu import Connection
#         conn_string = f'amqp://{settings.QUEUE_USER}:{settings.QUEUE_PASSWORD}@' \
#                       f'{settings.QUEUE_SERVER}//'
#         with Connection(conn_string) as conn:
#             queue = conn.SimpleQueue(settings.EMAIL_NOTIF_QUEUE_NAME)
#             queue.put(notification_message)


@receiver(post_save, sender=MessageInformation)
def create_message(sender, instance: MessageInformation, created, **kwargs):
    if created:
        case_information = {
            'mi': instance.pk,
            'ci': instance.case_information.pk,
            'name': instance.case_information.name,
            'gender': f'{instance.case_information.get_gender_display()}',
            'age': instance.case_information.age,
            'patient_contact': instance.case_information.patient_contact,
            'disease_type': f'{instance.case_information.get_disease_type_display()}',
            'case_report_type': f'{instance.case_information.get_case_report_type_display()}',
            'classification_case': f'{instance.case_information.get_classification_case_display()}',
            'address': instance.case_information.address,
            'province': instance.case_information.province.name,
            'city': instance.case_information.city.name,
            'district': instance.case_information.district.name,
            'sub_district': instance.case_information.sub_district.name,
            'is_pregnant': instance.case_information.is_pregnant,
        }
        send_notification_email(instance.case_information.user, instance.destination_facility, case_information)