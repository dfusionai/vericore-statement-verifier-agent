from __future__ import annotations
import os
import click
import aiohttp
import asyncio
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from services import verifier_service, bittensor_service

logger = logging.getLogger("neurons")


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
@click.option("--wallet.name", "wallet_name", envvar="BT_WALLET_COLD", help="Bittensor coldkey wallet name")
@click.option("--wallet.hotkey", "wallet_hotkey", envvar="BT_WALLET_HOT", help="Bittensor hotkey wallet name")
@click.option("--github-token", envvar="GITHUB_TOKEN", help="GitHub token for creating gists")
def push(file_path: str, wallet_name: Optional[str], wallet_hotkey: Optional[str], github_token: Optional[str]):
    def require_value(name: str, value: Optional[str], env_name: str) -> str:
        if value:
            return value
        env_value = os.getenv(env_name)
        if env_value:
            return env_value
        raise RuntimeError(f"Missing required value for {name}. Set --{name.replace('_', '-')} or {env_name} environment variable")

    coldkey = require_value("wallet_name", wallet_name, "BT_WALLET_COLD")
    hotkey = require_value("wallet_hotkey", wallet_hotkey, "BT_WALLET_HOT")
    github_token_val = require_value("github_token", github_token, "GITHUB_TOKEN")
    logger.debug(f"Creating wallet with name={coldkey}, hotkey={hotkey}")
    wallet = bittensor_service.wallet

    async def main():
        logger.debug(f"Wallet {wallet.hotkey.ss58_address} is registered")

        # Build up the 'files' object with all files found in file_path
        logger.debug(f"Building files dict for path: {file_path}")
        files_dict = add_files_for_gist(file_path)
        logger.debug(f"Files dict built with {len(files_dict)} files")

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
                logger.debug(f"Gist API response status: {resp.status}")
                if resp.status != 201:
                    try:
                        error_json = await resp.json()
                        error_msg = error_json.get("message") or str(error_json)
                    except Exception:
                        error_msg = await resp.text()
                    raise RuntimeError(
                        f"Failed to create gist ({resp.status}): {error_msg}. Ensure your GITHUB_TOKEN is valid and has 'gist' scope, visit: https://github.com/settings/tokens/new"
                    )
                gist_response = await resp.json()
                gist_url = gist_response["html_url"]
                logger.info(f"Created gist: {gist_url}")

        logger.info(f"Sending submission to verifier server for wallet: {wallet.hotkey.ss58_address}...")

        await verifier_service.send_submission(gist_url)
        logger.info(f"Submission sent to verifier server.")

    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Push command failed: {e}")
        raise







