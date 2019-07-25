from django.db import models, router
from django.urls import reverse


HEALTHFACILITY_TYPE_DISTRICT = '3'
HEALTHFACILITY_TYPE_HEALTH_CENTER = '2'
HEALTHFACILITY_TYPE_CLINIC = '1'
HEALTHFACILITY_TYPES = (
    (HEALTHFACILITY_TYPE_DISTRICT, 'District Health'),
    (HEALTHFACILITY_TYPE_HEALTH_CENTER, 'Health Center'),
    (HEALTHFACILITY_TYPE_CLINIC, 'Clinic/Health Center Satelite')
)

class HealthFacility(models.Model):
    name = models.CharField(max_length=50)
    # slug = MonoLangSlugField(from_field='name')
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=15)

    linked_facility = models.ForeignKey('HealthFacility', on_delete=models.SET_NULL, null=True, blank=True)
    facility_level = models.CharField(max_length=15, default=HEALTHFACILITY_TYPE_CLINIC, choices=HEALTHFACILITY_TYPES)

    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=15, decimal_places=9, default=0)
    longitude = models.DecimalField(max_digits=15, decimal_places=9, default=0)

    def __str__(self):
        return f'{self.name} - {self.code}'

    class Meta:
        db_table = 'health_facility'

    # def get_absolute_url(self):
    #     return reverse('product:warehouse:details', kwargs={'slug': self.slug})

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