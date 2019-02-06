import us
from django.db import models


class Locality(models.Model):
    """
    County equivalents, the atomic unit by which we'll collect data.
    """
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=20)
    wikipedia_url = models.URLField()
    official_url = models.URLField()
    ocd_id = models.CharField(max_length=200, unique=True)
    census_geoid = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.name}, {self.state}"

    @property
    def state_abbreviation(self):
        return us.states.lookup(self.state).abbr

    class Meta:
        verbose_name_plural = "localities"
