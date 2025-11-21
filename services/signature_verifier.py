"""
Signature Verifier Service

This module provides signature verification functionality for Bittensor wallet signatures.
"""
import logging
from fastapi import HTTPException

logger = logging.getLogger("signature_verifier")

# Constants for signature verification
HTTP_401_UNAUTHORIZED = 401
ERROR_INVALID_WALLET = "Invalid wallet address"
ERROR_INVALID_SIGNATURE = "Invalid signature"
ERROR_SIGNATURE_VERIFICATION_FAILED = "Signature verification failed"
REFRESH_INTERVAL_SECONDS = 300  # 5 minutes


class SignatureVerifier:
    """Signature verifier for Bittensor wallet signatures."""

    def __init__(self):
        """Initialize the signature verifier."""
        from services import bittensor_service
        self.bittensor_service = bittensor_service


    def sign_message(self, wallet_hotkey , message: str) -> str:
        """
        Sign a message using the Bittensor wallet hotkey.

        Args:
            wallet_hotkey: The wallet hotkey to sign with
            message: The message to sign

        Returns:
            str: The hex-encoded signature

        Raises:
            HTTPException: If signing fails
        """
        try:
            # Create message bytes
            message_bytes = message.encode("utf-8")

            if not wallet_hotkey:
                raise Exception("Wallet hotkey not initialized")

            # Sign the message
            signature_bytes = wallet_hotkey.sign(message_bytes)

            # Convert to hex string
            signature_hex = signature_bytes.hex()

            logger.info(f"Successfully signed message for wallet: {wallet_hotkey.ss58_address}")
            return signature_hex

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error signing message: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to sign message")

    def create_signature(self, gist_url: str) -> str:
        """
        Create a signature for the wallet address from BittensorService and gist URL using Bittensor.

        Args:
            gist_url: The gist URL to sign

        Returns:
            str: The hex-encoded signature

        Raises:
            HTTPException: If signature creation fails
        """
        try:
            if not self.bittensor_service.wallet:
                raise HTTPException(status_code=500, detail="Wallet not initialized")

            wallet_address = self.bittensor_service.wallet.hotkey.ss58_address

            # Create expected message
            expected_message = f"{wallet_address}:{gist_url}"

            # Sign the message
            return self.sign_message(self.bittensor_service.wallet.hotkey, expected_message)

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error creating signature: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create signature")
