#!/usr/bin/env python3
"""
🎯 Recommendation Engine Module
===============================
Generates smart recommendations based on network analysis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """A single recommendation"""
    category: str
    priority: str  # high, medium, low
    title: str
    description: str
    action: str
    impact: str


class RecommendationEngine:
    """Smart recommendation engine for network optimization"""

    def __init__(self):
        self.recommendations = []

    def analyze(
        self,
        network_data: Dict[str, Any] = None,
        dns_data: Dict[str, Any] = None,
        cdn_data: Dict[str, Any] = None,
        protocol_data: Dict[str, Any] = None,
        port_data: Dict[str, Any] = None,
        ping_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze all data and generate recommendations"""
        self.recommendations = []

        if network_data:
            self._analyze_network(network_data)

        if dns_data:
            self._analyze_dns(dns_data)

        if cdn_data:
            self._analyze_cdn(cdn_data)

        if protocol_data:
            self._analyze_protocol(protocol_data)

        if port_data:
            self._analyze_ports(port_data)

        if ping_data:
            self._analyze_ping(ping_data)

        high_priority = [r for r in self.recommendations if r.priority == "high"]
        medium_priority = [r for r in self.recommendations if r.priority == "medium"]
        low_priority = [r for r in self.recommendations if r.priority == "low"]

        return {
            "total_recommendations": len(self.recommendations),
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
            "low_priority": len(low_priority),
            "recommendations": {
                "high": [self._to_dict(r) for r in high_priority],
                "medium": [self._to_dict(r) for r in medium_priority],
                "low": [self._to_dict(r) for r in low_priority]
            },
            "summary": self._generate_summary()
        }

    def _to_dict(self, rec: Recommendation) -> Dict[str, Any]:
        """Convert recommendation to dict"""
        return {
            "category": rec.category,
            "priority": rec.priority,
            "title": rec.title,
            "description": rec.description,
            "action": rec.action,
            "impact": rec.impact
        }

    def _analyze_network(self, data: Dict[str, Any]):
        """Analyze network data"""
        latency = data.get("latency_ms", 0)

        if latency > 100:
            self.recommendations.append(Recommendation(
                category="network",
                priority="high",
                title="High Network Latency",
                description=f"Your network latency is {latency}ms which may impact performance.",
                action="Consider switching to a closer server or using a VPN with better routing.",
                impact="Reduce latency by up to 50%"
            ))
        elif latency > 50:
            self.recommendations.append(Recommendation(
                category="network",
                priority="medium",
                title="Moderate Network Latency",
                description=f"Your network latency is {latency}ms which is acceptable but could be improved.",
                action="Consider using a CDN or optimizing your connection.",
                impact="Improve response times by 10-30%"
            ))

        mtu = data.get("mtu", 1500)
        if mtu < 1400:
            self.recommendations.append(Recommendation(
                category="network",
                priority="medium",
                title="Low MTU Detected",
                description=f"Your MTU is {mtu} which may cause fragmentation.",
                action="Consider adjusting MTU settings or using a VPN that handles fragmentation.",
                impact="Reduce packet overhead and improve throughput"
            ))

    def _analyze_dns(self, data: Dict[str, Any]):
        """Analyze DNS data"""
        if "best_server" in data and data["best_server"]:
            best = data["best_server"]
            current_time = best.get("avg_response_time", 0)

            if current_time > 50:
                self.recommendations.append(Recommendation(
                    category="dns",
                    priority="high",
                    title="Slow DNS Resolution",
                    description=f"DNS resolution time is {current_time}ms which is slow.",
                    action=f"Switch to {best.get('name', 'a faster DNS')} for better performance.",
                    impact="Reduce page load times significantly"
                ))

        servers = data.get("servers", {})
        for name, server_data in servers.items():
            privacy = server_data.get("privacy")
            if privacy == "high":
                self.recommendations.append(Recommendation(
                    category="privacy",
                    priority="low",
                    title=f"Consider {name} for Privacy",
                    description=f"{name} offers high privacy protection.",
                    action=f"Use {server_data.get('ip', name)} as your DNS server.",
                    impact="Improve privacy and reduce tracking"
                ))
                break

    def _analyze_cdn(self, data: Dict[str, Any]):
        """Analyze CDN data"""
        if "best_cdn" in data and data["best_cdn"]:
            best = data["best_cdn"]
            time_ms = best.get("avg_response_time", 0)

            if time_ms < 100:
                self.recommendations.append(Recommendation(
                    category="cdn",
                    priority="low",
                    title="Optimal CDN Performance",
                    description=f"{best.get('name', 'CDN')} is performing excellently at {time_ms}ms.",
                    action="Continue using current CDN configuration.",
                    impact="Already optimized"
                ))
            else:
                self.recommendations.append(Recommendation(
                    category="cdn",
                    priority="medium",
                    title="CDN Optimization Possible",
                    description=f"CDN response time is {time_ms}ms.",
                    action=f"Consider using {best.get('name', 'a different CDN')}.",
                    impact="Improve content delivery by 20-40%"
                ))

    def _analyze_protocol(self, data: Dict[str, Any]):
        """Analyze protocol data"""
        summary = data.get("summary", {})

        tls13 = summary.get("tls_1_3", {})
        if tls13.get("success_rate", 0) < 50:
            self.recommendations.append(Recommendation(
                category="security",
                priority="high",
                title="TLS 1.3 Not Available",
                description="TLS 1.3 is not consistently available on tested endpoints.",
                action="Ensure your servers support TLS 1.3 for better security and performance.",
                impact="Improve security and reduce handshake latency"
            ))

        https = summary.get("https", {})
        if https.get("avg_time_ms", 0) > 500:
            self.recommendations.append(Recommendation(
                category="performance",
                priority="medium",
                title="Slow HTTPS Connections",
                description=f"HTTPS connections averaging {https.get('avg_time_ms', 0)}ms.",
                action="Consider using HTTP/2 or optimizing TLS settings.",
                impact="Reduce connection overhead by 30%"
            ))

    def _analyze_ports(self, data: Dict[str, Any]):
        """Analyze port scan data"""
        open_ports = data.get("open_ports", [])

        risky_ports = [p for p in open_ports if p.get("port") in [23, 21, 3389]]
        if risky_ports:
            self.recommendations.append(Recommendation(
                category="security",
                priority="high",
                title="Potentially Risky Ports Open",
                description=f"Found {len(risky_ports)} potentially risky ports open.",
                action="Review and close unnecessary ports, or restrict access via firewall.",
                impact="Improve security posture significantly"
            ))

        vpn_ports = [p for p in open_ports if p.get("category") == "vpn"]
        if vpn_ports:
            self.recommendations.append(Recommendation(
                category="vpn",
                priority="low",
                title="VPN Ports Available",
                description=f"{len(vpn_ports)} VPN-related ports are open.",
                action="Consider using these for secure connections.",
                impact="Enable VPN connectivity"
            ))

    def _analyze_ping(self, data: Dict[str, Any]):
        """Analyze global ping data"""
        if "fastest_region" in data and data["fastest_region"]:
            fastest = data["fastest_region"]
            latency = fastest.get("avg_latency_ms", 0)

            self.recommendations.append(Recommendation(
                category="deployment",
                priority="medium",
                title=f"Optimal Region: {fastest.get('name', 'Unknown')}",
                description=f"Lowest latency region at {latency}ms.",
                action=f"Consider deploying to {fastest.get('location', 'this region')} for best performance.",
                impact="Minimize latency for your users"
            ))

    def _generate_summary(self) -> str:
        """Generate summary text"""
        total = len(self.recommendations)
        high = len([r for r in self.recommendations if r.priority == "high"])

        if high > 0:
            return f"Found {total} recommendations with {high} high-priority items requiring attention."
        elif total > 0:
            return f"Found {total} recommendations. Your network is performing well with room for optimization."
        else:
            return "No recommendations at this time. Consider running more tests."

    def get_quick_wins(self) -> List[Dict[str, Any]]:
        """Get quick optimization opportunities"""
        quick_wins = [
            r for r in self.recommendations
            if r.priority in ["high", "medium"] and r.category in ["dns", "cdn"]
        ]
        return [self._to_dict(r) for r in quick_wins[:5]]
