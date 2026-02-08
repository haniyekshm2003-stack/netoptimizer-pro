#!/usr/bin/env python3
"""
🌍 Global Ping Module
=====================
Tests latency to global endpoints and cloud regions.
"""

import asyncio
import time
import socket
from typing import Dict, List, Any
import aiohttp
import logging

logger = logging.getLogger(__name__)

GLOBAL_ENDPOINTS = {
    "US East (Virginia)": {
        "host": "ec2.us-east-1.amazonaws.com",
        "region": "us-east-1",
        "provider": "AWS",
        "location": "Virginia, USA"
    },
    "US West (Oregon)": {
        "host": "ec2.us-west-2.amazonaws.com",
        "region": "us-west-2",
        "provider": "AWS",
        "location": "Oregon, USA"
    },
    "US West (California)": {
        "host": "ec2.us-west-1.amazonaws.com",
        "region": "us-west-1",
        "provider": "AWS",
        "location": "California, USA"
    },
    "Europe (Frankfurt)": {
        "host": "ec2.eu-central-1.amazonaws.com",
        "region": "eu-central-1",
        "provider": "AWS",
        "location": "Frankfurt, Germany"
    },
    "Europe (Ireland)": {
        "host": "ec2.eu-west-1.amazonaws.com",
        "region": "eu-west-1",
        "provider": "AWS",
        "location": "Dublin, Ireland"
    },
    "Europe (London)": {
        "host": "ec2.eu-west-2.amazonaws.com",
        "region": "eu-west-2",
        "provider": "AWS",
        "location": "London, UK"
    },
    "Asia Pacific (Singapore)": {
        "host": "ec2.ap-southeast-1.amazonaws.com",
        "region": "ap-southeast-1",
        "provider": "AWS",
        "location": "Singapore"
    },
    "Asia Pacific (Tokyo)": {
        "host": "ec2.ap-northeast-1.amazonaws.com",
        "region": "ap-northeast-1",
        "provider": "AWS",
        "location": "Tokyo, Japan"
    },
    "Asia Pacific (Sydney)": {
        "host": "ec2.ap-southeast-2.amazonaws.com",
        "region": "ap-southeast-2",
        "provider": "AWS",
        "location": "Sydney, Australia"
    },
    "Asia Pacific (Mumbai)": {
        "host": "ec2.ap-south-1.amazonaws.com",
        "region": "ap-south-1",
        "provider": "AWS",
        "location": "Mumbai, India"
    },
    "Asia Pacific (Seoul)": {
        "host": "ec2.ap-northeast-2.amazonaws.com",
        "region": "ap-northeast-2",
        "provider": "AWS",
        "location": "Seoul, South Korea"
    },
    "South America (São Paulo)": {
        "host": "ec2.sa-east-1.amazonaws.com",
        "region": "sa-east-1",
        "provider": "AWS",
        "location": "São Paulo, Brazil"
    },
    "Middle East (Bahrain)": {
        "host": "ec2.me-south-1.amazonaws.com",
        "region": "me-south-1",
        "provider": "AWS",
        "location": "Bahrain"
    },
    "Canada (Montreal)": {
        "host": "ec2.ca-central-1.amazonaws.com",
        "region": "ca-central-1",
        "provider": "AWS",
        "location": "Montreal, Canada"
    },
    "Cloudflare": {
        "host": "1.1.1.1",
        "region": "global",
        "provider": "Cloudflare",
        "location": "Global CDN"
    },
    "Google DNS": {
        "host": "8.8.8.8",
        "region": "global",
        "provider": "Google",
        "location": "Global Network"
    },
    "Microsoft Azure": {
        "host": "azure.microsoft.com",
        "region": "global",
        "provider": "Microsoft",
        "location": "Global Network"
    },
    "Google Cloud": {
        "host": "cloud.google.com",
        "region": "global",
        "provider": "Google",
        "location": "Global Network"
    }
}


