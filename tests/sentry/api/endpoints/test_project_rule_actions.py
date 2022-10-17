from unittest import mock

from sentry.rules.actions.notify_event import NotifyEventAction
from sentry.testutils import APITestCase


class ProjectRuleActionsTest(APITestCase):
    endpoint = "sentry-api-0-project-rule-actions"
    method = "POST"

    @mock.patch.object(NotifyEventAction, "after")
    def test_actions(self, action):
        self.create_group(self.project)
        self.store_event(
            data={"message": "test error", "level": "error"}, project_id=self.project.id
        )
        action_data = [
            {
                "id": "sentry.rules.actions.notify_event.NotifyEventAction",
            }
        ]
        self.rule = self.create_project_rule(project=self.project, action_match=action_data)
        self.login_as(self.user)

        self.get_success_response(self.organization.slug, self.project.slug, self.rule.id)

        assert action.called

    def test_no_events(self):
        self.rule = self.create_project_rule(project=self.project)
        self.login_as(self.user)

        response = self.get_response(self.organization.slug, self.project.slug, self.rule.id)
        assert response.status_code == 400
