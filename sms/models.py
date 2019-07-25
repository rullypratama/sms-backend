from django.db import models, router
from django.urls import reverse

from users.models import User


GENDER_TYPE_MEN = '1'
GENDER_TYPE_WOMEN = '2'
GENDER_TYPE_OTHERS = '3'
GENDER_TYPES = (
    (GENDER_TYPE_MEN, 'Men'),
    (GENDER_TYPE_WOMEN, 'Women'),
    (GENDER_TYPE_OTHERS, 'Others')
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


class CaseInformation(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    gender = models.CharField(max_length=15, default=GENDER_TYPE_OTHERS, choices=GENDER_TYPES)
    age = models.IntegerField(null=True, blank=True)
    patient_contact = models.CharField(max_length=16, null=True, blank=True)

    disease_type = models.CharField(max_length=15, default=DISEASE_TYPE_PF, choices=DISEASE_TYPES)
    case_report_type = models.CharField(max_length=15, default=PASSIVE_CASE_DETECTION, choices=CASE_TYPES)
    classification_case = models.CharField(max_length=15, default=IMPORTED_CASE, choices=CLASSIFICATION_TYPES)

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
