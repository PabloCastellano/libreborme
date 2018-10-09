from django.db import models as m


class CompanyRobotsTxt(m.Model):
    company = m.OneToOneField("borme.Company", primary_key=True, on_delete=m.PROTECT)
    date_created = m.DateTimeField(auto_now_add=True)
    date_updated = m.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return self.company.get_absolute_url()

    def __str__(self):
        return self.company.slug


class PersonRobotsTxt(m.Model):
    person = m.OneToOneField("borme.Person", primary_key=True, on_delete=m.PROTECT)
    date_created = m.DateTimeField(auto_now_add=True)
    date_updated = m.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return self.person.get_absolute_url()

    def __str__(self):
        return self.person.slug
