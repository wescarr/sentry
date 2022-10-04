from collections import OrderedDict
from typing import Any

from django import forms

from sentry.eventstore.models import Event
from sentry.rules import EventState
from sentry.rules.filters import EventFilter
from sentry.types.issues import GroupType

TYPE_CHOICES = OrderedDict([(f"{gt.value}", gt.name) for gt in GroupType])


class IssueTypeForm(forms.Form):
    value = forms.ChoiceField(choices=list(TYPE_CHOICES.items()))


class IssueTypeFilter(EventFilter):
    id = "sentry.rules.filters.issue_type.IssueTypeFilter"
    form_cls = IssueTypeForm
    form_fields = {"value": {"type": "choice", "choices": list(TYPE_CHOICES.items())}}
    rule_type = "filter/event"
    label = "The issue's type is equal to {value}"
    prompt = "The issue's type is ..."

    def passes(self, event: Event, state: EventState, **kwargs: Any) -> bool:
        try:
            value: GroupType = GroupType(int(self.get_option("value")))
        except (TypeError, ValueError):
            return False

        if event.group and event.group.issue_type:
            return value == event.group.issue_type

        if event.groups:
            for group in event.groups:
                if value == group.issue_type:
                    return True

        return False
