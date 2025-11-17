"""
Bittensor Service

This module provides a service for interacting with the Bittensor network,
including subtensor connections and metagraph management.
"""
import os
import argparse
import logging
import bittensor as bt

logger = logging.getLogger("bittensor_service")


class BittensorService:
    """Service for Bittensor network interactions."""

    _instance = None

    @classmethod
    def get_instance(cls, config=None):
        if cls._instance is None:
            if config is None:
                config = cls.get_config()
            cls._instance = cls(config)
        return cls._instance

    @classmethod
    def get_config(cls):
        """Get Bittensor configuration from command line arguments."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--netuid", type=int, default=1, help="Chain subnet uid")
        bt.wallet.add_args(parser)
        bt.subtensor.add_args(parser)
        bt.logging.add_args(parser)
        config = bt.config(parser)

        bt.logging.info(f"get_config: {config}")
        return config

    def __init__(self, config):
        """Initialize the Bittensor service."""
        self.config = config
        self.netuid = config.netuid  # Hardcode for now
        try:
            self.wallet = bt.wallet(config=config)
            # self.subtensor = bt.subtensor(config=config)
            # self.metagraph = self.subtensor.metagraph(config.netuid)
            # logger.info(f"Bittensor service initialized for netuid {self.metagraph.netuid}")
            # logger.info(f"Chain endpoint: {self.subtensor.chain_endpoint}")
            logger.info(f"Wallet Initialised: {self.wallet.hotkey}")
        except Exception as e:
            logger.warning(f"Failed to initialize Bittensor service components: {e}")
            self.wallet = None
            self.subtensor = None
            self.metagraph = None