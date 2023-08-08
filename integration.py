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
    max_retries = 100
    poll_interval = 2
    for retry in range(max_retries):
        url = f"{base_url}/search/{search_id}/poll/"
        try:
            response = requests.get(url, timeout=poll_interval)
            search_status = response.json()

            status = search_status.get("status")
            if status == "completed":
                return search_status
            elif status == "failed":
                error_message = search_status.get("error_message")
                print(f"Search creation failed with message: {error_message}")
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


def create_reservation(body):
    """Create a reservation with the information retrieved from the search. 

    Args:
        params (dict): a dictionary with the information needed for the reservation.

    Returns:
        reservation_info (dict): a dictionary with the information of the reservation.
    """

    url = f"{base_url}/reservations/"
    response = requests.get(url, headers, json=body)
    reservation_info = response.json()
    return reservation_info

def poll_reservation(search_id):
    """
        This function will keep looking the creation of the reservation until it is completed. 
    
    Args:
        reservation_id: Id of the reservation that was created

    Returns:
        reservation_status (dict): dictionary with the information of the reservation
    """
    timeout = 120
    start_time = time.time()
    while time.time() - start_time < timeout:

        url = f"{base_url}/reservation/{search_id}/poll/"
        response = requests.get(url, headers)
        reservation_status = response.json()

        if reservation_status.get("status") == "pending":
            if reservation_status("status") == "failed":
                raise RuntimeError(f"Reservation with search id {search_id} failed")

    return reservation_status

def cancel_reservation(reservation_id):
    """This function perform the cancelation of a reservation by deleting it.
    
    Args:
        reservation_id:Id of the reservation got from the poll reservation.
    
    Returns:
        bool: True when the deletion was completed. 
        """
    
    url = f"{base_url}/reservations/{reservation_id}/"
    response = requests.delete(url, headers)
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
    
    search_status = poll_search(searched_trip["search_id"])

    if search_status:
        print("Reservation confirmed:", search_status)
    else:
        pass

    create_reservation(params = {
        "search_id": search_status["search_id"],
        "email": "happytraveler@mozio.com",
        "country_code_name": "US",
        "phone_number": "8776665544",
        "first_name": "Happy",
        "last_name": "Traveler",
        "currency": "USD",
        "provider": {
            "name": "Dummy External Provider"
        }
    })

    confirmation_search = poll_reservation(searched_trip["search_id"])

    cancel_reservation(confirmation_search["reservation"]["id"])

if __name__ == "__main__":
    main()
