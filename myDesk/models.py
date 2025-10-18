from django.db import models
from adminDashboard.models import Profile

class Request(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    request_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='vacation_requests')
    processed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    manager_message = models.TextField(blank=True)

    def __str__(self):
        return self.request_user.user.username

    def serialize(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "processed": self.processed,
            "approved": self.approved,
            "manager_message": self.manager_message,
            }  
