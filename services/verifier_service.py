"""
Verifier Service

This module provides functionality for interacting with the verifier agent server,
including sending submissions with signatures.
"""
import os
import logging
import requests
from . import bittensor_service
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
        # Ensure bittensor_service is initialized
        await bittensor_service.initialize()

        # Create signature verifier
        verifier = SignatureVerifier()

        wallet_address = bittensor_service.wallet.hotkey.ss58_address

        # Create signature
        logger.info(f"Creating signature for wallet: {wallet_address}, gist_url: {gist_url}")
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
            if response_json.get("saved", False):
                logger.info("Submission successfully saved on server")
            else:
                logger.warning("Submission was not saved on server")
            return response_json
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to submit to verifier server: {e}")
            raise