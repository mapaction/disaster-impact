
standard_columns = [
    'Event_ID', 'Event_Name', 'Event_Type', 'Country', 'Country_Code', 'Location',
    'Latitude', 'Longitude', 'Date', 'Year', 'Month', 'Day', 'Time', 'Severity',
    'Population_Affected', 'Alert_Level', 'Source', 'Comments'
]

glide_mapping = {
    'Event_ID': 'GLIDE_number',
    'Event_Name': 'Event',
    'Event_Type': 'Event_Code',
    'Country': 'Country',
    'Country_Code': 'Country_Code',
    'Location': 'Location',
    'Latitude': 'Latitude',
    'Longitude': 'Longitude',
    'Date': 'Date_',
    'Year': 'Year',
    'Month': 'Month',
    'Day': 'Day',
    'Time': 'Time',
    'Severity': 'Magnitude',
    'Population_Affected': False,
    'Alert_Level': False,
    'Source': 'Source',
    'Comments': 'Comments'
}

gdacs_mapping = {
    'Event_ID': 'event_id',
    'Event_Name': 'event_name',
    'Event_Type': 'event_type',
    'Country': 'countries',
    'Country_Code': False,
    'Location': False,
    'Latitude': False,
    'Longitude': False,
    'Date': 'from_date',
    'Year': 'year',
    'Month': False,
    'Day': False,
    'Time': False,
    'Severity': 'severity',
    'Day': False,
    'Time': False,
    'Severity': 'severity',
    'Population_Affected': 'population',
    'Alert_Level': 'alert_level',
    'Source': False,
    'Comments': False
}


adam_mapping = {
    'Event_ID': 'uid',
    'Event_Name': False,
    'Event_Type': False,
    'Country': False,
    'Country_Code': False,
    'Location': False,
    'Latitude': 'y',
    'Longitude': 'x',
    'Date': 'created_at',
    'Year': False,
    'Month': False,
    'Day': False,
    'Time': False,
    'Severity': False,
    'Population_Affected': 'population',
    'Alert_Level': False,
    'Source': False,
    'Comments': False
}


cerf_mapping = {
    'Event_ID': 'allocation_code',
    'Event_Name': False,
    'Event_Type': 'emergency_type',
    'Country': 'country',
    'Country_Code': False,
    'Location': False,
    'Latitude': False,
    'Longitude': False,
    'Date': 'approval_date',
    'Year': False,
    'Month': False,
    'Day': False,
    'Time': False,
    'Severity': False,
    'Population_Affected': 'number_of_people_targeted',
    'Alert_Level': False,
    'Source': False,
    'Comments': 'project_description'
}

disaster_charter_mapping = {
    'Event_ID': 'Activation ID',
    'Event_Name': 'Disaster',
    'Event_Type': 'Type of Event',
    'Country': 'Location of Event',
    'Country_Code': False,
    'Location': 'Location of Event',
    'Latitude': False,
    'Longitude': False,
    'Date': 'Date of Activation',
    'Year': 'Year',
    'Month': 'Month',
    'Day': False,
    'Time': 'Time of Activation',
    'Severity': False,
    'Population_Affected': False,
    'Alert_Level': False,
    'Source': False,
    'Comments': False
}
