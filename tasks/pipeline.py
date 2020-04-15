from .models import ShowArchived
from django.contrib.auth.models import User


def archived_entry(backend, user, response, *args, **kwargs):
    ShowArchived.objects.get_or_create(user=User.objects.filter(email=response['email']).values('id')[0]['id'])
