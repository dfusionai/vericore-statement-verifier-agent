from __future__ import annotations
import os
import time
import click
import random
import aiohttp
import asyncio
import aiofiles
import traceback
import logging
import bittensor as bt
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from vericore_agent import Container

logger = logging.getLogger("neurons")

NETUID = int(os.getenv('NETUID', '2'))
logger.debug(f"Using NETUID: {NETUID}")

# ---------------- Subtensor ----------------
SUBTENSOR = None
async def get_subtensor():
    global SUBTENSOR
    if SUBTENSOR is None:
        subtensor_endpoint = os.getenv('SUBTENSOR_ENDPOINT', 'ws://127.0.0.1:9944')
        logger.debug(f"Making Bittensor connection...: {subtensor_endpoint}")
        if bt is None:
            raise RuntimeError("bittensor not installed")
        SUBTENSOR = bt.async_subtensor(subtensor_endpoint)
        try:
            await SUBTENSOR.initialize()
            logger.debug("Connected")
        except Exception as e:
            os._exit(1)
    return SUBTENSOR


# ---------------- Get Agent. ----------------
async def pull_agent(uid: int) -> Optional[str]:
    """
    Pulls agent code from blockchain commitment (gist URL) and downloads all files.
    Returns the directory path where files were saved.
    """
    try:
        logger.info(f"Starting to pull agent for uid: {uid}")
        sub = await get_subtensor()
        commit = await sub.get_revealed_commitment(netuid=NETUID, uid=uid)
        g = commit[0][1]
        block = commit[0][0]
        if g.startswith("http") and "api.github.com" not in g:
            g = f"https://api.github.com/gists/{g.rstrip('/').split('/')[-1]}"
            logger.debug(f"Converted to gist URL: {g}")
        if not g.startswith("http"):
            g = f"https://api.github.com/gists/{g}"
            logger.debug(f"Added gist prefix: {g}")
        logger.info(f"Final gist URL: {g}")
        
        # Download all files from the gist
        async with aiohttp.ClientSession() as s:
            async with s.get(g) as r:
                data = await r.json()
        
        # Create directory for this agent
        dir_path = Path(f"agents/{uid}/{block}/")
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Download all files from the gist
        files_downloaded = []
        async with aiohttp.ClientSession() as s:
            for filename, file_meta in data["files"].items():
                content = file_meta.get("content")
                if content is None or file_meta.get("truncated"):
                    # If content is truncated or missing, fetch from raw_url
                    async with s.get(file_meta["raw_url"]) as r:
                        content = await r.text()
                
                # Preserve directory structure from gist (if filename has path separators)
                file_path = dir_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(content or "")
                files_downloaded.append(filename)
                logger.debug(f"Downloaded file: {filename}")
        
        resolved_path = str(dir_path.resolve())
        logger.info(f"Successfully pulled {len(files_downloaded)} file(s) to: {resolved_path}")
        return resolved_path
    except Exception as e:
        logger.warning(f'Failed pulling agent on uid: {uid} with error: {e}')
        return None


# ---------------- Add Files for Gist ----------------
def add_files_for_gist(file_path: str) -> dict:
    """
    Recursively finds all files in the given path and returns a dictionary
    suitable for GitHub Gist API, with file paths as keys and content as values.
    
    Args:
        file_path: Path to a file or directory
        
    Returns:
        Dictionary mapping file paths to {'content': file_content} for Gist API
        
    Raises:
        RuntimeError: If path doesn't exist or no files found
    """
    files_dict = {}
    path_obj = Path(file_path)
    
    # Collect all files to include
    files_to_include = []
    if path_obj.is_file():
        # If it's a file, include just that file
        files_to_include = [path_obj]
    elif path_obj.is_dir():
        # If it's a directory, recursively find all files
        files_to_include = list(path_obj.rglob("*"))
        # Filter out directories and only keep files
        files_to_include = [f for f in files_to_include if f.is_file()]
    else:
        raise RuntimeError(f"Path does not exist: {file_path}")
    
    # Read all files and add to files_dict
    for file_path_item in files_to_include:
        try:
            with open(file_path_item, "r", encoding="utf-8") as f:
                content = f.read()
            # Use relative path from original file_path as the key to preserve directory structure
            if path_obj.is_file():
                # For single file, use just the filename
                file_key = file_path_item.name
            else:
                # For directory, use relative path from the directory
                file_key = str(file_path_item.relative_to(path_obj))
            files_dict[file_key] = {"content": content}
            logger.debug(f"Added file to gist: {file_key}")
        except Exception as e:
            logger.warning(f"Failed to read file {file_path_item}: {e}")
            continue

    if not files_dict:
        raise RuntimeError(f"No files found to upload in: {file_path}")
    
    return files_dict


