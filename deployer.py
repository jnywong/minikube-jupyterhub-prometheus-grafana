import argparse
import json
import os
import subprocess
import shutil
import tempfile
from contextlib import ExitStack, contextmanager
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError

yaml = YAML(typ="safe", pure=True)


def deploy(type, namespace, config, debug, dry_run):
    if type == "support" or type == "app":
        helm_chart = Path(__file__).parent.joinpath(f"helm/{type}")
        cmd = [
            "helm",
            "upgrade",
            "--install",
            "--create-namespace",
            f"--namespace={namespace}",
            namespace,
            helm_chart,
        ]
        if dry_run:
            cmd.append("--dry-run")
        if debug:
            cmd.append("--debug")

        if config:
            val_files_str = [str(file) for file in config]
            for val_file in val_files_str:
                cmd.append(f"--values={val_file}")

                print(f"Running {' '.join([str(c) for c in cmd])}")
                subprocess.check_call(cmd)
        else:
            print(f"Running {' '.join([str(c) for c in cmd])}")
            subprocess.check_call(cmd)

    elif type == "grafana":
        grafana_url = "http://localhost:3000"
        dashboards_dir = config
        deploy_env = os.environ.copy()
        # sops_age_key = deploy_env.get("SOPS_AGE_KEY")  # FIX: decrypt sops key

        p1 = subprocess.Popen(
            [
                'sops',
                'decrypt',
                'helm/support/enc-grafana-token.secret.yaml',
            ],
            stdout=subprocess.PIPE,
        )
        p2 = subprocess.Popen(
            [
                'sed',
                '-r',
                's/(grafana_token: )//'
            ],
            stdin=p1.stdout,
            stdout=subprocess.PIPE,
        )
        p1.stdout.close()
        grafana_token = p2.communicate()[0].decode('utf-8').strip()
        deploy_env.update({"GRAFANA_TOKEN": grafana_token})

        try:
            print(f"Deploying grafana dashboards to {grafana_url}...")
            subprocess.check_call(
                ["./deploy.py", grafana_url],
                env=deploy_env,
                cwd=f"{dashboards_dir}",
            )
        except Exception as e:
            print(f"Failed to deploy Grafana dashboards: {str(e)}")
    else:
        raise ValueError(f"Unknown type: {type}")


def main():
    parser = argparse.ArgumentParser(description="Deploy script")
    parser.add_argument(
        "type", type=str, help="Type of deployment. Choose from support/app!"
    )
    parser.add_argument(
        "--namespace",
        type=str,
        help="Namespace to deploy to. Choose from support/app",
    )
    parser.add_argument(
        "--grafana_dashboards",
        type=str,
        default="../grafana-dashboards",
        help="Directory containing Grafana dashboards config",
    )    
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform a dry run"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )

    args = parser.parse_args()

    if args.type == "support":
        helm_chart = Path(__file__).parent.joinpath("helm/support")
        config = [
            helm_chart.joinpath(f"{args.namespace}.values.yaml"),
        ]
    elif args.type == "app":
        helm_chart = Path(__file__).parent.joinpath("helm/app")
        config = [
            helm_chart.joinpath("app.values.yaml"),
        ]
    elif args.type == "grafana":
        config = args.grafana_dashboards
    else:
        raise ValueError(f"Unknown type: {args.type}")

    deploy(
        args.type,
        args.namespace,
        config,
        args.debug,
        args.dry_run,
    )


if __name__ == "__main__":
    main()
