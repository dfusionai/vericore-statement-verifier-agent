"""
Signature Verifier Service

This module provides signature verification functionality for Bittensor wallet signatures.
"""
import time
import logging
import bittensor as bt
from fastapi import HTTPException
from . import bittensor_service

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
        self.bittensor_service = bittensor_service
        self.metagraph = bittensor_service.metagraph
        self.subtensor = bittensor_service.subtensor

        try:
            self.last_refresh_time = 0
            self.refresh_metagraph()
            logger.info(f"Signature verifier initialized for netuid {self.metagraph.netuid if self.metagraph else 'unknown'}")
        except Exception as e:
            logger.error(f"Failed to initialize signature verifier: {str(e)}")
            # Initialize with None and handle in methods
            self.metagraph = None
            self.subtensor = None
            self.last_refresh_time = 0

    def refresh_metagraph(self):
        """Refresh the metagraph if enough time has passed."""
        if self.metagraph is None:
            logger.warning("Metagraph not initialized, skipping refresh")
            return

        current_time = time.time()
        if (current_time - self.last_refresh_time) > REFRESH_INTERVAL_SECONDS:
            try:
                print("Refreshing metagraph")
                self.metagraph.sync()  # Fetch new data
                self.last_refresh_time = current_time
            except Exception as e:
                logger.error(f"Failed to refresh metagraph: {str(e)}")

    def verify_wallet_hotkey(self, wallet_hotkey: str) -> str:
        """
        Verify that the wallet hotkey is valid within the Bittensor network.

        Args:
            wallet_hotkey: The wallet hotkey to verify

        Returns:
            str: The verified wallet hotkey

        Raises:
            HTTPException: If wallet hotkey is invalid
        """
        if self.metagraph is None:
            logger.warning("Metagraph not initialized, skipping wallet verification")
            return wallet_hotkey  # Allow in case of initialization failure

        # Refresh metagraph
        self.refresh_metagraph()

        # Check to see whether wallet hotkey is valid within the bittensor network
        if wallet_hotkey not in self.metagraph.hotkeys:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_WALLET)

        return wallet_hotkey

    def verify_request_signature(
        self, signature: str, expected_message: str, wallet_hotkey: str
    ) -> bool:
        """
        Verify the request signature using Bittensor keypair.

        Args:
            signature: The signature to verify (hex string)
            expected_message: The expected message that was signed
            wallet_hotkey: The wallet hotkey that signed the message

        Returns:
            bool: True if signature is valid

        Raises:
            HTTPException: If signature verification fails
        """
        try:
            # Create message bytes
            message_bytes = expected_message.encode("utf-8")
            signature_bytes = bytes.fromhex(signature)

            # Create keypair from wallet hotkey
            hotkey = bt.Keypair(ss58_address=wallet_hotkey)

            # Verify signature
            verified = hotkey.verify(message_bytes, signature_bytes)

            print(f"Verified: {verified}")

            if not verified:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_SIGNATURE)

            return verified

        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=ERROR_SIGNATURE_VERIFICATION_FAILED)

    def sign_message(self, wallet_hotkey: str, message: str) -> str:
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
            # First verify the wallet hotkey is valid
            self.verify_wallet_hotkey(wallet_hotkey)

            # Create message bytes
            message_bytes = message.encode("utf-8")

            # Use the wallet's hotkey if available, otherwise create from address
            if self.bittensor_service.wallet and self.bittensor_service.wallet.hotkey.ss58_address == wallet_hotkey:
                hotkey = self.bittensor_service.wallet.hotkey
            else:
                # Fallback to creating from address (won't work for signing without private key)
                hotkey = bt.Keypair(ss58_address=wallet_hotkey)

            # Sign the message
            signature_bytes = hotkey.sign(message_bytes)

            # Convert to hex string
            signature_hex = signature_bytes.hex()

            logger.info(f"Successfully signed message for wallet: {wallet_hotkey}")
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
            return self.sign_message(wallet_address, expected_message)

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error creating signature: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create signature")

    def verify_signature(self, wallet_address: str, gist_url: str, signature: str) -> bool:
        """
        Verify the signature for the given wallet address and gist URL using Bittensor.

        Args:
            wallet_address: The wallet address that signed the message
            gist_url: The gist URL that was signed
            signature: The signature to verify

        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # First verify the wallet hotkey is valid
            self.verify_wallet_hotkey(wallet_address)

            # Create expected message
            expected_message = f"{wallet_address}:{gist_url}"

            # Verify the signature
            return self.verify_request_signature(signature, expected_message, wallet_address)

        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False