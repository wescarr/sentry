from io import BytesIO

from django.urls import reverse

from sentry.models import File
from sentry.replays.models import ReplayRecordingSegment
from sentry.testutils import APITestCase


class ReplayRecordingSegmentDetailsTestCase(APITestCase):
    endpoint = "sentry-api-0-project-replay-recording-segment-details"

    def setUp(self):
        super().setUp()

        self.file = File.objects.create(name="recording-segment-0", type="application/octet-stream")
        self.file.putfile(BytesIO(b"replay-recording-segment"))

        self.recording_segment = ReplayRecordingSegment.objects.create(
            replay_id="977771b2-ddd0-4cec-81bf-4c9283",
            project_id=self.project.id,
            sequence_id=0,
            file_id=self.file.id,
        )

        self.url = reverse(
            self.endpoint,
            args=(
                self.organization.slug,
                self.project.slug,
                self.recording_segment.replay_id,
                self.recording_segment.sequence_id,
            ),
        )

    def test_get_replay_recording_segment(self):
        self.login_as(user=self.user)

        with self.feature("organizations:session-replay"):
            response = self.client.get(self.url)

            assert response.status_code == 200, response.content
            assert response.data["id"] == str(self.recording_segment.id)
            assert response.data["replay_id"] == self.recording_segment.replay_id
            assert response.data["sequence_id"] == self.recording_segment.sequence_id
            assert response.data["project_id"] == self.recording_segment.project_id
            assert response.data["date_added"] == self.recording_segment.date_added

    def test_get_replay_recording_segment_download(self):
        self.login_as(user=self.user)

        with self.feature("organizations:session-replay"):
            response = self.client.get(self.url + "?download")

            assert response.status_code == 200, response.content
            assert (
                response.get("Content-Disposition")
                == f'attachment; filename="{self.recording_segment.replay_id}-{self.recording_segment.sequence_id}"'
            )
            assert response.get("Content-Length") == str(self.file.size)
            assert response.get("Content-Type") == "application/octet-stream"
            assert b"replay-recording-segment" == b"".join(response.streaming_content)
