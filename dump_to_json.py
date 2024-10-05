import json
import sys
import os
from models import Email, Label
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
import pytz

# Configure EST timezone
est = pytz.timezone('US/Eastern')

def dump_db_to_json(db_path, output_file):
    # Ensure the database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} does not exist.")
        sys.exit(1)
    
    # Create an engine to connect to the specified database path
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query all emails that are not discarded, eager load the labels
    emails = session.query(Email).filter_by(discarded=False).options(joinedload(Email.labels)).all()
    
    # Create a list to store the final result
    data = []
    
    for email in emails:
        # Convert the email's timestamp to EST and format it as a string (e.g., "09-19-2024 17:00")
        email_time_str = datetime.fromtimestamp(email.time, est).strftime('%m-%d-%Y %H:%M')
        
        # Prepare the email document
        email_doc = {
            '_id': email.id,
            'text': email.text,
            'time': email_time_str,  # Formatted date as string in EST
            'events': []
        }

        # Add associated events (labels) to the events array
        for label in email.labels:
            event = {
                'event_name': label.event_name,
                'start_datetime': label.start_datetime.astimezone(est).strftime('%Y-%m-%d %H:%M:%S'),  # Convert to EST
                'end_datetime': label.end_datetime.astimezone(est).strftime('%Y-%m-%d %H:%M:%S')  # Convert to EST
            }
            email_doc['events'].append(event)
        
        # Append the email document to the final data list
        data.append(email_doc)
    
    # Write the data to a JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python dump_to_json.py <db_path> <output_json>")
        sys.exit(1)

    # Get the database path and output JSON file from the command-line arguments
    db_path = sys.argv[1]
    output_file = sys.argv[2]

    # Call the function to dump the database to JSON
    dump_db_to_json(db_path, output_file)
