from django.contrib.postgres.fields import ArrayField
from django.db import models

class Alumno(models.Model):
    Hombre = 'H'
    Mujer = 'D'
    H_D_CHOICES = [
        (Hombre, 'H'),
        (Mujer, 'D'),
    ]

    SI = 'Si'
    NO = 'No'
    SI_NO_CHOICES = [
        (SI, 'Si'),
        (NO, 'No'),
    ]

    alumno_id = models.AutoField(primary_key=True)
    Sexo = models.CharField(max_length=1, choices=H_D_CHOICES, null=True)
    Edad= models.IntegerField(blank=True, null=True)
    Procedencia = models.CharField(max_length=100, null=True)
    Trabajo = models.CharField(max_length=2, choices=SI_NO_CHOICES, default='No')
    Beca = models.CharField(max_length=2, choices=SI_NO_CHOICES, default='No')
    Convocatoria = models.CharField(max_length=3, blank=True, null=True)
    Preferencia = models.IntegerField(blank=True, null=True)
    Modalidad = models.CharField(max_length=3, blank=True, null=True)
    Especialidad = models.CharField(max_length=100, blank=True, null=True)
    Nota_Bach_Ciclo = models.FloatField(blank=True, null=True) 
    Nota_Prueba = models.FloatField(blank=True, null=True)
    Nota_Especifica = models.FloatField(blank=True, null=True)
    Nota_Admision = models.FloatField(blank=True, null=True)
    Abandono = models.CharField(max_length=2, choices=SI_NO_CHOICES, default='No')
    asignaturas_matriculadas_primer_año = models.IntegerField(blank=True, null=True)
    asignaturas_presentadas_primer_año = models.IntegerField(blank=True, null=True)
    asignaturas_aprobadas_primer_año = models.IntegerField(blank=True, null=True)
    asignaturas_matriculadas_segundo_año = models.IntegerField(blank=True, null=True)
    asignaturas_presentadas_segundo_año = models.IntegerField(blank=True, null=True)
    asignaturas_aprobadas_segundo_año = models.IntegerField(blank=True, null=True)
    media_primer_año = models.FloatField(blank=True, null=True)
    media_segundo_año = models.FloatField(blank=True, null=True)
    asignaturas = ArrayField(models.CharField(max_length=200), null=True, blank=True)
    notas = ArrayField(models.FloatField(), null=True, blank=True)

    class Meta:
        abstract = True

class Grado(Alumno):
    Grado = models.CharField(max_length=150)
    Ingreso = models.CharField(max_length=15)

class Grado_rp30(Alumno):
    Grado = models.CharField(max_length=150)
    Ingreso = models.CharField(max_length=15)
    Aciertos = models.IntegerField(blank=True, null=True)
    Fallos = models.IntegerField(blank=True, null=True)
    Total_prueba = models.IntegerField(blank=True, null=True)
