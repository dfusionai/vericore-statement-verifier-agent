"""
Verifier Service

This module provides functionality for interacting with the verifier agent server,
including sending submissions with signatures.

Key features:
- Sends POST requests to the verifier server with wallet signature and gist URL
- Checks submission success based on presence of 'submission_id' and absence of 'rejection_reason'
- Logs successful submissions with highlighted submission ID in green
- Handles HTTP 409 (rate limiting) by logging a warning and returning None
- Raises exceptions for other HTTP errors and request failures
"""
import os
import logging
import requests
from .signature_verifier import SignatureVerifier

logger = logging.getLogger("verifier_service")


class VerifierService:
    """Service for verifier server interactions."""

    def __init__(self):
        """Initialize the verifier service."""
        self.verifier_server_url = os.getenv('VERIFIER_SERVER_URL', 'http://localhost:8000')

    async def send_submission(self, gist_url: str):
        """
        Send submission to verifier agent server by creating and using a signature.

        Args:
            gist_url: The gist URL

        Raises:
            HTTPException: If signature creation fails
        """
        from services import bs as bittensor_service
        # Create signature verifier
        verifier = SignatureVerifier()
        logger.info(f"Wallet used: {bittensor_service.wallet}")
        wallet_address = bittensor_service.wallet.hotkey.ss58_address

        # Create signature
        logger.info(f"Creating signature for wallet: {wallet_address}, gist_url: {gist_url}")
        logger.debug(f"Wallet object: {bittensor_service.wallet}")
        try:
            signature = verifier.create_signature(gist_url)
            logger.info("Signature created successfully")
        except Exception as e:
            logger.error(f"Failed to create signature: {e}")
            raise

        # Make POST request to verifier server
        url = f"{self.verifier_server_url}/api/v1/miners/submission"
        headers = {
            "signature": signature,
            "wallet": wallet_address,
            "gist_url": gist_url,
            "Content-Type": "application/json"
        }
        data = {
            "decrypted_gist_url": gist_url
        }

        logger.info(f"Sending submission to verifier server: URL={url}, wallet={wallet_address}, gist_url={gist_url}")

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()
            logger.info(f"Received response from verifier server: status={response.status_code}, response={response_json}")
            if 'submission_id' in response_json and response_json.get('rejection_reason') is None:
                logger.info(f"Submission successfully saved on server with ID: \033[92m{response_json['submission_id']}\033[0m")
            else:
                logger.warning("Submission was not saved on server")
            return response_json
        except requests.exceptions.HTTPError as e:
            if response.status_code == 409:
                logger.warning("Submission was too quick - rate limited")
                return None
            else:
                logger.error(f"Failed to submit to verifier server: {e}")
                raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to submit to verifier server: {e}")
            raise