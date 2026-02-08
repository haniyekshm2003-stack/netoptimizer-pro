#!/usr/bin/env python3
"""
🌐 DNS Analyzer Module
======================
Advanced DNS testing, benchmarking, and analysis.
"""

import asyncio
import time
import socket
import struct
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

DNS_SERVERS = {
    "Cloudflare": {"primary": "1.1.1.1", "secondary": "1.0.0.1", "category": "public", "privacy": "high", "features": ["DoH", "DoT", "DNSSEC"]},
    "Google": {"primary": "8.8.8.8", "secondary": "8.8.4.4", "category": "public", "privacy": "medium", "features": ["DoH", "DoT", "DNSSEC"]},
    "Quad9": {"primary": "9.9.9.9", "secondary": "149.112.112.112", "category": "security", "privacy": "high", "features": ["DoH", "DoT", "DNSSEC", "Malware Blocking"]},
    "OpenDNS": {"primary": "208.67.222.222", "secondary": "208.67.220.220", "category": "public", "privacy": "medium", "features": ["DNSSEC", "Content Filtering"]},
    "Cloudflare Malware": {"primary": "1.1.1.2", "secondary": "1.0.0.2", "category": "security", "privacy": "high", "features": ["DoH", "DoT", "Malware Blocking"]},
    "Cloudflare Family": {"primary": "1.1.1.3", "secondary": "1.0.0.3", "category": "family", "privacy": "high", "features": ["DoH", "DoT", "Adult Content Blocking"]},
    "AdGuard": {"primary": "94.140.14.14", "secondary": "94.140.15.15", "category": "adblock", "privacy": "high", "features": ["DoH", "DoT", "Ad Blocking"]},
    "AdGuard Family": {"primary": "94.140.14.15", "secondary": "94.140.15.16", "category": "family", "privacy": "high", "features": ["DoH", "DoT", "Ad + Adult Blocking"]},
    "CleanBrowsing Security": {"primary": "185.228.168.9", "secondary": "185.228.169.9", "category": "security", "privacy": "high", "features": ["DoH", "DoT", "Malware Blocking"]},
    "CleanBrowsing Family": {"primary": "185.228.168.168", "secondary": "185.228.169.168", "category": "family", "privacy": "high", "features": ["DoH", "DoT", "Adult + Malware Blocking"]},
    "NextDNS": {"primary": "45.90.28.0", "secondary": "45.90.30.0", "category": "privacy", "privacy": "high", "features": ["DoH", "DoT", "Customizable"]},
    "Control D": {"primary": "76.76.2.0", "secondary": "76.76.10.0", "category": "privacy", "privacy": "high", "features": ["DoH", "DoT", "Customizable"]},
}

TEST_DOMAINS = ["google.com", "cloudflare.com", "github.com", "microsoft.com", "apple.com", "amazon.com", "facebook.com", "twitter.com", "netflix.com", "youtube.com"]


