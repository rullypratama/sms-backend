import json
from django.core.exceptions import ValidationError
from django.forms import MultipleChoiceField
from json import JSONDecodeError

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Model
from django.db.models.fields import SlugField
from django.utils.text import slugify


def generate_slug(model_class: Model, base_text: str, tries=0) -> str:
    """ Create a unique slug for the given model_class.

    .. warning::

        Makes the slightly naive assumption that your slug field will be called 'slug'

    :param model_class: A django model class (NOT the instance)
    :param base_text: Some text to use as a base for the slug, such as the 'name'
    :param tries: Previous attempts to geenrate the slug
    :return: A unique slug for an item from the database.
    """
    candidate_slug = f'{slugify(base_text)}-{tries}' if tries else slugify(base_text)
    if model_class.objects.filter(slug=candidate_slug).exists():
        return generate_slug(model_class, base_text, tries+1)
    return candidate_slug


# TODO: we could just combine mult+mono lang slug into a single class...
# then just detects whether 'from_field' is a str or a dict
# and if dict, use settings.LANGUAGE_CODE for the key

class MonoLangSlugField(SlugField):
    """ Field that automatically generates a slug from a CharField before saving.
    """
    def __init__(self, from_field='name', *args, **kwargs):
        if not 'unique' in kwargs:
            kwargs['unique'] = True
        if not 'max_length' in kwargs:
            kwargs['max_length'] = 150
        super(MonoLangSlugField, self).__init__(*args, **kwargs)
        self.from_field = from_field

    def pre_save(self, model_instance: any, add: bool):
        if not getattr(model_instance, self.attname):
            source = getattr(model_instance, self.from_field)
            setattr(
                model_instance,
                self.attname,
                generate_slug(model_instance.__class__, source)
            )
        return super(MonoLangSlugField, self).pre_save(model_instance, add)


class MultiLangSlugField(MonoLangSlugField):

    def __init__(self, from_lang=settings.LANGUAGE_CODE, *args, **kwargs):
        self.from_lang = from_lang
        super(MultiLangSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance: any, add: bool):
        if not getattr(model_instance, self.attname):
            source = getattr(model_instance, self.from_field).get(self.from_lang)
            setattr(
                model_instance,
                self.attname,
                generate_slug(model_instance.__class__, source)
            )
        return super(MonoLangSlugField, self).pre_save(model_instance, add)


class MultiLangCharField(JSONField):
    """ A JSON-field that requires that **all** languages enabled for the site are accounted for.

    Example:

    .. code-block:: python

        # in settings.py
        LANGUAGES = ['en', 'id', ]

        # then when we're using our model with this json field..

        class SomeModel(models.Model):
            multilang_field = MultiLangCharField()

        # valid
        SomeModel(multilang_field={'en': 'Duck vehicle', 'id': 'Motor bebek'})

        # throws value error
        SomeModel(multilang_field={'fr': 'Berlkjwer'})

    """
    def pre_save(self, model_instance: any, add: bool) -> dict:
        val = getattr(model_instance, self.attname, None)
        if val:
            allowed_languages = sorted([t[0] for t in settings.LANGUAGES])
            if isinstance(val, str):
                # val in string must be converted to dict using json loads
                try:
                    val = json.loads(val)
                except JSONDecodeError as ex:
                    raise ValueError("Value is not a valid JSON for multi languages field.")
            selected_languages = sorted([k for k in val])

            if not allowed_languages == selected_languages:
                raise ValueError(f"Language {selected_languages} is not allowed")

        return super(MultiLangCharField, self).pre_save(model_instance, add)


class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimestampedModel):
    """ Common model for most of our standard use-cases.  Includes a name, slug, and is_active field.
    """
    name = models.CharField(max_length=70)
    slug = MonoLangSlugField()

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class MultiLangBaseModel(TimestampedModel):

    name = MultiLangCharField()
    slug = MultiLangSlugField()

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[settings.LANGUAGE_CODE]


class TypedMultipleChoiceField(MultipleChoiceField):
    def __init__(self, *, coerce=lambda val: val, **kwargs):
        self.coerce = coerce
        self.empty_value = kwargs.pop('empty_value', [])
        super().__init__(**kwargs)

    def _coerce(self, value):
        """
        Validate that the values are in self.choices and can be coerced to the
        right type.
        """
        if value == self.empty_value or value in self.empty_values:
            return self.empty_value
        new_value = []
        for choice in value:
            try:
                new_value.append(self.coerce(choice))
            except (ValueError, TypeError, ValidationError):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': choice},
                )
        return new_value

    def clean(self, value):
        value = super().clean(value)
        return self._coerce(value)

    def validate(self, value):
        if value != self.empty_value:
            super().validate(value)
        elif self.required:
            raise ValidationError(self.error_messages['required'], code='required')

