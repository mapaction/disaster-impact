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
    'Event_ID': False,  # Will be assigned after internal consolidation, concatinated strings that come up from Source_Event_IDs. 
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

GDACS_MAPPING = {
    'Event_ID': False,              # Will be assigned after internal consolidation
    'Source_Event_IDs': 'event_id', # Convert numeric event_id to string and store in array
    'Event_Name': 'event_name',
    'Event_Type': 'event_type',
    'Country': 'countries',         # Provided by GDACS; can remain as string or null if NaN can be derived by Event_Name
    'Country_Code': 'iso3',          # Provided by GDACS, may derive from Country if its NaN
    'Location': 'countries',              # Provided by GDACS, if its NaN should derive from Country 
    'Latitude': 'coordinates',      # Not provided by GDACS, can derive from coordinates[1]
    'Longitude': 'coordinates',     # Not provided by GDACS, can derive from coordinates[0]
    'Date': 'from_date',            # ISO 8601 format available; can derive Month, Day, Time
    'Year': 'year',
    'Month': False,                 # Derive from Date
    'Day': False,                   # Derive from Date
    'Time': False,                  # Derive from Date
    'Severity': 'severity',         # Numeric severity, convert to string or leave as is
    'Population_Affected': 'population', # Float, convert to int if possible
    'Fatalities': False,            # Not provided by GDACS
    'People_Displaced': False,      # Not provided by GDACS
    'Financial_Loss': False,        # Not provided by GDACS
    'Alert_Level': 'alert_level',
    'Source': False,                # Could set to ["GDACS"] manually if desired
    'Comments': False,              # Not provided by GDACS
    'External_Links': False         # Not provided by GDACS
}

DISASTER_CHARTER_MAPPING = {
    'Event_ID': False,                      # Will be assigned after internal consolidation
    'Source_Event_IDs': 'Activation ID',    # Convert numeric ID to string and store in array
    'Event_Name': 'Disaster',
    'Event_Type': 'Type of Event',
    'Country': 'Location of Event',         # Use as country if specific; could also be parsed for subnational
    'Country_Code': False,                  # Not provided by Disaster Charter
    'Location': 'Location of Event',        # Use as an array if multiple locations
    'Latitude': False,                      # Not provided by Disaster Charter
    'Longitude': False,                     # Not provided by Disaster Charter
    'Date': 'Date of Activation',           # ISO 8601 date
    'Year': 'Year',
    'Month': 'Month',
    'Day': False,                           # Not provided; derive from Date if needed
    'Time': 'Time of Activation',
    'Severity': False,                      # Not provided by Disaster Charter
    'Population_Affected': False,           # Not provided by Disaster Charter
    'Fatalities': False,                    # Not provided by Disaster Charter
    'People_Displaced': False,              # Not provided by Disaster Charter
    'Financial_Loss': False,                # Not provided by Disaster Charter
    'Alert_Level': False,                   # Not provided by Disaster Charter
    'Source': False,                        # Could set to ["Disaster Charter"] manually
    'Comments': False,                      # Not provided by Disaster Charter
    'External_Links': 'Details Link'        # URL for activation details
}