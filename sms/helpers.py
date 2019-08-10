from smtplib import SMTPException

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from users.models import User


def send_notification_email(user: User, reporter: User, case_information):
    """ Send Email Notification

    :param user: User object
    :return: Email send status
    """

    content = {
        'user': {
            'name': f'{user.first_name} {user.last_name}'
        },
        'reporter': {
            'name': f'{reporter.first_name} {reporter.last_name}',
            'health_facility': reporter.health_facility.name
        },
        'case_information': {
            'name': case_information.get('name'),
            'gender': case_information.get('gender'),
            'age': case_information.get('age'),
            'patient_contact': case_information.get('patient_contact'),
            'disease_type': case_information.get('disease_type'),
            'case_report_type': case_information.get('case_report_type'),
            'classification_case': case_information.get('classification_case'),
            'address': case_information.get('address'),
            'is_pregnant': case_information.get('is_pregnant')
        }
    }

    try:
        # log.info(f"Sending Email notification: {user}")
        email = EmailMultiAlternatives(
            subject=f'Case Information from {reporter.health_facility.name} #MI{case_information.get("mi")} #CI{case_information.get("ci")}',
            body=render_to_string('case_information/email_notification/email_notification.txt', content),
            from_email='no-reply@mail.garuda.com',
            # to=[user.email, ]
            to=['azharieazharou@gmail.com', 'rully.annihilator@gmail.com' ]
        )

        email.attach_alternative(
            render_to_string(
                'case_information/email_notification/email_notification.html',
                content),
            'text/html')

        return email.send()
    except SMTPException as e:
        # log.error(f'Send Notification email failed : {str(e)}')
        print(e)
        return 0