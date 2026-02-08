#!/usr/bin/env python3
"""
🔍 Port Scanner Module
======================
Advanced port scanning for network analysis.
"""

import asyncio
import socket
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

COMMON_PORTS = {
    20: {"service": "FTP Data", "category": "file_transfer"},
    21: {"service": "FTP Control", "category": "file_transfer"},
    22: {"service": "SSH", "category": "remote_access"},
    23: {"service": "Telnet", "category": "remote_access"},
    25: {"service": "SMTP", "category": "email"},
    53: {"service": "DNS", "category": "network"},
    80: {"service": "HTTP", "category": "web"},
    110: {"service": "POP3", "category": "email"},
    143: {"service": "IMAP", "category": "email"},
    443: {"service": "HTTPS", "category": "web"},
    445: {"service": "SMB", "category": "file_transfer"},
    465: {"service": "SMTPS", "category": "email"},
    587: {"service": "SMTP Submission", "category": "email"},
    993: {"service": "IMAPS", "category": "email"},
    995: {"service": "POP3S", "category": "email"},
    1433: {"service": "MSSQL", "category": "database"},
    3306: {"service": "MySQL", "category": "database"},
    3389: {"service": "RDP", "category": "remote_access"},
    5432: {"service": "PostgreSQL", "category": "database"},
    5900: {"service": "VNC", "category": "remote_access"},
    6379: {"service": "Redis", "category": "database"},
    8080: {"service": "HTTP Proxy", "category": "web"},
    8443: {"service": "HTTPS Alt", "category": "web"},
    27017: {"service": "MongoDB", "category": "database"},
}

VPN_PORTS = {
    500: {"service": "IKE", "protocol": "IPSec", "category": "vpn"},
    1194: {"service": "OpenVPN", "protocol": "OpenVPN", "category": "vpn"},
    1701: {"service": "L2TP", "protocol": "L2TP", "category": "vpn"},
    1723: {"service": "PPTP", "protocol": "PPTP", "category": "vpn"},
    4500: {"service": "IPSec NAT-T", "protocol": "IPSec", "category": "vpn"},
    51820: {"service": "WireGuard", "protocol": "WireGuard", "category": "vpn"},
    443: {"service": "HTTPS/SSL VPN", "protocol": "SSL VPN", "category": "vpn"},
    8443: {"service": "AnyConnect", "protocol": "Cisco AnyConnect", "category": "vpn"},
    10443: {"service": "V2Ray", "protocol": "V2Ray", "category": "vpn"},
    2083: {"service": "V2Ray/Xray", "protocol": "V2Ray", "category": "vpn"},
    2087: {"service": "Trojan", "protocol": "Trojan", "category": "vpn"},
    8388: {"service": "Shadowsocks", "protocol": "Shadowsocks", "category": "vpn"},
}


