import subprocess
import tempfile
import os

class LXDExecutor:
    def __init__(self, base_image="ubuntu:22.04"):
        self.base_image = base_image
    
    def is_lxd_ready(self):
        """Check if LXD is installed and initialized."""
        try:
            subprocess.run(["lxc", "list"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def execute_in_container(self, script):
        """Execute script in disposable LXD container."""
        import sys
        
        if not self.is_lxd_ready():
            raise RuntimeError("LXD not ready. Run: sudo lxd init --auto")
        
        container_name = f"agentshell-{os.urandom(4).hex()}"
        
        try:
            # Launch container
            print(f"  → Launching container {container_name}...", flush=True)
            subprocess.run(
                ["lxc", "launch", self.base_image, container_name],
                check=True,
                capture_output=True
            )
            
            # Wait for container to be ready
            print("  → Waiting for container to be ready...", flush=True)
            subprocess.run(
                ["lxc", "exec", container_name, "--", "cloud-init", "status", "--wait"],
                check=True,
                capture_output=True,
                timeout=60
            )
            
            # Write script to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script)
                script_path = f.name
            
            try:
                # Push script to container
                print("  → Uploading script...", flush=True)
                subprocess.run(
                    ["lxc", "file", "push", script_path, f"{container_name}/tmp/script.sh"],
                    check=True
                )
                
                # Make executable and run
                print("  → Running script...", flush=True)
                result = subprocess.run(
                    ["lxc", "exec", container_name, "--", "bash", "/tmp/script.sh"],
                    capture_output=True,
                    text=True
                )
                
                return {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            finally:
                os.unlink(script_path)
        
        finally:
            # Always cleanup container
            print("  → Cleaning up container...", flush=True)
            subprocess.run(
                ["lxc", "delete", "-f", container_name],
                capture_output=True
            )
    
    def execute_on_host(self, script):
        """Execute script on host (only if all commands are safe)."""
        from agentshell.main import is_script_safe
        
        safe, message = is_script_safe(script)
        if not safe:
            raise RuntimeError(f"{message}. Use --run-container instead.")
        
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True
        )
        
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
