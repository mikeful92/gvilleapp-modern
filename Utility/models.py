from django.db import models


class Electric(models.Model):
    ServiceAddress = models.CharField(max_length=120, db_index=True)
    Month = models.CharField(max_length=20)
    Year = models.CharField(max_length=4)
    KWH_Consumption = models.IntegerField()
    Charge = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "Utility_electric"

    def __str__(self) -> str:
        return f"{self.ServiceAddress} {self.Month} {self.Year}"


class Water(models.Model):
    ServiceAddress = models.CharField(max_length=120, db_index=True)
    Month = models.CharField(max_length=20)
    Year = models.CharField(max_length=4)
    Water_Consumption = models.IntegerField()
    Charge = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "Utility_water"

    def __str__(self) -> str:
        return f"{self.ServiceAddress} {self.Month} {self.Year}"
