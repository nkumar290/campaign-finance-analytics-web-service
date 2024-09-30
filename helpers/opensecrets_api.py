#opensecrets_api.py
import json, os, requests, sqlite3
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from mysql_util import get_connection

load_dotenv()
api_key = os.getenv("OPENSECRETS_API_KEY")

# Fetch legislators data for a given state
def get_legislators(state_code):
    params = {
        "method": "getLegislators",
        "id": state_code,
        "output": "json",
        "apikey": API_KEY,
    }

    response = requests.get(API_BASE_URL, params=params)

    try:
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

    if "error" in data:
        return {"error": data["error"]}

    legislators_list = data["response"]["legislator"]
    return legislators_list


# Function to insert legislators data into the database (Calls insert_legislators function )
def insert_legislators_for_all_states():
    state_codes = [
        "al","ak","az","ar","ca","co","ct","de","fl","ga","hi","id","il",
        "in","ia","ks","ky","la","me","md","ma","mi","mn","ms","mo","mt",
        "ne","nv","nh","nj","nm","ny","nc","nd","oh","ok","or","pa","ri",
        "sc","sd","tn","tx","ut","vt","va","wa","wv","wi","wy",
    ]

    for state_code in state_codes:
        legislators_data = get_legislators(state_code)

        if "error" not in legislators_data:
            print("Inserting data for", state_code)
            insert_legislators(legislators_data)
            

# Insert state legislator data into the database
def insert_legislators(data):
    try:
        conn = get_connection() # sqlite3.connect("legislators.db")
        c = conn.cursor()

        for legislator in data:
            attributes = legislator["@attributes"]

            # Extract 'first_elected' and 'exit_code' from attributes dictionary
            first_elected = attributes.get("first_elected")
            exit_code = attributes.get("exit_code")

            # Prepare the list of column names and values to be inserted
            columns = [
                "cid", "firstlast", "lastname", "party", "office", "gender",
                "firstelectoff", "exitcode", "comments", "phone", "fax", "website",
                "webform", "congress_office", "bioguide_id", "votesmart_id", 
                "feccandid", "twitter_id", "youtube_url", "facebook_id", "birthdate"
            ]

            values = [
                attributes.get(col) if col not in ["firstelectoff", "exitcode"] else None
                for col in columns
            ]

            # Set the 'firstelectoff' and 'exitcode' values
            values[columns.index("firstelectoff")] = first_elected
            values[columns.index("exitcode")] = exit_code

            # Insert the values into the database
            c.execute(
                f"""INSERT INTO current_legislators ({', '.join(columns)})
                          VALUES ({', '.join(['?'] * len(columns))})""",
                values,
            )

        conn.commit()
        conn.close()
        print("Data inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting data into the database: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()