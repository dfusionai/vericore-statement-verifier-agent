"""
Services package for reusable components.
"""
import os
from .bittensor_service import BittensorService
from .verifier_service import VerifierService

# Global service instances
bittensor_service = BittensorService.get_instance()
verifier_service = VerifierService()