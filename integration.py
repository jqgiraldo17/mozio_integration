import requests
import time

base_url = "https://api-testing.mozio.com/v2"
headers = {
    "API-KEY": "ADD YOUR "
}

def search_trip(headers, params):
    """
        Search trips giving a specific information: start, end, locations. 
    
    Args:
        params (dict): Input that describes the intended trip.

    Returns:
        dict: Information with the rest of the information of the trip.
    """
    url = f"{base_url}/search"
    response = requests.post(url, headers, params=params)
    search_info = response.json()
    return search_info

def poll_search(search_id, headers):
    """
        This function will keep looking the search_trip until it is completed. 
    
    Args:
        search_id: Id of the search that was created

    Returns:
        search_status (dict): dictionary with the information of the creation of the search.
    """
    timeout_secs = 200
    in_progress = 1
    start_time = time.time()
    while in_progress == 1:

        url = f"{base_url}/{search_id}/poll"
        response = requests.get(url, headers)
        search_status = response.json()

        if search_status.get("status") == "pending":
            if search_status("status") == "failed":
                raise RuntimeError(f"Creation of search id {search_id} failed")
            else:
                in_progress = 0
        
        current_time = time.time()
        elapsed_time = start_time - current_time
        
        if elapsed_time > timeout_secs:
            raise TimeoutError("Search id failed for timeout")

    return search_status


def create_reservation(headers, params):
    """Create a reservation with the information retrieved from the search. 

    Args:
        params (dict): a dictionary with the information needed for the reservation.

    Returns:
        reservation_info (dict): a dictionary with the information of the reservation.
    """

    url = f"{base_url}/reservations"
    response = requests.get(url, headers, params=params)
    reservation_info = response.json()
    return reservation_info

def poll_reservation(search_id, headers):
    """
        This function will keep looking the creation of the reservation until it is completed. 
    
    Args:
        reservation_id: Id of the reservation that was created

    Returns:
        reservation_status (dict): dictionary with the information of the reservation
    """
    timeout_secs = 200
    in_progress = 1
    start_time = time.time()
    while in_progress == 1:

        url = f"{base_url}/reservation/{search_id}/poll"
        response = requests.get(url, headers)
        reservation_status = response.json()

        if reservation_status.get("status") == "pending":
            if reservation_status("status") == "failed":
                raise RuntimeError(f"Reservation with search id {search_id} failed")
            else:
                in_progress = 0
        
        current_time = time.time()
        elapsed_time = start_time - current_time
        
        if elapsed_time > timeout_secs:
            raise TimeoutError("Reservation failed for timeout")

    return reservation_status

def cancel_reservation(reservation_id, headers):
    """This function perform the cancelation of a reservation by deleting it.
    
    Args:
        reservation_id:Id of the reservation got from the poll reservation.
    
    Returns:
        bool: True when the deletion was completed. 
        """
    
    url = f"{base_url}/reservations/{reservation_id}"
    response = requests.delete(url, headers)
    return response.json()


def main():

    searched_trip = search_trip({
        {
            "start_address": "44 Tehama Street, San Francisco, CA, USA",
            "end_address": "SFO",
            "mode": "one_way",
            "pickup_datetime": "2023-12-01 15:30",
            "num_passengers": 2,
            "currency": "USD",
            "campaign": "Deisy Jaqueline Giraldo Rivera"
            }
        })
    
    confirmation_search = poll_search(searched_trip["search_id"])

    # Create reservation with the search_id
    create_reservation(params = {
        "search_id": confirmation_search["search_id"],
        "email": "happytraveler@mozio.com",
        "country_code_name": "US",
        "phone_number": "8776665544",
        "first_name": "Happy",
        "last_name": "Traveler",
        "airline": "AA",
        "flight_number": "123",
        "customer_special_instructions": "My doorbell is broken, please yell"
    })

    confirmation_search = poll_reservation(searched_trip["search_id"])

    cancel_reservation(confirmation_search["reservation"]["id"])

if __name__ == "__main__":
    main()
