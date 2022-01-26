import datetime
import requests
import time


class RTM:
    def __init__(self):
        """Init main class
        """
        None
        
    def get_station_details(self, nom_pt_reseau):
        content_type = 'application/json'
        epoch_time   = int(time.time())

        # create request
        session = requests.Session()
        url = 'https://map.rtm.fr/WebBusServeur/getStationDetails?nomPtReseau={0}&response={1}&{2}'.format(
            nom_pt_reseau,
            content_type,
            epoch_time)
        print(url)
        session.get(url)

        # get response
        response = session.get(url).json()
        
        if 'getStationDetailsResponse' not in response:
            raise ValueError("Error: Empty response from the API")
        if 'comLieu' not in response['getStationDetailsResponse']:
            raise ValueError("Error: Invalid station requested to the API")
            
        com_lieu = response['getStationDetailsResponse']['comLieu']
        
        if 'passage' not in response['getStationDetailsResponse']:
            return com_lieu, None, None, None, None 
            
        for passage in response['getStationDetailsResponse']['passage']:
            if passage['heurePassageReel']:
                nom_ligne_cial     = passage['nomLigneCial']
                heure_passage_reel = passage['heurePassageReel']
                passage_reel       = passage['passageReel']
                destination        = passage['destination']
                
                # only read first element
                break

        return com_lieu, nom_ligne_cial, heure_passage_reel, passage_reel, destination
