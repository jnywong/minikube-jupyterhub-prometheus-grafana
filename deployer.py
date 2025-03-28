import argparse
import json
import os
import subprocess
import tempfile
from contextlib import ExitStack, contextmanager
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError

yaml = YAML(typ="safe", pure=True)


def deploy(type, namespace, values_files, debug, dry_run):
    if type == "support":
        helm_chart = Path(__file__).parent.joinpath("helm-charts/support")
    elif type == "app":
        helm_chart = Path(__file__).parent.joinpath("helm-charts/app")
    else:
        raise ValueError(f"Unknown type: {type}")

    cmd = [
        "helm",
        "upgrade",
        "--install",
        "--create-namespace",
        "--wait",
        f"--namespace={namespace}",
        namespace,
        helm_chart,
    ]
    if dry_run:
        cmd.append("--dry-run")
    if debug:
        cmd.append("--debug")

    if values_files:
        val_files_str = [str(file) for file in values_files]
        for val_file in val_files_str:
            cmd.append(f"--values={val_file}")

            print(f"Running {' '.join([str(c) for c in cmd])}")
            subprocess.check_call(cmd)
    else:
        print(f"Running {' '.join([str(c) for c in cmd])}")
        subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser(description="Deploy script")
    parser.add_argument(
        "type", type=str, help="Type of deployment. Choose from support/app!"
    )
    parser.add_argument(
        "--namespace",
        type=str,
        help="Namespace to deploy to. Choose from support/staging/prod",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform a dry run"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )

    args = parser.parse_args()
    key_path = Path(__file__).parent.joinpath(
        "helm-charts/enc-deploy-credentials.secret.json"
    )
    if args.type == "support":
        helm_chart = Path(__file__).parent.joinpath("helm-charts/support")
        values_files = [
            helm_chart.joinpath(f"{args.namespace}.values.yaml"),
        ]
    elif args.type == "app":
        helm_chart = Path(__file__).parent.joinpath("helm-charts/app")
        values_files = [
            helm_chart.joinpath("app.values.yaml"),
        ]
    else:
        raise ValueError(f"Unknown type: {args.type}")

    deploy(
        args.type,
        args.namespace,
        values_files,
        args.debug,
        args.dry_run,
    )


if __name__ == "__main__":
    main()
