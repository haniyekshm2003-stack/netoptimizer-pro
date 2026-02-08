#!/usr/bin/env python3
"""
🌐 Protocol Benchmark Module
============================
Tests various network protocols for performance.
"""

import asyncio
import time
import socket
import ssl
from typing import Dict, List, Any
import aiohttp
import logging

logger = logging.getLogger(__name__)

PROTOCOL_TESTS = {
    "HTTP": {
        "description": "Standard HTTP (unencrypted)",
        "port": 80,
        "secure": False
    },
    "HTTPS": {
        "description": "HTTP over TLS",
        "port": 443,
        "secure": True
    },
    "HTTP/2": {
        "description": "HTTP/2 protocol",
        "port": 443,
        "secure": True
    },
    "TLS 1.2": {
        "description": "TLS 1.2 encryption",
        "port": 443,
        "secure": True
    },
    "TLS 1.3": {
        "description": "TLS 1.3 encryption",
        "port": 443,
        "secure": True
    }
}


class ProtocolBenchmark:
    """Protocol performance benchmarking"""

    def __init__(self):
        self.timeout = 10.0
        self.test_targets = [
            "www.google.com",
            "www.cloudflare.com",
            "www.github.com",
            "www.microsoft.com"
        ]

    async def test_http(self, host: str) -> Dict[str, Any]:
        """Test HTTP connection"""
        try:
            start = time.perf_counter()

            async with aiohttp.ClientSession() as session:
                url = f"http://{host}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout), allow_redirects=False) as response:
                    end = time.perf_counter()

                    return {
                        "success": True,
                        "protocol": "HTTP/1.1",
                        "response_time_ms": round((end - start) * 1000, 2),
                        "status_code": response.status,
                        "redirected": response.status in [301, 302, 307, 308],
                        "error": None
                    }
        except Exception as e:
            return {
                "success": False,
                "protocol": "HTTP/1.1",
                "response_time_ms": 0,
                "status_code": 0,
                "error": str(e)
            }

    async def test_https(self, host: str) -> Dict[str, Any]:
        """Test HTTPS connection"""
        try:
            start = time.perf_counter()

            async with aiohttp.ClientSession() as session:
                url = f"https://{host}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    end = time.perf_counter()

                    return {
                        "success": True,
                        "protocol": "HTTPS",
                        "response_time_ms": round((end - start) * 1000, 2),
                        "status_code": response.status,
                        "error": None
                    }
        except Exception as e:
            return {
                "success": False,
                "protocol": "HTTPS",
                "response_time_ms": 0,
                "status_code": 0,
                "error": str(e)
            }

    async def test_tls_version(self, host: str, tls_version: str) -> Dict[str, Any]:
        """Test specific TLS version"""
        try:
            start = time.perf_counter()

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._sync_tls_test(host, tls_version)
            )

            end = time.perf_counter()

            if result["success"]:
                result["response_time_ms"] = round((end - start) * 1000, 2)

            return result
        except Exception as e:
            return {
                "success": False,
                "tls_version": tls_version,
                "response_time_ms": 0,
                "cipher": None,
                "error": str(e)
            }

    def _sync_tls_test(self, host: str, tls_version: str) -> Dict[str, Any]:
        """Synchronous TLS test"""
        try:
            context = ssl.create_default_context()

            if tls_version == "TLS 1.2":
                context.minimum_version = ssl.TLSVersion.TLSv1_2
                context.maximum_version = ssl.TLSVersion.TLSv1_2
            elif tls_version == "TLS 1.3":
                context.minimum_version = ssl.TLSVersion.TLSv1_3
                context.maximum_version = ssl.TLSVersion.TLSv1_3

            with socket.create_connection((host, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cipher = ssock.cipher()
                    version = ssock.version()

                    return {
                        "success": True,
                        "tls_version": version,
                        "cipher": cipher[0] if cipher else None,
                        "cipher_bits": cipher[2] if cipher else None,
                        "error": None
                    }
        except ssl.SSLError as e:
            return {
                "success": False,
                "tls_version": tls_version,
                "cipher": None,
                "error": f"SSL Error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "tls_version": tls_version,
                "cipher": None,
                "error": str(e)
            }

    async def test_tcp_connection(self, host: str, port: int) -> Dict[str, Any]:
        """Test TCP connection time"""
        try:
            start = time.perf_counter()

            loop = asyncio.get_event_loop()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )

            end = time.perf_counter()
            writer.close()
            await writer.wait_closed()

            return {
                "success": True,
                "host": host,
                "port": port,
                "connection_time_ms": round((end - start) * 1000, 2),
                "error": None
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "host": host,
                "port": port,
                "connection_time_ms": self.timeout * 1000,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "host": host,
                "port": port,
                "connection_time_ms": 0,
                "error": str(e)
            }

    async def benchmark(self, targets: List[str] = None) -> Dict[str, Any]:
        """Run full protocol benchmark"""
        hosts = targets or self.test_targets
        results = {
            "http": [],
            "https": [],
            "tls_1_2": [],
            "tls_1_3": [],
            "tcp": [],
            "summary": {}
        }

        for host in hosts:
            http_result = await self.test_http(host)
            http_result["host"] = host
            results["http"].append(http_result)

            https_result = await self.test_https(host)
            https_result["host"] = host
            results["https"].append(https_result)

            tls12_result = await self.test_tls_version(host, "TLS 1.2")
            tls12_result["host"] = host
            results["tls_1_2"].append(tls12_result)

            tls13_result = await self.test_tls_version(host, "TLS 1.3")
            tls13_result["host"] = host
            results["tls_1_3"].append(tls13_result)

            tcp_result = await self.test_tcp_connection(host, 443)
            results["tcp"].append(tcp_result)

        results["summary"] = self._calculate_summary(results)

        return results

    def _calculate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate benchmark summary"""
        summary = {}

        for protocol, tests in results.items():
            if protocol == "summary" or not tests:
                continue

            successful = [t for t in tests if t.get("success")]
            if successful:
                times = [t.get("response_time_ms", t.get("connection_time_ms", 0)) for t in successful]
                summary[protocol] = {
                    "avg_time_ms": round(sum(times) / len(times), 2),
                    "min_time_ms": round(min(times), 2),
                    "max_time_ms": round(max(times), 2),
                    "success_rate": round((len(successful) / len(tests)) * 100, 2),
                    "tests_passed": len(successful),
                    "tests_total": len(tests)
                }
            else:
                summary[protocol] = {
                    "avg_time_ms": 0,
                    "success_rate": 0,
                    "tests_passed": 0,
                    "tests_total": len(tests)
                }

        return summary

    async def test_all(self) -> Dict[str, Any]:
        """Run all protocol tests"""
        return await self.benchmark()

    async def get_protocol_support(self, host: str) -> Dict[str, Any]:
        """Check which protocols a host supports"""
        support = {
            "host": host,
            "protocols": {}
        }

        http_result = await self.test_http(host)
        support["protocols"]["HTTP"] = {
            "supported": http_result["success"],
            "response_time_ms": http_result.get("response_time_ms", 0)
        }

        https_result = await self.test_https(host)
        support["protocols"]["HTTPS"] = {
            "supported": https_result["success"],
            "response_time_ms": https_result.get("response_time_ms", 0)
        }

        tls12 = await self.test_tls_version(host, "TLS 1.2")
        support["protocols"]["TLS 1.2"] = {
            "supported": tls12["success"],
            "cipher": tls12.get("cipher")
        }

        tls13 = await self.test_tls_version(host, "TLS 1.3")
        support["protocols"]["TLS 1.3"] = {
            "supported": tls13["success"],
            "cipher": tls13.get("cipher")
        }

        return support
