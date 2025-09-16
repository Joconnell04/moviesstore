from django.db import models

class CheckoutFeedback(models.Model):
    name = models.CharField(max_length=80, blank=True)       # optional
    message = models.TextField(max_length=500)                # required
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.name or 'Anonymous'}: {self.message[:40]}..."