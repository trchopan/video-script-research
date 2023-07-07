import yaml


def load_secret():
    with open("/etc/secrets/gcloud/secret.yaml", "r") as f:
        return yaml.safe_load(f.read())


secret = load_secret()
