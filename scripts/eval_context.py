#!/usr/bin/env python3
"""Check the context classifier on hand-written synthetic IP cases.

DEV_CASES were used while choosing the prompt, so their score is a sanity
check only. HOLDOUT_CASES were written after the prompt was fixed and the
prompt was not changed for them; they are still few and written by the team,
so neither score is an estimate of real-world accuracy.
"""

import argparse
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from privacylens.config import load_context  # noqa: E402
from privacylens.context import HeuristicContextClassifier  # noqa: E402
from privacylens.llm import DEFAULT_MODEL, DEFAULT_URL, LLMContextClassifier, OllamaClient  # noqa: E402
from privacylens.models import Candidate  # noqa: E402


DEV_CASES = (
    (
        "DOCUMENTATION EXAMPLE (PUBLIC TUTORIAL)\nHow to configure the SDK:\nAPI_KEY=<YOUR_API_KEY>\n"
        "SERVER_IP=192.168.10.24\nReaders substitute their own values.\nAll values shown are synthetic test data.",
        "192.168.10.24",
        "KEEP",
    ),
    (
        "INTERNAL CONFIGURATION (SENSITIVE)\nEMAIL=demo@example.com\nSERVER_IP=192.168.10.24\n"
        "PASSWORD=demo-password-123\nTOKEN=demo-token-987654\nAll values shown are synthetic test data.",
        "192.168.10.24",
        "REPLACE",
    ),
    (
        "README - Quick start\nIn the sample setup below, point the client at 10.0.0.5.\n"
        "Replace it with the address of your own server.",
        "10.0.0.5",
        "KEEP",
    ),
    ("ops-dashboard | prod-eu\nProduction database host: 10.20.30.40\nreplicas: 3   status: healthy", "10.20.30.40", "REPLACE"),
    ("Acme Corp customer VPN\nGateway: 172.16.4.9\nTunnel status: UP", "172.16.4.9", "REPLACE"),
    (
        "Home networking tutorial\nMost home routers use the default address 192.168.1.1.\n"
        "Type it into your browser to open the settings page.",
        "192.168.1.1",
        "KEEP",
    ),
    ("$ ssh admin@203.0.113.7\n# staging bastion for the payments team\nLast login: Mon Oct 5", "203.0.113.7", "REPLACE"),
    (
        "Docs: example output\n$ ip addr\ninet 192.168.0.10/24 brd 192.168.0.255\nYour address will differ.",
        "192.168.0.10",
        "KEEP",
    ),
    (
        "Kubernetes guide - step 3\nExample: kubectl config set-cluster demo --server=https://10.1.2.3:6443\n"
        "Use your cluster's API address here.",
        "10.1.2.3",
        "KEEP",
    ),
    (
        "#incident-2231  (Slack)\nprimary DB at 10.8.0.14 is refusing connections, failing over now",
        "10.8.0.14",
        "REPLACE",
    ),
    (
        "Grafana - Finance team / Billing API\nupstream: 172.31.9.200:8443   p99 latency 240ms",
        "172.31.9.200",
        "REPLACE",
    ),
    (
        "Lecture 4: IPv4 addressing\nA private class C address looks like 192.168.5.20\n"
        "Exercise: write down the network part.",
        "192.168.5.20",
        "KEEP",
    ),
)


HOLDOUT_CASES = (
    (
        "Zoom screen share - Alice's laptop\n$ ping 10.12.0.8\n"
        "64 bytes from 10.12.0.8: icmp_seq=1 ttl=63 time=1.2 ms\n# our office printer",
        "10.12.0.8",
        "REPLACE",
    ),
    (
        "RFC 5737 reserves 198.51.100.0/24 for documentation.\n"
        "For instance, 198.51.100.23 is safe to use in examples.",
        "198.51.100.23",
        "KEEP",
    ),
    (
        "docker-compose.yml (from the official tutorial repo)\n  db:\n    environment:\n"
        "      DB_HOST: 172.17.0.2   # default Docker bridge address",
        "172.17.0.2",
        "KEEP",
    ),
    (
        "VS Code - ~/work/hr-portal/.env\nLDAP_SERVER=10.60.3.21\nLDAP_BIND_DN=cn=svc-hr",
        "10.60.3.21",
        "REPLACE",
    ),
    (
        "Quiz question 3\nWhich of these is a valid IPv4 address?\n(a) 256.1.1.1  (b) 10.4.5.6  (c) 1.2.3",
        "10.4.5.6",
        "KEEP",
    ),
    (
        "Jenkins build #482 - deploy to eu-west\nPushing artifact to 10.200.14.77:5000 ... done",
        "10.200.14.77",
        "REPLACE",
    ),
    (
        "Course slides: NAT explained\nInside host 192.168.1.50 is translated to the router's public address.",
        "192.168.1.50",
        "KEEP",
    ),
    (
        "Customer support ticket #8812\n"
        "Client reports their POS terminal at 192.168.44.12 cannot reach the store server.",
        "192.168.44.12",
        "REPLACE",
    ),
    (
        "Postman - Collection: Sample Pet Store API (public)\n"
        "GET http://10.0.2.2:8080/pets   # Android emulator alias for your localhost",
        "10.0.2.2",
        "KEEP",
    ),
    (
        "mysql> SELECT * FROM servers;\n| web-07 | 10.31.7.7 | rack B |\n| web-08 | 10.31.7.8 | rack B |",
        "10.31.7.7",
        "REPLACE",
    ),
    (
        "Wireshark - hotel_wifi.pcap\nSource 172.24.9.133 -> Destination 52.1.2.3 (TLS)\n"
        "Captured during client visit",
        "172.24.9.133",
        "REPLACE",
    ),
    (
        "Cisco Packet Tracer lab 2 - instructions\n"
        "Assign PC0 the address 192.168.10.10 and PC1 192.168.10.11.",
        "192.168.10.10",
        "KEEP",
    ),
)

SETS = {"dev": DEV_CASES, "holdout": HOLDOUT_CASES}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classifier", choices=("llm", "rules"), default="llm")
    parser.add_argument("--llm-url", default=DEFAULT_URL)
    parser.add_argument("--llm-model", default=DEFAULT_MODEL)
    parser.add_argument("--set", choices=("dev", "holdout", "all"), default="all")
    args = parser.parse_args()

    context = load_context(ROOT / "config" / "context.yaml")
    if args.classifier == "rules":
        classifier = HeuristicContextClassifier(context)
    else:
        client = OllamaClient(args.llm_url, args.llm_model)
        if not client.available():
            raise SystemExit("model {} is not available at {}".format(args.llm_model, args.llm_url))
        classifier = LLMContextClassifier(context, client.chat)

    started = time.time()
    total = 0
    for name in ("dev", "holdout") if args.set == "all" else (args.set,):
        correct = leaked = 0
        for index, (screen, value, expected) in enumerate(SETS[name], start=1):
            decision = classifier.classify(Candidate(value, "IP_ADDRESS", 0, len(value), (0, 0, 1, 1)), screen)
            correct += decision.action == expected
            leaked += expected == "REPLACE" and decision.action == "KEEP"
            mark = "ok " if decision.action == expected else "BAD"
            print("{} {}#{:<2} expected={:<7} got={:<7} by={:<13} {}".format(
                mark, name, index, expected, decision.action, decision.decided_by, decision.reason
            ))
        total += len(SETS[name])
        print("[{}] correct {}/{}  sensitive values kept (leaks) {}".format(name, correct, len(SETS[name]), leaked))
    print("{:.1f}s per case".format((time.time() - started) / total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
