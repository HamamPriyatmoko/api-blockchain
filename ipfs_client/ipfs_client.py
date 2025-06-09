import requests
import json
from config import PINATA_API_KEY, PINATA_SECRET_API_KEY

def upload_file_to_pinata(file_stream, filename):
    """
    Uploads a file-like object to Pinata via pinFileToIPFS endpoint.
    Returns the IPFS CID (string).
    """
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    # file_stream should be a file-like object, filename is the original name
    files = {
        'file': (filename, file_stream)
    }
    response = requests.post(url, files=files, headers=headers)
    response.raise_for_status()
    return response.json()['IpfsHash']

def upload_json_to_pinata(data: dict) -> str:
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "pinataContent": data
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        res_json = response.json()
        return res_json['IpfsHash']
    else:
        raise Exception(f"Failed to upload to Pinata: {response.text}")

def get_json_from_ipfs(cid: str) -> dict:
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from IPFS: {response.status_code} {response.text}")
