# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accidentes(models.Model):
    id_accidentes = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    id_tip_acci = models.ForeignKey('TipoAccidente', models.DO_NOTHING, db_column='id_tip_acci', blank=True, null=True)
    direccion = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accidentes'


class Contactos(models.Model):
    id_contactos = models.AutoField(primary_key=True)
    nro_emer = models.CharField(max_length=10, blank=True, null=True)
    nombre = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contactos'


class DetalleTuto(models.Model):
    id_datalle = models.AutoField(primary_key=True)
    id_tuto = models.ForeignKey('Tutoriales', models.DO_NOTHING, db_column='id_tuto', blank=True, null=True)
    imagenes = models.CharField(max_length=1, blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detalle_tuto'


class ModoEmergencia(models.Model):
    id_mod_emer = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    direccion = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modo_emergencia'


class TipoAccidente(models.Model):
    id_tipo_acc = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    direccion = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_accidente'


class Tutoriales(models.Model):
    id_tuto = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=15, blank=True, null=True)
    link = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutoriales'


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=15, blank=True, null=True)
    ubicacion = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'
