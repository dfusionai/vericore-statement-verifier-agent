"""
Miner Agent - Pulls agent code from blockchain and runs verify routine.

This script:
1. Pulls agent code from blockchain commitment (gist) for a given UID
2. Builds Docker image from the pulled directory
3. Runs the Docker container
4. Calls the FastAPI /verify endpoint with test statements
"""
import subprocess
import time
import requests
import asyncio
from pathlib import Path
from neurons import pull_agent, NETUID

# Docker configuration
DOCKER_IMAGE_NAME_PREFIX = "miner-statement-app"
DOCKER_CONTAINER_NAME_PREFIX = "miner-statement-api"
API_PORT = 8080  # Required port per specification
API_URL = f"http://localhost:{API_PORT}"


def docker_command(*args, check=True, capture_output=True):
    """Run a docker command and return the result."""
    try:
        result = subprocess.run(
            ["docker", *args],
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Docker command failed: {' '.join(['docker', *args])}")
        print(f"Error: {e.stderr if e.stderr else e}")
        raise
    except FileNotFoundError:
        print("Error: Docker is not installed or not in PATH")
        raise


def stop_and_remove_container(container_name: str):
    """Stop and remove a Docker container if it exists."""
    try:
        # Check if container exists
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        if container_name in result.stdout:
            print(f"Stopping container: {container_name}")
            subprocess.run(["docker", "stop", container_name], capture_output=True)
            print(f"Removing container: {container_name}")
            subprocess.run(["docker", "rm", container_name], capture_output=True)
    except Exception as e:
        print(f"Warning: Could not stop/remove container: {e}")


def build_docker_image(image_name: str, build_path: Path):
    """Build the Docker image."""
    print(f"Building Docker image: {image_name}")
    print(f"Build path: {build_path}")
    
    if not build_path.exists():
        raise FileNotFoundError(f"Build path does not exist: {build_path}")
    
    # Don't capture output so user can see build progress in real-time
    # This helps identify if the build is actually running or stuck
    try:
        result = subprocess.run(
            ["docker", "build", "-t", image_name, str(build_path)],
            check=True,
            capture_output=False  # Show output in real-time
        )
        print(f"Successfully built image: {image_name}")
    except subprocess.CalledProcessError as e:
        if e.returncode == 130:
            print("\n⚠️  Docker build was interrupted (exit code 130)")
            print("Possible causes:")
            print("  - Build was manually canceled (Ctrl+C)")
            print("  - Docker daemon stopped or restarted")
            print("  - System resource constraints (memory/CPU)")
            print("  - Network timeout during dependency download")
            print("\nTry running the build again. If it persists, check:")
            print("  - Docker daemon status: docker info")
            print("  - Available disk space: df -h")
            print("  - Docker system resources: docker system df")
        raise


def run_docker_container(image_name: str, container_name: str, port: int):
    """Run the Docker container with resource limits enforced."""
    print(f"Running Docker container: {container_name}")
    
    # Stop and remove existing container if it exists
    stop_and_remove_container(container_name)
    
    # Resource limits as documented in Specification
    # CPU: 8 cores maximum
    # RAM: 32GB maximum
    # GPU: 24GB VRAM (NVIDIA GPU with CUDA support) - optional, only if available
    # Storage: 500GB maximum - handled by Docker daemon configuration
    
    docker_args = [
        "run", "-d",
        "--name", container_name,
        "-p", f"{port}:{port}",
        "--cpus", "8",  # CPU: 8 cores maximum
        "--memory", "32g",  # RAM: 32GB maximum
        "--memory-swap", "32g",  # Disable swap to enforce hard limit
    ]
    
    # Add GPU support if NVIDIA GPU is available (optional)
    # Note: GPU VRAM limit of 24GB should be configured at Docker daemon level
    # or via nvidia-container-runtime. Here we just enable GPU access if available.
    try:
        # Check if nvidia-container-runtime is available
        result = subprocess.run(
            ["docker", "info", "--format", "{{.Runtimes}}"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and "nvidia" in result.stdout.lower():
            # GPU runtime available, enable GPU access
            docker_args.extend(["--gpus", "all"])  # Enable all GPUs
            print("GPU support enabled (VRAM limit should be configured at Docker daemon level)")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        # GPU not available or nvidia-container-runtime not installed, continue without GPU
        print("GPU not available or not configured, running without GPU")
    
    docker_args.append(image_name)
    
    # Run the container
    docker_command(*docker_args)
    
    print(f"Container {container_name} is running on port {port}")
    
    # Wait for the API to be ready
    print("Waiting for API to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                print("API is ready!")
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"Still waiting... ({i}/{max_retries})")
    
    raise TimeoutError("API did not become ready in time")


def call_verify_api(statement: str, statement_id: str = None, timeout_seconds: int = 300):
    """Call the /verify endpoint with a statement."""
    if statement_id is None:
        statement_id = f"stmt_{hash(statement) % 10000}"
    
    payload = {
        "statement": statement,
        "statement_id": statement_id,
        "timeout_seconds": timeout_seconds
    }
    
    try:
        response = requests.post(
            f"{API_URL}/verify",
            json=payload,
            timeout=timeout_seconds + 10  # Add buffer for network overhead
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        raise


async def run_miner_agent(uid: int, statements: list[str] = None):
    """
    Pull agent from blockchain, build Docker image, run container, and call API with statements.
    
    Args:
        uid: The UID of the agent to pull from blockchain
        statements: List of statements to verify (defaults to test statements)
    """
    if statements is None:
        statements = [
            "The sky is blue",
            "Water boils at 100 degrees Celsius",
            "The Earth is flat",
            "Python is a programming language",
            "2 + 2 = 5"
        ]
    
    print(f"Pulling agent for UID {uid} from blockchain (NETUID {NETUID})...")
    
    # Step 1: Pull agent code from blockchain
    agent_dir = await pull_agent(uid)
    if not agent_dir:
        print(f"Failed to pull agent for UID {uid}")
        return
    
    print(f"Agent code pulled to: {agent_dir}")
    
    # Check if Dockerfile exists in the pulled directory
    agent_path = Path(agent_dir)
    dockerfile_path = agent_path / "Dockerfile"
    
    if not dockerfile_path.exists():
        print(f"Warning: No Dockerfile found in {agent_dir}")
        print("Looking for Dockerfile in pulled files...")
        # Try to find any Dockerfile
        dockerfiles = list(agent_path.rglob("Dockerfile"))
        if dockerfiles:
            dockerfile_path = dockerfiles[0]
            agent_path = dockerfile_path.parent
            print(f"Found Dockerfile at: {dockerfile_path}")
        else:
            raise FileNotFoundError(f"No Dockerfile found in pulled agent directory: {agent_dir}")
    
    # Generate unique image and container names based on UID
    image_name = f"{DOCKER_IMAGE_NAME_PREFIX}-uid{uid}"
    container_name = f"{DOCKER_CONTAINER_NAME_PREFIX}-uid{uid}"
    
    try:
        # Step 2: Build Docker image from pulled directory
        build_docker_image(image_name, agent_path)
        
        # Step 3: Run Docker container
        run_docker_container(image_name, container_name, API_PORT)
        
        # Step 4: Call API with statements
        print(f"\nCalling API with {len(statements)} statement(s)...")
        results = []
        
        for i, statement in enumerate(statements, 1):
            print(f"\n[{i}/{len(statements)}] Verifying: '{statement}'")
            try:
                statement_id = f"test_{i}_{int(time.time())}"
                result = call_verify_api(statement, statement_id=statement_id)
                results.append(result)
                print(f"  Statement ID: {result.get('statement_id')}")
                print(f"  Overall Verdict: {result.get('overall_verdict')}")
                print(f"  Overall Score: {result.get('overall_score')}")
                print(f"  Evidence Count: {len(result.get('evidence', []))}")
                print(f"  Processing Time: {result.get('response_metadata', {}).get('processing_time_seconds', 'N/A')}s")
            except Exception as e:
                print(f"  Error: {e}")
                results.append(None)
        
        print(f"\nCompleted {len([r for r in results if r is not None])}/{len(statements)} verifications")
        
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Clean up: stop and remove container
        print(f"\nCleaning up container...")
        stop_and_remove_container(container_name)


def main():
    """Main entry point - can be called with UID as command line argument."""
    import sys
    
    # Get UID from command line
    if len(sys.argv) > 1:
        try:
            uid = int(sys.argv[1])
        except ValueError:
            print(f"Invalid UID: {sys.argv[1]}. Must be an integer.")
            return
    else:
        print("No UID provided. Usage: python run.py <uid> [statements...]")
        print("Example: python run.py 0")
        print("Example: python run.py 0 'The sky is blue' 'Water boils at 100'")
        return
    
    # Optional: Get statements from command line
    statements = None
    if len(sys.argv) > 2:
        statements = sys.argv[2:]
    
    # Run the miner agent
    asyncio.run(run_miner_agent(uid, statements))


if __name__ == "__main__":
    main()
