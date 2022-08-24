from rest_framework.request import Request
from rest_framework.response import Response

from sentry.api.bases import OrganizationEventsEndpointBase
from sentry.types.ratelimit import RateLimit, RateLimitCategory


class OrganizationIssuesHotspotsEndpoint(OrganizationEventsEndpointBase):
    enforce_rate_limit = True
    rate_limits = {
        "GET": {
            RateLimitCategory.IP: RateLimit(10, 1),
            RateLimitCategory.USER: RateLimit(10, 1),
            RateLimitCategory.ORGANIZATION: RateLimit(10, 1),
        }
    }

    def get(self, request: Request, organization) -> Response:

        response = [
            {
                "id": "<root>",
                "depth": 0,
                "index": 0,
            },
            {
                "id": "<root>/billiard",
                "depth": 1,
                "index": 1,
            },
            {
                "id": "<root>/billiard/pool.py",
                "errorCount": 3,
                "depth": 2,
                "index": 2,
            },
            {
                "id": "<root>/getsentry",
                "depth": 1,
                "index": 3,
            },
            {
                "id": "<root>/getsentry/utils",
                "depth": 2,
                "index": 4,
            },
            {
                "id": "<root>/getsentry/utils/flagr.py",
                "errorCount": 10,
                "depth": 3,
                "index": 5,
            },
            {
                "id": "<root>/sentry",
                "depth": 1,
                "index": 6,
            },
            {
                "id": "<root>/sentry/api",
                "depth": 2,
                "index": 7,
            },
            {
                "id": "<root>/sentry/api/client.py",
                "errorCount": 13,
                "depth": 3,
                "index": 8,
            },
            {
                "id": "<root>/sentry/api/endpoints",
                "depth": 3,
                "index": 10,
            },
            {
                "id": "<root>/sentry/api/endpoints/release_deploys.py",
                "errorCount": 123,
                "depth": 4,
                "index": 11,
            },
            {
                "id": "<root>/sentry/api/fields",
                "depth": 3,
                "index": 12,
            },
            {
                "id": "<root>/sentry/api/fields/avatar.py",
                "errorCount": 123,
                "depth": 3,
                "index": 13,
            },
            {
                "id": "<root>/sentry/db",
                "depth": 1,
                "index": 14,
            },
            {
                "id": "<root>/sentry/db/models",
                "depth": 2,
                "index": 15,
            },
            {
                "id": "<root>/sentry/db/models/fields",
                "depth": 3,
                "index": 16,
            },
            {
                "id": "<root>/sentry/db/models/fields/bounded.py",
                "errorCount": 123,
                "depth": 4,
                "index": 17,
            },
            {
                "id": "<root>/sentry/identity",
                "depth": 2,
                "index": 17,
            },
            {
                "id": "<root>/sentry/identity/oauth2.py",
                "errorCount": 123,
                "depth": 2,
                "index": 18,
            },
            {
                "id": "<root>/sentry/interfaces",
                "depth": 2,
                "index": 19,
            },
            {
                "id": "<root>/sentry/interfaces/contexts.py",
                "errorCount": 123,
                "depth": 2,
                "index": 20,
            },
            {
                "id": "<root>/sentry/models",
                "depth": 2,
                "index": 21,
            },
            {
                "id": "<root>/sentry/models/organizationmember.py",
                "errorCount": 123,
                "depth": 2,
                "index": 22,
            },
            {
                "id": "<root>/sentry/models/releasefile.py",
                "errorCount": 123,
                "depth": 2,
                "index": 23,
            },
            {
                "id": "<root>/sentry/net",
                "depth": 2,
                "index": 24,
            },
            {
                "id": "<root>/sentry/net/socket.py",
                "errorCount": 123,
                "depth": 2,
                "index": 25,
            },
            {
                "id": "<root>/sentry/receivers",
                "depth": 2,
                "index": 26,
            },
            {
                "id": "<root>/sentry/receivers/releases.py",
                "errorCount": 123,
                "depth": 2,
                "index": 27,
            },
            {
                "id": "<root>/sentry/release_health",
                "depth": 2,
                "index": 28,
            },
            {
                "id": "<root>/sentry/release_health/tasks.py",
                "errorCount": 123,
                "depth": 2,
                "index": 29,
            },
            {
                "id": "<root>/sentry/shared_integrations",
                "depth": 2,
                "index": 30,
            },
            {
                "id": "<root>/sentry/shared_integrations/client",
                "depth": 3,
                "index": 31,
            },
            {
                "id": "<root>/sentry/shared_integrations/client/base.py",
                "errorCount": 123,
                "depth": 3,
                "index": 32,
            },
            {
                "id": "<root>/sentry/utils",
                "depth": 2,
                "index": 33,
            },
            {
                "id": "<root>/sentry/utils/json.py",
                "errorCount": 123,
                "depth": 2,
                "index": 34,
            },
            {
                "id": "<root>/sentry/utils/locking",
                "depth": 3,
                "index": 35,
            },
            {
                "id": "<root>/sentry/utils/locking/lock.py",
                "errorCount": 123,
                "depth": 3,
                "index": 36,
            },
            {
                "id": "<root>/sentry/utils/monitors.py",
                "errorCount": 123,
                "depth": 2,
                "index": 38,
            },
        ]

        return Response(response)