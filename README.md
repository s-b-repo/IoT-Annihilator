🚀 IoT Annihilator 🔥

⚠️ WARNING: This tool is powerful, relentless, and engineered to expose the soft underbelly of vulnerable IoT devices. Use it responsibly and with extreme caution. Unauthorized use is illegal and will get you in a lot more than trouble. This project was created for ethical research, penetration testing, and fortifying defenses against the inevitable cyber onslaught. If you misuse it, you’re on your own.

⚙️ About

IoT Annihilator is an automated, multi-vector exploitation framework designed to systematically obliterate vulnerabilities in IoT devices. By leveraging an arsenal of pre-configured attacks using Kali Linux's most notorious tools, this script scours for outdated, poorly secured devices and tries every trick in the book. Think of it as a wake-up call for devices that have been left behind.

    Real-World Disclaimer: This tool is not a toy. It’s a full-throttle beast intended to be used by seasoned penetration testers, cybersecurity researchers, and system hardeners. Think twice and use this knowledge responsibly.

💀 Features

    Nmap Service Detection: Finds and tags open ports and protocols on target devices.
    Brute Force with Hydra: Brutally efficient at cracking passwords for vulnerable SSH services.
    Metasploit HTTP Exploits: Takes aim at weak HTTP implementations and preys on unpatched versions.
    RouterSploit Autopwn: Fully automated vulnerability discovery and exploitation for IoT devices.
    Outdated Service Detection: Discovers vulnerable services and saves them separately for deeper analysis.

🚨 Note

The tool is crafted with power and precision; the intent is to identify weaknesses, not to destroy. Use it as a shield, not a sword.
⚡ Requirements

    Kali Linux with tools like nmap, hydra, metasploit, and routersploit installed.
    A text file, ips.txt, listing the target IPs.
    Python 3 and administrator privileges (recommended to run with sudo).

🔥 How to Run

    Clone the repo:

    

git clone https://github.com/s-b-repo/IoT-Annihilator.git
cd IoT-Annihilator

Add Target IPs: Populate ips.txt with the IPs you want to scan and target. No mercy.

Execute:

    sudo python3 fiot.py

    Results:
        exploit_results.json: Full report on the carnage.
        outdated_services.json: IPs with outdated services — your new target list.

⚔️ Fight the evil Fight

The IoT landscape is a vast, uncharted wilderness with countless weak links. Use IoT Annihilator to bring vulnerabilities to light and secure the networks of tomorrow. Misuse this power, and it will come back to haunt you.
Don’t say we didn’t warn you.
📜 Legal Disclaimer

This project is made for educational and ethical purposes only. Unauthorized testing or hacking of any network, device, or application is illegal and can result in severe consequences. Use it only with explicit permission from the owner or in a controlled environment.

Stay edgy, stay un-ethical. 🕶️