# ---------------- CLI ----------------
@click.group()
@click.option('--log-level', type=click.Choice(['CRITICAL','ERROR','WARNING','INFO','DEBUG'], case_sensitive=False), default=None, help='Logging level (or set LOG_LEVEL env)')
def cli(log_level: Optional[str]):
    load_dotenv(override=True)
    level_name = (log_level or os.getenv('LOG_LEVEL') or 'INFO').upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


@cli.command("push")
@click.argument("file_path", default="agents/base_agent.py", required=False)
@click.option("--wallet-coldkey", envvar="BT_WALLET_COLD", help="Bittensor coldkey wallet name")
@click.option("--wallet-hotkey", envvar="BT_WALLET_HOT", help="Bittensor hotkey wallet name")
@click.option("--github-token", envvar="GITHUB_TOKEN", help="GitHub token for creating gists")
def push(file_path: str, wallet_coldkey: Optional[str], wallet_hotkey: Optional[str], github_token: Optional[str]):
    def require_value(name: str, value: Optional[str], env_name: str) -> str:
        if value:
            return value
        env_value = os.getenv(env_name)
        if env_value:
            return env_value
        raise RuntimeError(f"Missing required value for {name}. Set --{name.replace('_', '-')} or {env_name} environment variable")
    
    coldkey = require_value("wallet_coldkey", wallet_coldkey, "BT_WALLET_COLD")
    hotkey = require_value("wallet_hotkey", wallet_hotkey, "BT_WALLET_HOT")
    github_token_val = require_value("github_token", github_token, "GITHUB_TOKEN")
    wallet = bt.wallet(name=coldkey, hotkey=hotkey)

    async def main():
        logger.info(f'Loading chain state for NETUID: {NETUID}...')
        sub = await get_subtensor()
        metagraph = await sub.metagraph(NETUID)
        if wallet.hotkey.ss58_address not in metagraph.hotkeys:
            logger.info(f"Not registered, first register your wallet `btcli subnet register --netuid {NETUID} --wallet.name {coldkey} --hotkey {hotkey}`")
            os._exit(1)

        # Build up the 'files' object with all files found in file_path
        files_dict = add_files_for_gist(file_path)
        
        scheme = "token" if github_token_val.startswith(("ghp_", "github_pat_")) else "Bearer"
        headers = {
            "Authorization": f"{scheme} {github_token_val}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "neurons-cli"
        }
        gist_data = {"description": "Agent code", "public": False, "files": files_dict}
        logger.info(f"Uploading {len(files_dict)} file(s) to gist...")
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.github.com/gists", json=gist_data, headers=headers) as resp:
                if resp.status != 201:
                    try:
                        error_json = await resp.json()
                        error_msg = error_json.get("message") or str(error_json)
                    except Exception:
                        error_msg = await resp.text()
                    raise RuntimeError(
                        f"Failed to create gist ({resp.status}): {error_msg}. Ensure your GITHUB_TOKEN is valid and has 'gist' scope, visit: https://github.com/settings/tokens/new"
                    )
                gist_url = (await resp.json())["html_url"]
                logger.info(f"Created gist: {gist_url}")

        logger.info(f"Committing gist URL to blockchain for wallet: {wallet.hotkey.ss58_address}...")

        await sub.set_reveal_commitment(wallet=wallet, netuid=NETUID, data=gist_url, blocks_until_reveal=1)
        logger.info(f"Committed gist URL to blockchain.")

    asyncio.run(main())


@cli.command("pull")
@click.argument("uid", type=int, required=False)
def pull(uid: int = None):
    if uid is not None:
        asyncio.run(pull_agent(uid))
    else:
        async def pull_all():
            sub = await get_subtensor()
            metagraph = await sub.metagraph(NETUID)
            for uid in metagraph.uids:
                await pull_agent(int(uid))
        asyncio.run(pull_all())


