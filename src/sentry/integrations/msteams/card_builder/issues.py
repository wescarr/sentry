from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence

from sentry.integrations.msteams.card_builder import (
    URL_FORMAT_STR,
    Action,
    AdaptiveCard,
    ColumnSetBlock,
    ContainerBlock,
    TextBlock,
)
from sentry.integrations.msteams.utils import ACTION_TYPE
from sentry.integrations.notifications import (
    build_attachment_text,
    build_attachment_title,
    build_footer,
    build_title_link,
    format_actor_option,
    format_actor_options,
)
from sentry.models import Event, Group, GroupStatus, Integration, Project, Rule
from sentry.types.integrations import ExternalProviders

from .base import MSTeamsMessageBuilder
from .block import (
    ActionType,
    TextSize,
    TextWeight,
    create_action_block,
    create_action_set_block,
    create_column_block,
    create_column_set_block,
    create_container_block,
    create_input_choice_set_block,
    create_logo_block,
    create_text_block,
)
from .utils import IssueConstants

# NOTE: DATE and TIME are formatting functions in Adaptive Cards.
# The syntax is `{{DATE(<some_date>, SHORT)}}` or `{{TIME(<some_date>)}}`
# https://docs.microsoft.com/en-us/adaptive-cards/authoring-cards/text-features
# Since `{` and `}` are special characters in format strings, we need to use
# double `{{` and `}}` to get the actual character in. Hence the `{{{{` and `}}}}`.


def build_input_choice_card(
    title: str,
    data: Any,
    input_id: str,
    choices: Sequence[str, Any],
    default_choice: Any = None,
):
    return MSTeamsMessageBuilder().build(
        title=create_text_block(title, weight=TextWeight.BOLDER),
        text=create_input_choice_set_block(
            id=input_id, choices=choices, default_choice=default_choice
        ),
        actions=[create_action_block(ActionType.SUBMIT, title=title, data=data)],
    )


class MSTeamsIssueMessageBuilder(MSTeamsMessageBuilder):
    def __init__(self, group: Group, event: Event, rules: Sequence[Rule], integration: Integration):
        self.group = group
        self.event = event
        self.rules = rules
        self.integration = integration

    def get_timestamp(self) -> datetime:
        ts = self.group.last_seen
        return max(ts, self.event.datetime) if self.event else ts

    def create_date_block(self) -> TextBlock:
        date = self.get_timestamp()

        # Adaptive cards is strict about the isoformat.
        date = date.replace(microsecond=0).isoformat()

        return create_text_block(
            IssueConstants.DATE_FORMAT.format(date=date),
            size=TextSize.SMALL,
            weight=TextWeight.LIGHTER,
            horizontalAlignment="Center",
        )

    def create_footer_block(self) -> ColumnSetBlock:
        logo = create_logo_block(height="20px")

        project = Project.objects.get_from_cache(id=self.group.project_id)
        footer = create_text_block(
            build_footer(self.group, project, self.rules, URL_FORMAT_STR),
            size=TextSize.SMALL,
            weight=TextWeight.LIGHTER,
            wrap=False,
        )

        return create_column_set_block(
            logo,
            create_column_block(footer, isSubtle=True, spacing="none"),
            self.create_date_block(),
        )

    def create_assignee_block(self) -> TextBlock | None:
        assignee = self.group.get_assignee()

        if assignee:
            assignee_string = format_actor_option(assignee)["text"]
            return create_text_block(
                IssueConstants.ASSIGNEE_NOTE.format(assignee=assignee_string), size=TextSize.SMALL
            )

    def generate_action_payload(self, action_type: ACTION_TYPE) -> Any:
        # we need nested data or else Teams won't handle the payload correctly
        return {
            "payload": {
                "actionType": action_type,
                "groupId": self.event.group.id,
                "eventId": self.event.event_id,
                "rules": [rule.id for rule in self.rules],
                "integrationId": self.integration.id,
            }
        }

    def get_teams_choices(self) -> Sequence[str, str]:
        teams = self.group.project.teams.all().order_by("slug")
        return [("Me", IssueConstants.ME)] + [
            (team["text"], team["value"]) for team in format_actor_options(teams)
        ]

    def create_issue_action_block(
        self,
        condition: bool,
        action: ACTION_TYPE,
        action_title: str,
        reverse_action: ACTION_TYPE,
        reverse_action_title: str,
        **card_kwargs: str,
    ) -> Action:
        if condition:
            data = self.generate_action_payload(reverse_action)
            return create_action_block(ActionType.SUBMIT, title=reverse_action_title, data=data)

        data = self.generate_action_payload(action)
        card = build_input_choice_card(title=action_title, data=data, **card_kwargs)
        return create_action_block(ActionType.SHOW_CARD, title=action_title, card=card)

    def get_ignore_action(self, status: GroupStatus) -> Action:
        return self.create_issue_action_block(
            condition=GroupStatus.IGNORED == status,
            action=ACTION_TYPE.IGNORE,
            action_title=IssueConstants.IGNORE,
            reverse_action=ACTION_TYPE.UNRESOLVE,
            reverse_action_title=IssueConstants.STOP_IGNORING,
            input_id=IssueConstants.IGNORE_INPUT_ID,
            choices=IssueConstants.IGNORE_INPUT_CHOICES,
        )

    def get_resolve_action(self, status: GroupStatus) -> Action:
        return self.create_issue_action_block(
            condition=GroupStatus.RESOLVED == status,
            action=ACTION_TYPE.RESOLVE,
            action_title=IssueConstants.RESOLVE,
            reverse_action=ACTION_TYPE.UNRESOLVE,
            reverse_action_title=IssueConstants.UNRESOLVE,
            input_id=IssueConstants.RESOLVE_INPUT_ID,
            choices=IssueConstants.RESOLVE_INPUT_CHOICES,
        )

    def get_assign_action(self) -> Action:
        teams_choices = self.get_teams_choices()

        return self.create_issue_action_block(
            condition=self.group.get_assignee(),
            action=ACTION_TYPE.ASSIGN,
            action_title=IssueConstants.ASSIGN,
            reverse_action=ACTION_TYPE.UNASSIGN,
            reverse_action_title=IssueConstants.UNASSIGN,
            input_id=IssueConstants.ASSIGN_INPUT_ID,
            choices=teams_choices,
            default_choice=IssueConstants.ME,
        )

    def get_issue_actions(self) -> ContainerBlock:
        status = self.group.get_status()

        return create_container_block(
            create_action_set_block(
                self.get_resolve_action(status),
                self.get_ignore_action(status),
                self.get_assign_action(),
            )
        )

    def build(
        self,
    ) -> AdaptiveCard:
        title_text = build_attachment_title(self.group or self.event)
        title_link = build_title_link(
            group=self.group,
            event=self.event,
            link_to_event=True,
            issue_details=False,
            notification=None,
            provider=ExternalProviders.MSTEAMS,
        )

        fields = []

        description_text = build_attachment_text(self.group, self.event)
        if description_text:
            fields.append(
                create_text_block(description_text, size=TextSize.MEDIUM, weight=TextWeight.BOLDER)
            )

        fields.append(self.create_footer_block())

        assignee_block = self.create_assignee_block()
        if assignee_block:
            fields.append(assignee_block)

        fields.append(self.get_issue_actions())

        return super().build(
            title=create_text_block(
                URL_FORMAT_STR.format(text=title_text, url=title_link),
                size=TextSize.LARGE,
                weight=TextWeight.BOLDER,
            ),
            fields=fields,
        )