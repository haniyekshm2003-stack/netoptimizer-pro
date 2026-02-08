#!/usr/bin/env python3
"""
🌐 CDN Tester Module
====================
Tests CDN providers for performance and availability.
"""

import asyncio
import time
import aiohttp
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

CDN_PROVIDERS = {
    "Cloudflare": {
        "test_url": "https://www.cloudflare.com/cdn-cgi/trace",
        "description": "Global CDN with DDoS protection",
        "features": ["DDoS Protection", "WAF", "Edge Computing", "Free Tier"]
    },
    "Fastly": {
        "test_url": "https://www.fastly.com",
        "description": "Real-time CDN",
        "features": ["Edge Computing", "Real-time Logs", "Image Optimization"]
    },
    "Akamai": {
        "test_url": "https://www.akamai.com",
        "description": "Enterprise CDN",
        "features": ["Enterprise Security", "Media Delivery", "Edge Platform"]
    },
    "Amazon CloudFront": {
        "test_url": "https://d1.awsstatic.com/logos/aws-logo-lockups/poweredbyaws/PB_AWS_logo_RGB_REV_SQ.8c88ac215fe4e441dc42865dd6962ed4f444a90d.png",
        "description": "AWS CDN",
        "features": ["Lambda@Edge", "AWS Integration", "Global Network"]
    },
    "Google Cloud CDN": {
        "test_url": "https://www.gstatic.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
        "description": "GCP CDN",
        "features": ["GCP Integration", "Anycast", "HTTP/2"]
    },
    "Microsoft Azure CDN": {
        "test_url": "https://azure.microsoft.com/favicon.ico",
        "description": "Azure CDN",
        "features": ["Azure Integration", "Rules Engine", "Analytics"]
    },
    "BunnyCDN": {
        "test_url": "https://bunny.net",
        "description": "Affordable CDN",
        "features": ["Low Cost", "Storage", "Stream"]
    },
    "KeyCDN": {
        "test_url": "https://www.keycdn.com",
        "description": "Developer-friendly CDN",
        "features": ["HTTP/2", "Let's Encrypt", "Real-time Analytics"]
    },
    "StackPath": {
        "test_url": "https://www.stackpath.com",
        "description": "Edge computing CDN",
        "features": ["Edge Computing", "WAF", "DDoS"]
    },
    "Imperva (Incapsula)": {
        "test_url": "https://www.imperva.com",
        "description": "Security-focused CDN",
        "features": ["Bot Management", "WAF", "DDoS Protection"]
    },
    "jsDelivr": {
        "test_url": "https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js",
        "description": "Free CDN for open source",
        "features": ["npm/GitHub Integration", "Free", "Fast"]
    },
    "cdnjs": {
        "test_url": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js",
        "description": "Free library CDN",
        "features": ["Cloudflare Powered", "Free", "Libraries"]
    }
}


class CDNTester:
    """CDN Performance Tester"""

    def __init__(self):
        self.timeout = 10.0
        self.results_cache = {}

    def get_cdn_list(self) -> Dict[str, Any]:
        return CDN_PROVIDERS

    async def test_cdn(self, cdn_name: str, url: str) -> Dict[str, Any]:
        """Test a single CDN endpoint"""
        try:
            start = time.perf_counter()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    content = await response.read()
                    end = time.perf_counter()

                    response_time = (end - start) * 1000
                    headers = dict(response.headers)

                    cdn_header = None
                    for header in ["cf-ray", "x-cache", "x-cdn", "x-served-by", "x-amz-cf-id"]:
                        if header in headers:
                            cdn_header = f"{header}: {headers[header]}"
                            break

                    return {
                        "success": True,
                        "status_code": response.status,
                        "response_time_ms": round(response_time, 2),
                        "content_length": len(content),
                        "cdn_header": cdn_header,
                        "headers": {k: v for k, v in list(headers.items())[:10]},
                        "error": None
                    }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "status_code": 0,
                "response_time_ms": self.timeout * 1000,
                "content_length": 0,
                "cdn_header": None,
                "headers": {},
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "response_time_ms": 0,
                "content_length": 0,
                "cdn_header": None,
                "headers": {},
                "error": str(e)
            }

    async def benchmark(self, iterations: int = 3) -> Dict[str, Any]:
        """Benchmark all CDN providers"""
        results = {}

        for cdn_name, cdn_info in CDN_PROVIDERS.items():
            cdn_results = {
                "url": cdn_info["test_url"],
                "description": cdn_info["description"],
                "features": cdn_info["features"],
                "tests": [],
                "avg_response_time": 0,
                "min_time": float("inf"),
                "max_time": 0,
                "success_rate": 0,
                "score": 0
            }

            all_times = []
            successful = 0

            for _ in range(iterations):
                result = await self.test_cdn(cdn_name, cdn_info["test_url"])
                cdn_results["tests"].append(result)

                if result["success"] and result["status_code"] < 400:
                    successful += 1
                    time_ms = result["response_time_ms"]
                    all_times.append(time_ms)
                    cdn_results["min_time"] = min(cdn_results["min_time"], time_ms)
                    cdn_results["max_time"] = max(cdn_results["max_time"], time_ms)

            cdn_results["success_rate"] = round((successful / iterations) * 100, 2)

            if all_times:
                cdn_results["avg_response_time"] = round(sum(all_times) / len(all_times), 2)
                cdn_results["min_time"] = round(cdn_results["min_time"], 2)
                cdn_results["max_time"] = round(cdn_results["max_time"], 2)
            else:
                cdn_results["min_time"] = 0

            cdn_results["score"] = self._calculate_score(
                cdn_results["avg_response_time"],
                cdn_results["success_rate"]
            )

            results[cdn_name] = cdn_results

        sorted_results = dict(sorted(
            results.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        ))

        best_cdn = list(sorted_results.keys())[0] if sorted_results else None

        return {
            "providers": sorted_results,
            "best_cdn": {"name": best_cdn, **sorted_results.get(best_cdn, {})} if best_cdn else None,
            "total_tested": len(sorted_results),
            "iterations": iterations
        }

    def _calculate_score(self, avg_time: float, success_rate: float) -> int:
        """Calculate CDN score based on speed and reliability"""
        if success_rate == 0:
            return 0

        if avg_time <= 50:
            time_score = 100
        elif avg_time <= 100:
            time_score = 90
        elif avg_time <= 200:
            time_score = 75
        elif avg_time <= 500:
            time_score = 50
        elif avg_time <= 1000:
            time_score = 30
        else:
            time_score = 10

        return int(success_rate * 0.6 + time_score * 0.4)

    async def test_all(self) -> Dict[str, Any]:
        """Test all CDN providers"""
        return await self.benchmark()

    async def get_recommendations(self) -> Dict[str, Any]:
        """Get CDN recommendations based on testing"""
        results = await self.benchmark(iterations=2)
        providers = results["providers"]

        by_speed = sorted(
            providers.items(),
            key=lambda x: x[1]["avg_response_time"] if x[1]["avg_response_time"] > 0 else float("inf")
        )

        by_score = sorted(
            providers.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        return {
            "best_overall": {"name": by_score[0][0], **by_score[0][1]} if by_score else None,
            "fastest": {"name": by_speed[0][0], **by_speed[0][1]} if by_speed else None,
            "top_5": [{"name": n, **d} for n, d in by_score[:5]],
            "free_options": [
                {"name": n, **d} for n, d in by_score
                if "Free" in d.get("features", []) or "Free Tier" in d.get("features", [])
            ][:3]
        }
