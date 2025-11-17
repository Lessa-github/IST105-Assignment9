from django.db import models

class ApiLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100) # Ex: "Get Token", "List Devices"
    ip_address = models.CharField(max_length=50, blank=True, null=True) # Device IP, if applicable
    result = models.CharField(max_length=10) # "Success" or "Failure"
    details = models.TextField(blank=True, null=True) # For error messages

    def __str__(self):
        return f"{self.timestamp} - {self.action} - {self.result}"

    class Meta:
        # Define the collection name in MongoDB
        db_table = 'api_logs'