class PortScanner:
    """Advanced port scanner with service detection"""

    def __init__(self):
        self.timeout = 3.0
        self.concurrent_limit = 100
        self.all_ports = {**COMMON_PORTS, **VPN_PORTS}

    def get_port_info(self) -> Dict[str, Any]:
        """Get port database"""
        return {
            "common_ports": COMMON_PORTS,
            "vpn_ports": VPN_PORTS,
            "total_ports": len(self.all_ports)
        }

    async def scan_port(self, host: str, port: int, timeout: float = None) -> Dict[str, Any]:
        """Scan a single port"""
        timeout = timeout or self.timeout

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout
            )
            writer.close()
            await writer.wait_closed()

            port_info = self.all_ports.get(port, {})

            return {
                "port": port,
                "status": "open",
                "service": port_info.get("service", "Unknown"),
                "category": port_info.get("category", "unknown"),
                "protocol": port_info.get("protocol"),
                "error": None
            }
        except asyncio.TimeoutError:
            return {
                "port": port,
                "status": "filtered",
                "service": None,
                "category": None,
                "error": "Timeout"
            }
        except ConnectionRefusedError:
            return {
                "port": port,
                "status": "closed",
                "service": None,
                "category": None,
                "error": "Connection refused"
            }
        except Exception as e:
            return {
                "port": port,
                "status": "error",
                "service": None,
                "category": None,
                "error": str(e)
            }

    async def scan_ports(self, host: str, ports: List[int] = None, scan_type: str = "common") -> Dict[str, Any]:
        """Scan multiple ports"""
        if ports:
            target_ports = ports
        elif scan_type == "vpn":
            target_ports = list(VPN_PORTS.keys())
        elif scan_type == "all":
            target_ports = list(self.all_ports.keys())
        else:  # common
            target_ports = list(COMMON_PORTS.keys())

        results = {
            "host": host,
            "scan_type": scan_type,
            "ports_scanned": len(target_ports),
            "open_ports": [],
            "closed_ports": [],
            "filtered_ports": [],
            "results": [],
            "summary": {}
        }

        # Scan with concurrency limit
        semaphore = asyncio.Semaphore(self.concurrent_limit)

        async def scan_with_limit(port):
            async with semaphore:
                return await self.scan_port(host, port)

        tasks = [scan_with_limit(port) for port in target_ports]
        scan_results = await asyncio.gather(*tasks)

        for result in scan_results:
            results["results"].append(result)

            if result["status"] == "open":
                results["open_ports"].append(result)
            elif result["status"] == "closed":
                results["closed_ports"].append(result)
            elif result["status"] == "filtered":
                results["filtered_ports"].append(result)

        results["summary"] = {
            "total_scanned": len(target_ports),
            "open": len(results["open_ports"]),
            "closed": len(results["closed_ports"]),
            "filtered": len(results["filtered_ports"]),
            "open_percentage": round((len(results["open_ports"]) / len(target_ports)) * 100, 2)
        }

        return results

    async def scan_common(self, host: str) -> Dict[str, Any]:
        """Scan common ports"""
        return await self.scan_ports(host, scan_type="common")

    async def scan_vpn(self, host: str) -> Dict[str, Any]:
        """Scan VPN-related ports"""
        return await self.scan_ports(host, scan_type="vpn")

    async def scan_range(self, host: str, start_port: int, end_port: int) -> Dict[str, Any]:
        """Scan a range of ports"""
        ports = list(range(start_port, end_port + 1))
        return await self.scan_ports(host, ports=ports)

    async def quick_scan(self, host: str) -> Dict[str, Any]:
        """Quick scan of most important ports"""
        important_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080]
        return await self.scan_ports(host, ports=important_ports)

    async def get_open_services(self, host: str) -> Dict[str, Any]:
        """Get all open services categorized"""
        results = await self.scan_ports(host, scan_type="all")

        open_by_category = {}
        for port_result in results["open_ports"]:
            category = port_result.get("category", "unknown")
            if category not in open_by_category:
                open_by_category[category] = []
            open_by_category[category].append(port_result)

        return {
            "host": host,
            "open_services": results["open_ports"],
            "by_category": open_by_category,
            "total_open": len(results["open_ports"])
        }

    async def check_vpn_connectivity(self, host: str) -> Dict[str, Any]:
        """Check VPN protocol availability"""
        results = await self.scan_vpn(host)

        vpn_status = {}
        for port_result in results["results"]:
            if port_result["port"] in VPN_PORTS:
                protocol = VPN_PORTS[port_result["port"]].get("protocol", "Unknown")
                vpn_status[protocol] = {
                    "port": port_result["port"],
                    "status": port_result["status"],
                    "available": port_result["status"] == "open"
                }

        available_protocols = [p for p, v in vpn_status.items() if v["available"]]

        return {
            "host": host,
            "vpn_protocols": vpn_status,
            "available_protocols": available_protocols,
            "total_available": len(available_protocols)
        }
