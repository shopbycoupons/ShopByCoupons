from django.db import models



class Email(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    date = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:

        db_table = 'email'

    def __str__(self):
        return self.email

class letsdoc_users(models.Model):
    email = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    date = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)

    class Meta:

        db_table = 'letsdoc_user'

    def __str__(self):
        return self.email


class campaign(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    tag1 = models.CharField(max_length=100, blank=True, null=True)
    tag2 = models.CharField(max_length=100, blank=True, null=True)
    sent = models.IntegerField(blank=True, null=True)
    unsubscribes = models.IntegerField(blank=True, null=True)
    complaints = models.IntegerField(blank=True, null=True)
    bounces = models.IntegerField(blank=True, null=True)
    opens = models.IntegerField(blank=True, null=True)
    clicks = models.IntegerField(blank=True, null=True)

    class Meta:

        db_table = 'emails_campaign'


    def __str__(self):
        return self.tag1

class ecamp(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    eid = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    date = models.CharField(max_length=50, blank=True, null=True)

    class Meta:

        db_table = 'ecamp'

    def __str__(self):
        return self.eid

class edump(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    dump = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:

        db_table = 'edump'

    def __str__(self):
        return self.id
