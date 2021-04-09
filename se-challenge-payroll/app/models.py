from django.db import models


"""

Model Name : Timekeeping

Fields:
    - Entry ID (automatically generated through django)
    - Date
    - Hours Worked
    - Employee ID
    - Job Group

Description: 
    - The goal of this model is to keep track of all employee hours.
    - (id, date, hours worked, employee id, job group)

"""


class Timekeeping(models.Model):
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2,help_text="Hours worked for the day.")
    employee_id = models.IntegerField()
    job_group = models.CharField(max_length=1, help_text="Job group employee is assigned to.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "timekeeping"
        unique_together = ("employee_id", "date")

    def __str__(self):
        return '(' + self.date + ',' + self.hours + ',' + self.employee_id + ',' + self.job_group + ')'


"""
Model Name : Reports

Fields:
    - Report ID
        
Description: 
    - The goal of this model is to keep track of all uploaded reports.
    - (report id)
"""


class Reports(models.Model):

    report = models.IntegerField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reports"

    def __str__(self):
        return "Report " + self.report + "created at " + self.created_at + "."
