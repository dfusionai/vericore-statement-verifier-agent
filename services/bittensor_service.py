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
        bt.subtensor.add_args(parser)
        bt.logging.add_args(parser)
        config = bt.config(parser)

        bt.logging.info(f"get_config: {config}")
        return config

    def __init__(self, config):
        """Initialize the Bittensor service."""
        self.config = config
        self.netuid = config.netuid  # Hardcode for now
        self.wallet = bt.wallet(config=config)
        self.subtensor = bt.subtensor(config=config)
        self.metagraph = self.subtensor.metagraph(config.netuid)
        self._initialized = False

        logger.info(f"Bittensor service initialized for netuid {self.metagraph.netuid}")
        logger.info(f"Chain endpoint: {self.subtensor.chain_endpoint}")


    async def initialize(self):
        """Initialize the subtensor connection and metagraph."""
        if self._initialized:
            return

        try:
            # Initialize wallet and subtensor if config is available
            if self.config:
                if self.wallet is None:
                    self.wallet = bt.wallet(config=self.config)
                if self.subtensor is None:
                    self.subtensor = bt.subtensor(config=self.config)

            # Initialize subtensor
            await self._ensure_subtensor()
            # Initialize metagraph
            await self._ensure_metagraph()
            self._initialized = True
            logger.info(f"Bittensor service initialized for netuid {self.netuid}")
        except Exception as e:
            logger.error(f"Failed to initialize Bittensor service: {str(e)}")
            raise

    async def _ensure_subtensor(self):
        """Ensure subtensor is connected."""
        if self.subtensor is None:
            subtensor_endpoint = os.getenv('SUBTENSOR_ENDPOINT', 'ws://127.0.0.1:9944')
            logger.debug(f"Making Bittensor connection...: {subtensor_endpoint}")
            if bt is None:
                raise RuntimeError("bittensor not installed")
            self.subtensor = bt.async_subtensor(subtensor_endpoint)
            try:
                await self.subtensor.initialize()
                logger.debug("Connected to subtensor")
            except Exception as e:
                logger.error(f"Failed to connect to subtensor: {str(e)}")
                raise

    async def _ensure_metagraph(self):
        """Ensure metagraph is loaded."""
        if self.metagraph is None and self.subtensor is not None:
            try:
                self.metagraph = self.subtensor.metagraph(self.netuid)
                logger.debug(f"Loaded metagraph for netuid {self.netuid}")
            except Exception as e:
                logger.error(f"Failed to load metagraph: {str(e)}")
                raise

    async def get_subtensor(self):
        """Get the subtensor instance, initializing if necessary."""
        await self._ensure_subtensor()
        return self.subtensor

    async def get_metagraph(self):
        """Get the metagraph instance, initializing if necessary."""
        await self._ensure_metagraph()
        return self.metagraph

    async def refresh_metagraph(self):
        """Refresh the metagraph data."""
        if self.subtensor is not None:
            try:
                self.metagraph = await self.subtensor.metagraph(self.netuid)
                logger.debug("Refreshed metagraph")
            except Exception as e:
                logger.error(f"Failed to refresh metagraph: {str(e)}")
                raise