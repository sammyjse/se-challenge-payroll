import pandas as pd
from django.db.models import Count, Sum, When, Case, Value, FloatField, IntegerField

from django.http import JsonResponse
from rest_framework.views import APIView
from .models import Reports, Timekeeping
import datetime
from django.db.models.functions import TruncMonth, TruncYear

"""

UploadCSVView

    - Goal of this API is to upload csv's of the employee reported times to the Timekeeping table.
    - Have only setup the post call which will require the name of the csv file to add
    - {"filename" : "time-report-42.csv"}
"""


class UploadCSVView(APIView):

    # POST call
    def post(self, request):

        # Changing the date format
        display_format = '%d/%m/%Y'
        db_format = '%Y-%m-%d'

        # retrieving the filename passed through the API. Assuming the file is of valid type.
        file_name = request.data['filename']

        # Extracting the id so it can be checked if there is a duplicate in the Reports table
        report_id = int(file_name.split('.')[0].split('-')[2])

        # Checking the report id
        if Reports.objects.filter(report=report_id).count() == 1:
            return JsonResponse("Report ID already exists.", status=200, safe=False)

        # If the report is new it will be created in the db
        Reports.objects.create(report=report_id)

        # Reading through the csv using pandas
        records = pd.read_csv("app/" + file_name, encoding='utf8')

        # Adding each entry
        for idx, row in records.iterrows():
            Timekeeping.objects.create(date=datetime.datetime.strptime(row["date"], display_format).strftime(db_format),
                                       hours=row["hours worked"],
                                       employee_id=row["employee id"],
                                       job_group=row["job group"])

        return JsonResponse("Successfully added file " + file_name + "to the database.", status=200, safe=False)


"""

TimekeepingView

    - Goal of this view is to output a report JSON of all recorded hours, based of two periods:
        - 0 - 15 of the month (period1)
        - 16 - 31 of the month (period2)

"""


class TimekeepingView(APIView):
    # array to keep track of the reports
    employeeReports = []

    # This is a helper method to format the records
    def formatRecords(self, qs):

        """
        :param qs:       {
                "employeeId": 1,
                "payPeriod": {
                    "startDate": "2016-11-01",
                    "endDate": "2016-11-15"
                },
                "amountPaid": "$150.0"
            }

        The qs will include multiple employee reports based off period

        :return: Format and then add each report to the array (employeeReports)
        """

        for record in qs:
            formatted_record = {}
            year = str(record["year"]).split("-")[0]
            month = str(record["month"]).split("-")[1]
            formatted_record["employeeId"] = record["employee_id"]

            # formatting the start and end date because I only grouped by year, and month

            if record["period"] == 1:
                payPeriod = {"startDate": year + '-' + month + '-' + '01',
                             "endDate": year + '-' + month + '-' + '15'}

            else:
                payPeriod = {"startDate": year + '-' + month + '-' + '16',
                             "endDate": year + '-' + month + '-' + '31'}

            # formatting payPeriod and amount
            formatted_record["payPeriod"] = payPeriod
            formatted_record["amountPaid"] = '$' + str(record["amount"])

            # adding the specific report to employeeReports
            self.employeeReports.append(formatted_record)

    """
    GET call to group by all employee ids, based off period (year, month). Then output the employeeReport.
    """
    def get(self, request, format=None):


        """
        First period (0 - 15)

        I group by year, month, and employee_id (count). Then filter be day/period.
        """
        period1 = Timekeeping.objects \
            .annotate(year=TruncYear('date'), month=TruncMonth('date')) \
            .values('year', 'month').annotate(amount=Case(
            When(job_group="A", then=20.00 * Sum("hours")),
            When(job_group="B", then=30.00 * Sum("hours")),
            default=20.00 * Sum("hours"),
            output_field=FloatField())
        ) \
            .annotate(count=Count('employee_id'), period=Value(1, output_field=IntegerField())) \
            .filter(date__day__range=["01", "15"]) \
            .values('year', 'month', 'employee_id', 'count', 'amount', 'period')


        """
        Second period (16 - 31)
        
        Same idea as period 1, but filter by different days. 
        
        """
        period2 = Timekeeping.objects \
            .annotate(year=TruncYear('date'), month=TruncMonth('date')) \
            .values('year', 'month').annotate(amount=Case(
            When(job_group="A", then=20.00 * Sum("hours")),
            When(job_group="B", then=30.00 * Sum("hours")),
            default=20.00 * Sum("hours"),
            output_field=FloatField())
        ) \
            .annotate(count=Count('employee_id'), period=Value(2, output_field=IntegerField())) \
            .filter(date__day__range=["16", "31"]) \
            .values('year', 'month', 'employee_id', 'count', 'amount', 'period')

        # combining the two period (query sets) so that order is kept
        total = period1.union(period2)

        # calling formatRecords to format the qs for output
        self.formatRecords(total)

        return JsonResponse({"payrollReport": {"employeeReports": self.employeeReports}}, status=200, safe=False)
