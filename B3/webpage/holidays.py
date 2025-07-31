import os
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from datetime import date

load_dotenv()

YEAR:str = date.today().strftime("%Y")

def parse_b3_calendar():
    """
    Parse B3 holiday calendar and convert to structured JSON
    """
    url = os.getenv("B3_HOLIDAY_URL")

    # Debug: Check if URL is loaded
    if not url:
        print("ERROR: B3_HOLIDAY_URL not found in environment variables")
        return None

    try:
        response = requests.get(url)
        print(f"Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return None

    except Exception as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Debug: Check if we found the target div
    target_div = soup.find("div", id=f'panel{YEAR[-1]}a')
    if not target_div:
        print("ERROR: Could not find div with id='panel5a'")
        return None

    text = target_div.get_text()
    print(f"Extracted text length: {len(text)} characters")

    # Parse the calendar data
    holidays = parse_calendar_text(text)

    return holidays

def parse_calendar_text(text):
    """
    Parse the calendar text into structured data
    """
    holidays = []

    # Clean up the text
    text = text.replace('\xa0', ' ')  # Replace non-breaking spaces

    # Month mapping
    months = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }

    current_month = None

    # Split text into lines and process
    lines = text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check if this line is a month name
        if line in months:
            current_month = line
            print(f"Processing month: {current_month}")
            i += 1
            continue

        # Check if this line is a day number (should be 1-2 digits)
        if line.isdigit() and len(line) <= 2 and current_month:
            day = line.zfill(2)  # Pad with zero if needed

            # Look for the event name in the next few lines
            event_name = None
            description_parts = []

            # Skip empty lines and table headers
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()

                # Skip common table headers and empty lines
                if not next_line or next_line in ['Dia', 'Evento', 'Descrição']:
                    j += 1
                    continue

                # Check if we hit the next day or month
                if (next_line.isdigit() and len(next_line) <= 2) or next_line in months:
                    break

                # First non-empty line after day number is usually the event name
                if not event_name:
                    event_name = next_line
                    j += 1
                    continue

                # Collect description lines
                # Stop if we hit certain section headers or the next entry
                if next_line in ['Listed B3', 'OTC B3', 'Financing Infrastructure', 
                                'Insurconnect', 'Tesouro Direto', 
                                'B3 Clearinghouse and B3 Foreign Exchange Clearinghouse']:
                    # Start collecting description from this section
                    while j < len(lines):
                        desc_line = lines[j].strip()
                        if (desc_line.isdigit() and len(desc_line) <= 2) or desc_line in months:
                            break
                        if desc_line:
                            description_parts.append(desc_line)
                        j += 1
                    break

                # Add other description text
                if next_line:
                    description_parts.append(next_line)

                j += 1

            # Create holiday entry if we have the required data
            if event_name:
                holiday = {
                    'month': current_month.lower(),
                    'day': day,
                    'evento': event_name,
                    'descricao': ' '.join(description_parts) if description_parts else ''
                }
                holidays.append(holiday)
                print(f"Added: {current_month} {day} - {event_name}")

        i += 1

    return holidays

def save_to_json(holidays, filename=f'{YEAR}_holidays.json'):
    """
    Save holidays to JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(holidays, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(holidays)} holidays to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def main():
    """
    Main function to run the parser
    """
    print("Starting B3 Holiday Calendar Parser...")

    holidays = parse_b3_calendar()

    if holidays:
        print(f"\nFound {len(holidays)} holidays:")
        for holiday in holidays[:3]:  # Show first 3 as examples
            print(f"  {holiday['month']} {holiday['day']}: {holiday['evento']}")

        save_to_json(holidays)

        # Show sample JSON format
        print("\nSample JSON output:")
        print(json.dumps(holidays[0], indent=2, ensure_ascii=False))
    else:
        print("Failed to parse holidays")

if __name__ == "__main__":
    main()
