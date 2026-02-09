"""SOX-style approval matrix configuration."""

from __future__ import annotations

from typing import Any, Dict, List


def get_approval_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "action": "AP payment > $10,000",
            "required_approvals": ["finance_manager", "controller"],
            "policy": "two-step",
        },
        {
            "action": "Vendor creation",
            "required_approvals": ["ap_manager"],
            "policy": "single-step",
        },
        {
            "action": "GL journal entry post",
            "required_approvals": ["accounting_manager"],
            "policy": "single-step",
        },
        {
            "action": "Bank account changes",
            "required_approvals": ["treasury_manager", "controller"],
            "policy": "two-step",
        },
    ]