# ---------------- Watchdog ----------------
HEARTBEAT = time.monotonic()
def update_heartbeat():
    global HEARTBEAT
    HEARTBEAT = time.monotonic()

async def watchdog(timeout: int = 300):
    global HEARTBEAT
    while True:
        await asyncio.sleep(max(1, timeout // 3))
        elapsed = time.monotonic() - HEARTBEAT
        if elapsed > timeout:
            logging.error(f"[WATCHDOG] Process stalled {elapsed:.0f}s — exiting process.")
            os._exit(1)

@cli.command("validator")
def validator():
    def require_env(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value
    coldkey = require_env("BT_WALLET_COLD")
    hotkey = require_env("BT_WALLET_HOT")
    wallet = bt.wallet(name=coldkey, hotkey=hotkey)
    logger.debug(f"Validator initialized with wallet: {coldkey}/{hotkey}")

    async def _run():
        global HEARTBEAT
        logger.debug("Starting validator main loop")
        while True:
            try:
                HEARTBEAT = time.monotonic()
                SAMPLES = 10
                sub = await get_subtensor()
                logger.debug("Subtensor connection established")

                metagraph = await sub.metagraph(NETUID)
                uids = [int(uid) for uid in metagraph.uids]
                weights = [0 for _ in metagraph.uids]
                logger.debug(f"Loaded metagraph with {len(uids)} UIDs: {uids}")

                for uid in uids:
                    update_heartbeat()
                    logger.debug(f"Processing UID {uid}")
                    gen_tmp_file: str = await pull_agent(uid)
                    logger.debug(f"Retrieved agent file for UID {uid}: {gen_tmp_file}")
                    gen_tmp_file = "gen.py"
                    logger.debug(f"Using hardcoded agent file: {gen_tmp_file}")
                    with Container(gen_tmp_file) as c:
                        logger.debug(f"Created container for UID {uid}")
                        success = 0
                        for sample_idx in range(SAMPLES):
                            try:
                                # Test statements for verification
                                test_statements = [
                                    ("The capital of France is Paris", True),
                                    ("The Earth is flat", False),
                                    ("Water freezes at 0°C", True),
                                    ("2 + 2 = 5", False),
                                    ("Python is a programming language", True),
                                    ("The sun orbits the Earth", False),
                                    ("Gravity exists", True),
                                    ("1 + 1 = 3", False),
                                ]
                                statement, expected_verdict = random.choice(test_statements)
                                
                                logger.debug(f"UID {uid} sample {sample_idx}: verifying '{statement}'")
                                result = c.verify(statement=statement, timeout=10)
                                logger.debug(f"UID {uid} sample {sample_idx}: got result: {result}")
                                
                                # Check if result is a dict with verdict
                                if isinstance(result, dict) and "verdict" in result:
                                    actual_verdict = result["verdict"]
                                    if actual_verdict == expected_verdict:
                                        success += 1
                                        logger.debug(f"UID {uid} sample {sample_idx}: correct verdict")
                                    else:
                                        logger.debug(f"UID {uid} sample {sample_idx}: incorrect verdict {actual_verdict}, expected {expected_verdict}")
                                else:
                                    logger.debug(f"UID {uid} sample {sample_idx}: invalid result format")
                            except Exception as e:
                                logger.debug(f"UID {uid} sample {sample_idx}: error - {e}")
                        weights[uid] = float(success) / SAMPLES
                        logger.debug(f"UID {uid}: scored {success}/{SAMPLES} = {weights[uid]}")

                logger.debug(f"Setting weights: UIDs={uids}, weights={weights}")
                await sub.set_weights(
                    wallet=wallet,
                    netuid=NETUID,
                    weights=weights,
                    uids=uids,
                    wait_for_inclusion=False,
                    wait_for_finalization=False
                )
                logger.debug("Weights successfully set")

            except asyncio.CancelledError:
                logger.debug("Validator loop cancelled")
                break
            except Exception as e:
                traceback.print_exc()
                logger.info(f"runner error: {e}; retrying...")
                await asyncio.sleep(5)

    async def main():
        logger.debug("Starting validator with watchdog")
        await asyncio.gather(
            _run(),
            watchdog(),
            return_exceptions=True
        )
    asyncio.run(main())



