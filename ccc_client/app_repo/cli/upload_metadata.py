import argparse

from ccc_client.app_repo.AppRepoRunner import AppRepoRunner
from ccc_client.utils import print_API_response


def run(args):
    runner = AppRepoRunner(args.host, args.port, args.authToken)
    r = runner.upload_metadata(args.imageId, args.metadata)
    print_API_response(r)


parser = argparse.ArgumentParser()
parser.set_defaults(runner=run)
parser.add_argument(
    "--metadata", "-m",
    type=str,
    required=True,
    help="tool metadata"
)
parser.add_argument(
    "--imageId", "-i",
    type=str,
    help="docker image id"
)
