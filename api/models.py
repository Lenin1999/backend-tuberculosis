from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
 
    

class Registro(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    tuberculosis = models.BooleanField(default=False)
    prct_tuberculosis = models.DecimalField(max_digits=10, decimal_places=2) # Se establece decimal_places a 2
    prct_no_tuberculosis = models.DecimalField(max_digits=10, decimal_places=2) # Se establece decimal_places a 2

