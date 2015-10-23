# -*- coding: utf-8 -*-
"""
API module for ArtifactoryPath, it acts as a wrapper around ArtifactoryPath

Example:
    API usage

        code-block:: python
        >>> artifactory = Artifactory(
                url="https://artifactory.example.com",
                repo="repo-location",
                group="ext-snapshot-local/com/example",
                artifact="api",
                version="0.0.1-SNAPSHOT",
                )

        >>> # To downloaded artifact by name
        >>> artifactory.download('api-0.0.1-20150916.191654-929.jar')

        >>> # To downloaded latest artifact
        >>> artifactory.download()

Attributes:
    log (logging): Standard python logger

"""
__author__ = "Prathamesh Nevagi"

# stdlib imports
import os
import logging

# artifactory imports
from artifactory import ArtifactoryPath

# Define logger
# TODO: move logger to centralized location
log = logging
log.basicConfig(level=logging.INFO)


class Artifactory(object):
    """
    Artifactory api wrapper for ArtifactoryPath

    Attributes:
        log (logging): Standard python logger.
        TMP_DIR (str): Default temporary directory where artifact will be downloaded.

    """
    log = log
    TMP_DIR = "/tmp"

    def __init__(self, url, repo="", group="", artifact="",
            version="", username="", password="", *args, **kwargs):
        """
        Create artifactory client instance (ArtifactoryPath)

        Note:
            Please provide http/s in url args.

        Args:
            url (str): Artifactory server url.
            repo (str): Artifactory repo name.
            group (str): Artifactory group name.
            artifact (str): Artifactory artifact name.
            version (str): Artifactory version name.

            username (str): Artifactory account username.
            password (str): Artifactory account password.
        """
        self.url = url
        self.repo = repo
        self.group = group
        self.artifact = artifact
        self.version = version
        self.username = username
        self.password = password

        # create artifactory client instance
        self.client = ArtifactoryPath(self._construct_url(),
                auth=(self.username, self.password), *args, **kwargs)

    def download(self, artifact_name="", path=""):
        """
        Download artifact from artifactory server to local machine

        Note:
            If artifact_name is not provided, latest artifact will be downloaded.
            Default path to download artifact would be /tmp

        Args:
            artifact_name (str): Name of the artifact to be downloaded.
            path (str): Path where artifact will be downloaded

        """
        if artifact_name:
            artifact = self.get_by_name(artifact_name)
        else:
            artifact = self.get_latest()

        # path to download artifactory
        path = path if path else self.TMP_DIR
        artifactory_path = os.path.join(path, artifact.name)
        self.log.info("Downloading artifact {0} to {1}".format(
            artifact.name, artifactory_path))

        with artifact.open() as fl:
            with open(artifactory_path, "wb") as out:
                out.write(fl.read())

        return artifact

    def get_by_name(self, artifact_name):
        """
        Get artifact by name

        Args:
            artifact_name (str): Name of the artifact to be downloaded.

        Returns:
            matched_artifact (str): matched artifact from server is returned.

        Raises:
            Exception: If provided artifact is not found.

        """
        for artifact in reversed(list(self.client)):
            if artifact.name == artifact_name:
                matched_artifact = artifact
                break
        else:
            raise Exception("Artifact {0} not found.".format(artifact_name))

        self.log.info("Found artifact {0}".format(matched_artifact.name))
        return matched_artifact

    def get_latest(self, mime_type="application/java-archive"):
        """
        Get latest artifact

        Notes:
            Default mime_type is 'application/java-archive', it will search for latest jar file.

        Args:
            mime_type (str): MIME TYPE of the service.

        Returns:
            latest_artifact (str): latest artifact from server is returned.

        """
        for artifact in reversed(list(self.client)):
            if artifact.stat().mime_type == mime_type:
                latest_artifact = artifact
                break

        self.log.info("Found latest artifact {0}".format(latest_artifact.name))
        return latest_artifact

    def _construct_url(self):
        """
        Construct artifactory url from information provided.

        Returns:
            url (str): Absolute artifactory url.

        """
        url = "{url}/artifactory/{repo}/{group}/{artifact}/{version}".format(**{
            "url": self.url,
            "repo": self.repo,
            "group": self.group,
            "artifact": self.artifact,
            "version": self.version,
            })
        self.log.debug("Url constructed to {0}".format(url))
        return url