class GlobalPingTester:
    """Global ping and latency tester"""

    def __init__(self):
        self.timeout = 10.0
        self.iterations = 3

    def get_regions(self) -> Dict[str, Any]:
        """Get available regions"""
        return GLOBAL_ENDPOINTS

    async def ping_host(self, host: str, timeout: float = None) -> Dict[str, Any]:
        """Ping a host using TCP connection"""
        timeout = timeout or self.timeout

        try:
            # Resolve hostname first
            try:
                ip = socket.gethostbyname(host)
            except socket.gaierror:
                ip = host

            start = time.perf_counter()

            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, 443),
                timeout=timeout
            )

            end = time.perf_counter()

            writer.close()
            await writer.wait_closed()

            return {
                "success": True,
                "host": host,
                "ip": ip,
                "latency_ms": round((end - start) * 1000, 2),
                "error": None
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "host": host,
                "latency_ms": timeout * 1000,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "host": host,
                "latency_ms": 0,
                "error": str(e)
            }

    async def test_region(self, region_name: str, iterations: int = None) -> Dict[str, Any]:
        """Test a specific region"""
        iterations = iterations or self.iterations

        if region_name not in GLOBAL_ENDPOINTS:
            return {
                "success": False,
                "region": region_name,
                "error": "Region not found"
            }

        endpoint = GLOBAL_ENDPOINTS[region_name]
        host = endpoint["host"]

        results = []
        latencies = []

        for _ in range(iterations):
            result = await self.ping_host(host)
            results.append(result)

            if result["success"]:
                latencies.append(result["latency_ms"])

        if latencies:
            avg_latency = round(sum(latencies) / len(latencies), 2)
            min_latency = round(min(latencies), 2)
            max_latency = round(max(latencies), 2)
            jitter = round(max_latency - min_latency, 2)
        else:
            avg_latency = min_latency = max_latency = jitter = 0

        return {
            "success": len(latencies) > 0,
            "region": region_name,
            "host": host,
            "provider": endpoint["provider"],
            "location": endpoint["location"],
            "cloud_region": endpoint.get("region"),
            "tests": results,
            "avg_latency_ms": avg_latency,
            "min_latency_ms": min_latency,
            "max_latency_ms": max_latency,
            "jitter_ms": jitter,
            "success_rate": round((len(latencies) / iterations) * 100, 2)
        }

    async def test_all_regions(self, iterations: int = None) -> Dict[str, Any]:
        """Test all regions"""
        iterations = iterations or self.iterations

        results = {}

        for region_name in GLOBAL_ENDPOINTS.keys():
            result = await self.test_region(region_name, iterations)
            results[region_name] = result

        sorted_results = dict(sorted(
            results.items(),
            key=lambda x: x[1]["avg_latency_ms"] if x[1]["avg_latency_ms"] > 0 else float("inf")
        ))

        fastest = list(sorted_results.keys())[0] if sorted_results else None

        return {
            "regions": sorted_results,
            "fastest_region": {
                "name": fastest,
                **sorted_results.get(fastest, {})
            } if fastest else None,
            "total_tested": len(sorted_results),
            "iterations": iterations
        }

    async def get_best_location(self) -> Dict[str, Any]:
        """Get the best location for deployment"""
        results = await self.test_all_regions(iterations=2)
        regions = results["regions"]

        by_provider = {}
        for name, data in regions.items():
            provider = data.get("provider", "Unknown")
            if provider not in by_provider:
                by_provider[provider] = []
            by_provider[provider].append({"name": name, **data})

        for provider in by_provider:
            by_provider[provider].sort(
                key=lambda x: x["avg_latency_ms"] if x["avg_latency_ms"] > 0 else float("inf")
            )

        recommendations = {
            "best_overall": results["fastest_region"],
            "best_by_provider": {
                provider: regions[0] if regions else None
                for provider, regions in by_provider.items()
            },
            "top_5": [
                {"name": name, **data}
                for name, data in list(regions.items())[:5]
            ]
        }

        return recommendations

    async def test_custom_endpoint(self, host: str, iterations: int = 3) -> Dict[str, Any]:
        """Test a custom endpoint"""
        results = []
        latencies = []

        for _ in range(iterations):
            result = await self.ping_host(host)
            results.append(result)

            if result["success"]:
                latencies.append(result["latency_ms"])

        if latencies:
            return {
                "success": True,
                "host": host,
                "tests": results,
                "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
                "min_latency_ms": round(min(latencies), 2),
                "max_latency_ms": round(max(latencies), 2),
                "success_rate": round((len(latencies) / iterations) * 100, 2)
            }
        else:
            return {
                "success": False,
                "host": host,
                "tests": results,
                "error": "All tests failed"
            }
