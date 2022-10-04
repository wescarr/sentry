from sentry.integrations.github.webhook import GitHubIntegrationsWebhookEndpoint
from sentry.middleware.integrations.parsers.base import BaseRequestParser
from sentry.models.integrations import Integration


class GithubRequestParser(BaseRequestParser):
    webhook_endpoint_class = GitHubIntegrationsWebhookEndpoint

    def get_integration(self) -> Integration | None:
        view_class = self.match.func.view_class
        if view_class == self.webhook_endpoint_class:
            pass
