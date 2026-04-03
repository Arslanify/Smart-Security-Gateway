from django.db import models
from django.utils import timezone

class Entity(models.Model):
    USER_TYPES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
        ('guard', 'Guard'),
        ('visitor', 'Visitor'),
        ('vehicle', 'Vehicle'), 
    )

    name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=50, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    reference_photo = models.ImageField(upload_to='reference_photos/')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    fingerprint_id = models.TextField(blank=True, null=True) 
    
    # --- Dynamic Info Fields ---
    department = models.CharField(max_length=100, blank=True, null=True)
    session = models.CharField(max_length=50, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    purpose_of_visit = models.TextField(blank=True, null=True)

    # 🚩 GUARDIAN FIELDS 
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)

    # --- Visitor & Vehicle Fields ---
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_details = models.TextField(blank=True, null=True)
    vehicle_category = models.CharField(max_length=50, blank=True, null=True)
    driver_cnic = models.CharField(max_length=20, blank=True, null=True)
    driver_contact = models.CharField(max_length=20, blank=True, null=True)
    owner_type = models.CharField(max_length=50, blank=True, null=True)
    ownership = models.CharField(max_length=50, blank=True, null=True)
    number_plate = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.id_number})"

    @property
    def extra_html(self):
        html = f"<p><strong>Type:</strong> {self.get_user_type_display()}</p>"
        if self.user_type == 'student':
            html += f"<p><strong>Dept:</strong> {self.department or 'N/A'}</p>"
            if self.guardian_name and self.guardian_phone:
                html += f"<p><strong>Guardian:</strong> {self.guardian_name} (📱 {self.guardian_phone})</p>"
        return html


class AttendanceLog(models.Model):
    person = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=timezone.now)
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-entry_time']

    def __str__(self):
        return f"{self.person.name} - {self.date}"

# 🚩 LIVE BUS TRACKING MODEL
class BusLocation(models.Model):
    bus_id = models.CharField(max_length=50, default="UOG-BUS-01")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Live Location - {self.bus_id}"