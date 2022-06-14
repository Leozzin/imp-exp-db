from django.db import models
from imp_exp_db.settings import MEDIA_ROOT

class Structure(models.Model):
    document = models.FileField(upload_to=MEDIA_ROOT+'structure/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
class Data(models.Model):
    document = models.FileField(upload_to=MEDIA_ROOT+'data/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Zip(models.Model):
    document = models.FileField(upload_to=MEDIA_ROOT+'zip-files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)