class DNSAnalyzer:
    """Advanced DNS analyzer and benchmarker"""

    def __init__(self):
        self.timeout = 5.0
        self.results_cache = {}

    def get_dns_list(self) -> Dict[str, Any]:
        return DNS_SERVERS

    async def test_dns_server(self, dns_server: str, domain: str, timeout: float = 5.0) -> Dict[str, Any]:
        try:
            start = time.perf_counter()
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: self._resolve_dns(dns_server, domain)),
                timeout=timeout,
            )
            end = time.perf_counter()
            response_time = (end - start) * 1000
            return {
                "success": result["success"],
                "response_time_ms": round(response_time, 2),
                "resolved_ip": result.get("ip", ""),
                "error": result.get("error", None),
            }
        except asyncio.TimeoutError:
            return {"success": False, "response_time_ms": timeout * 1000, "resolved_ip": "", "error": "Timeout"}
        except Exception as e:
            return {"success": False, "response_time_ms": 0, "resolved_ip": "", "error": str(e)}

    def _resolve_dns(self, dns_server: str, domain: str) -> Dict[str, Any]:
        import random
        try:
            transaction_id = random.randint(0, 65535)
            flags = 0x0100
            questions = 1
            header = struct.pack(">HHHHHH", transaction_id, flags, questions, 0, 0, 0)

            question = b""
            for part in domain.split("."):
                question += bytes([len(part)]) + part.encode()
            question += b"\x00"
            question += struct.pack(">HH", 1, 1)

            query = header + question

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(query, (dns_server, 53))
            response, _ = sock.recvfrom(1024)
            sock.close()

            ip = self._parse_dns_response(response)
            return {"success": True, "ip": ip}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_dns_response(self, response: bytes) -> str:
        pos = 12
        while response[pos] != 0:
            pos += 1
        pos += 5

        while pos < len(response):
            if response[pos] >= 192:
                pos += 2
            else:
                while response[pos] != 0:
                    pos += 1
                pos += 1

            rtype = struct.unpack(">H", response[pos:pos + 2])[0]
            pos += 8
            rdlength = struct.unpack(">H", response[pos:pos + 2])[0]
            pos += 2

            if rtype == 1 and rdlength == 4:
                ip = ".".join(str(b) for b in response[pos:pos + 4])
                return ip
            pos += rdlength
        return ""

    async def benchmark(self, custom_servers: List[str] = None, test_domains: List[str] = None, iterations: int = 3) -> Dict[str, Any]:
        domains = test_domains or TEST_DOMAINS[:5]
        results = {}

        servers_to_test = {}
        for name, info in DNS_SERVERS.items():
            servers_to_test[name] = info["primary"]

        if custom_servers:
            for i, server in enumerate(custom_servers):
                servers_to_test[f"Custom_{i + 1}"] = server

        logger.info(f"Benchmarking {len(servers_to_test)} DNS servers...")

        for server_name, server_ip in servers_to_test.items():
            server_results = {
                "ip": server_ip,
                "tests": [],
                "avg_response_time": 0,
                "success_rate": 0,
                "min_time": float("inf"),
                "max_time": 0,
                "reliability_score": 0,
            }

            all_times = []
            successful = 0

            for domain in domains:
                for _ in range(iterations):
                    result = await self.test_dns_server(server_ip, domain)
                    server_results["tests"].append({"domain": domain, **result})

                    if result["success"]:
                        successful += 1
                        time_ms = result["response_time_ms"]
                        all_times.append(time_ms)
                        server_results["min_time"] = min(server_results["min_time"], time_ms)
                        server_results["max_time"] = max(server_results["max_time"], time_ms)

            total_tests = len(domains) * iterations
            server_results["success_rate"] = round((successful / total_tests) * 100, 2)

            if all_times:
                server_results["avg_response_time"] = round(sum(all_times) / len(all_times), 2)
                server_results["min_time"] = round(server_results["min_time"], 2)
                server_results["max_time"] = round(server_results["max_time"], 2)
            else:
                server_results["min_time"] = 0

            server_results["reliability_score"] = self._calculate_reliability(
                server_results["avg_response_time"], server_results["success_rate"]
            )

            if server_name in DNS_SERVERS:
                server_results["category"] = DNS_SERVERS[server_name]["category"]
                server_results["privacy"] = DNS_SERVERS[server_name]["privacy"]
                server_results["features"] = DNS_SERVERS[server_name]["features"]

            results[server_name] = server_results

        sorted_results = dict(sorted(results.items(), key=lambda x: x[1]["reliability_score"], reverse=True))
        best_server = list(sorted_results.keys())[0] if sorted_results else None

        return {
            "servers": sorted_results,
            "best_server": {"name": best_server, **sorted_results.get(best_server, {})} if best_server else None,
            "total_tested": len(sorted_results),
            "test_domains": domains,
            "iterations": iterations,
        }

    def _calculate_reliability(self, avg_time: float, success_rate: float) -> int:
        if success_rate == 0:
            return 0

        if avg_time <= 10:
            time_score = 100
        elif avg_time <= 25:
            time_score = 90
        elif avg_time <= 50:
            time_score = 75
        elif avg_time <= 100:
            time_score = 60
        elif avg_time <= 200:
            time_score = 40
        else:
            time_score = 20

        return int(success_rate * 0.6 + time_score * 0.4)

    async def benchmark_all(self) -> Dict[str, Any]:
        return await self.benchmark()

    async def get_recommendations(self) -> Dict[str, Any]:
        results = await self.benchmark(iterations=2)
        servers = results["servers"]

        recommendations = {
            "best_overall": None,
            "best_for_speed": None,
            "best_for_privacy": None,
            "best_for_security": None,
            "best_for_family": None,
            "top_5": [],
        }

        by_speed = sorted(servers.items(), key=lambda x: x[1]["avg_response_time"] if x[1]["avg_response_time"] > 0 else float("inf"))
        by_reliability = sorted(servers.items(), key=lambda x: x[1]["reliability_score"], reverse=True)

        if by_reliability:
            name, data = by_reliability[0]
            recommendations["best_overall"] = {"name": name, **data}

        if by_speed:
            name, data = by_speed[0]
            recommendations["best_for_speed"] = {"name": name, **data}

        privacy_servers = [(n, d) for n, d in servers.items() if d.get("privacy") == "high"]
        if privacy_servers:
            privacy_sorted = sorted(privacy_servers, key=lambda x: x[1]["reliability_score"], reverse=True)
            name, data = privacy_sorted[0]
            recommendations["best_for_privacy"] = {"name": name, **data}

        security_servers = [(n, d) for n, d in servers.items() if d.get("category") == "security"]
        if security_servers:
            security_sorted = sorted(security_servers, key=lambda x: x[1]["reliability_score"], reverse=True)
            name, data = security_sorted[0]
            recommendations["best_for_security"] = {"name": name, **data}

        family_servers = [(n, d) for n, d in servers.items() if d.get("category") == "family"]
        if family_servers:
            family_sorted = sorted(family_servers, key=lambda x: x[1]["reliability_score"], reverse=True)
            name, data = family_sorted[0]
            recommendations["best_for_family"] = {"name": name, **data}

        recommendations["top_5"] = [{"name": name, **data} for name, data in by_reliability[:5]]

        return recommendations
