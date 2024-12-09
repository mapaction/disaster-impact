ENRICHED_STANDARD_COLUMNS = [
    'Event_ID', 
    'Source_Event_IDs',  # New: To store all original source IDs
    'Event_Name', 
    'Event_Type', 
    'Country', 
    'Country_Code',  # ISO3 code
    'Location',      # Array of locations (admin areas)
    'Latitude',      # Array if multiple coords
    'Longitude',     # Array if multiple coords
    'Date',          # ISO 8601 date
    'Year', 
    'Month', 
    'Day', 
    'Time', 
    'Severity',
    'Population_Affected',
    'Fatalities',       # New field
    'People_Displaced', # New field
    'Financial_Loss',   # New field
    'Alert_Level', 
    'Source', 
    'Comments', 
    'External_Links'    # New field for external references
]

GLIDE_MAPPING = {
    'Event_ID': False,  # Will be assigned after internal consolidation.
    'Source_Event_IDs': 'GLIDE_number',
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
    'Severity': False,
    'Population_Affected': False,
    'Fatalities': False,
    'People_Displaced': False,
    'Financial_Loss': False,
    'Alert_Level': False,
    'Source': 'Source',
    'Comments': 'Comments',
    'External_Links': False
}