import requests
import json
import time

base_url = "https://api-testing.mozio.com/v2"
headers = {
    "API-KEY": "USE YOUR TOKEN HERE"
}

def search_trip(body):
    """
        Search trips giving a specific information: start, end, locations. 
    
    Args:
        params (dict): Input that describes the intended trip.

    Returns:
        dict: Information with the rest of the information of the trip.
    """
    url = f"{base_url}/search/"
    response = requests.post(url, headers=headers, json=body)
    search_info = response.json()
    return search_info

def poll_search(search_id, callback = None):
    """
        This function will keep looking the search_trip until it is completed. 
    
    Args:
        search_id: Id of the search that was created
        callback (callable): Callback function to provide progress information.

    Returns:
        search_status (dict) or None: dictionary with the information of the creation of the search or None if max retries reached.
    """
    max_retries = 10
    poll_interval = 2
    for retry in range(max_retries):
        url = f"{base_url}/search/{search_id}/poll/"
        
        try:
            response = requests.get(url, headers=headers, timeout=poll_interval)
            search_status = response.json()
            status = search_status.get("status")
            result_id = ""
            more_coming = search_status.get("more_coming")
            if search_status["results"] and search_status["results"][0]["result_id"]:
                result_id = search_status["results"][0]["result_id"]

            if more_coming == True:
                response = requests.get(url, headers=headers, timeout=poll_interval)
                status = search_status.get("status")
                if status == "confirmed":
                    print("Search creation is confirmed.")
                elif status == "pending":
                    print("Search creation is still pending.")
                else:
                    print("search creation failed.")
                
            else:
                print("Polling complete.")
                print("Status: ", status)
                return result_id
        except requests.Timeout:
            if callback:
                callback("Timeout occurred. Retrying...")
        except requests.RequestException as e:
            if callback:
                callback(f"An error occurred: {e}")
        except json.JSONDecodeError: 
            if callback:
                callback("Error decoding JSON response.")


def create_reservation(body):
    """Create a reservation with the information retrieved from the search. 

    Args:
        params (dict): a dictionary with the information needed for the reservation.

    Returns:
        reservation_info (dict): a dictionary with the information of the reservation.
    """

    url = f"{base_url}/reservations/"
    response = requests.get(url, headers=headers, json=body)
    reservation_info = response.json()
    return reservation_info

def poll_reservation(search_id, callback = None):
    """
        This function will keep looking the creation of the reservation until it is completed. 
    
    Args:
        reservation_id: Id of the reservation that was created

    Returns:
        reservation_status (dict): dictionary with the information of the reservation
    """
    max_retries = 10
    poll_interval = 2

    for retry in range(max_retries):
        url = f"{base_url}/reservation/{search_id}/poll/"
        try:
            response = requests.get(url, headers=headers, timeout=poll_interval)
            reservation_status = response.json()

            status = reservation_status.get("status")
            if status == "completed":
                return reservation_status
            elif status == "failed":
                error_message = reservation_status.get("error_message")
                print(f"Reservation failed with message: {error_message}")
                return None

            if callback:
                callback(f"Polling in progress - Attempt: {retry+1}, Status: {status}")
        except requests.Timeout:
            if callback:
                callback("Timeout occurred. Retrying...")
        except requests.RequestException as e:
            if callback:
                callback(f"An error occurred: {e}")
        except json.JSONDecodeError:
            if callback:
                callback("Error decoding JSON response.")
        
        time.sleep(poll_interval)

    if callback:
        callback("Max retries reached. Reservation status not completed.")
    return None

def progress_callback(status_info):
    """Callback function to display polling progress information."""
    print(status_info)

def cancel_reservation(reservation_id):
    """This function perform the cancelation of a reservation by deleting it.
    
    Args:
        reservation_id:Id of the reservation got from the poll reservation.
    
    Returns:
        bool: True when the deletion was completed. 
        """
    
    url = f"{base_url}/reservations/{reservation_id}/"
    response = requests.delete(url, headers=headers)
    return response.json()


def main():

    searched_trip = search_trip(
        {
            "start_address": "44 Tehama Street, San Francisco, CA, USA",
            "end_address": "SFO",
            "mode": "one_way",
            "pickup_datetime": "2023-12-01 15:30",
            "num_passengers": 2,
            "currency": "USD",
            "campaign": "Deisy Jaqueline Giraldo Rivera",
            "branch": "version_test"
        })
    print("search id: ", {searched_trip["search_id"]})
    result_id = poll_search(searched_trip["search_id"])
    print("Result_id: ", result_id)

    reservation_info = create_reservation(body = {
        "search_id": searched_trip["search_id"],
        "result_id": result_id,
        "email": "happytraveler@mozio.com",
        "country_code_name": "US",
        "phone_number": "8776665544",
        "first_name": "Happy",
        "last_name": "Traveler",
        "currency": "USD",
        "provider": {
            "name": "Dummy External Provider"
        },
        "airline": "AA",
        "flight_number": "269",
        "customer_special_instructions": "Check the alarms"
    })
    print("Reservation info: ", reservation_info)
    confirmation_search = poll_reservation(searched_trip["search_id"])
    if confirmation_search:
        print("Reservation confirmed:", confirmation_search)
    else:
        pass

    cancel_reservation(confirmation_search["reservation"]["id"])

if __name__ == "__main__":
    main()
