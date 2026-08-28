import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "copilot_review.py"


def load_module():
    spec = importlib.util.spec_from_file_location("copilot_review_under_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_response(status_code, text="", json_data=None):
    response = Mock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = {} if json_data is None else json_data
    return response


def write_event_file():
    event = {
        "pull_request": {"number": 8},
        "repository": {
            "full_name": "Krish-B06/ai-agent-code-review",
            "url": "https://api.github.com/repos/Krish-B06/ai-agent-code-review",
        },
    }
    handle = tempfile.NamedTemporaryFile("w", delete=False)
    json.dump(event, handle)
    handle.close()
    return handle.name


class TestCopilotReview(unittest.TestCase):
    def test_skips_review_when_copilot_for_actions_is_unavailable(self):
        module = load_module()
        event_path = write_event_file()
        stdout = io.StringIO()

        try:
            with patch.dict(os.environ, {"GITHUB_TOKEN": "github-token", "GITHUB_EVENT_PATH": event_path}, clear=False), \
                 patch.object(module.requests, "get", side_effect=[
                     make_response(200, text="diff --git a/file.py b/file.py"),
                     make_response(403, text="forbidden"),
                 ]), \
                 patch.object(module.requests, "post") as post_mock, \
                 patch.object(module.os.path, "exists", return_value=False), \
                 redirect_stdout(stdout):
                module.main()
        finally:
            os.unlink(event_path)

        self.assertIn("Skipping review", stdout.getvalue())
        post_mock.assert_not_called()

    def test_uses_exchanged_copilot_token_for_llm_request(self):
        module = load_module()
        event_path = write_event_file()
        stdout = io.StringIO()

        try:
            with patch.dict(os.environ, {"GITHUB_TOKEN": "github-token", "GITHUB_EVENT_PATH": event_path}, clear=False), \
                 patch.object(module.requests, "get", side_effect=[
                     make_response(200, text="diff --git a/file.py b/file.py"),
                     make_response(200, json_data={
                         "token": "copilot-token",
                         "endpoints": {"api": "https://api.githubcopilot.com"},
                     }),
                 ]), \
                 patch.object(module.requests, "post", side_effect=[
                     make_response(200, json_data={"choices": [{"message": {"content": "review body"}}]}),
                     make_response(201),
                 ]) as post_mock, \
                 patch.object(module.os.path, "exists", return_value=False), \
                 redirect_stdout(stdout):
                module.main()
        finally:
            os.unlink(event_path)

        llm_call = post_mock.call_args_list[0]
        self.assertEqual(llm_call.args[0], "https://api.githubcopilot.com/chat/completions")
        self.assertTrue(llm_call.kwargs["headers"]["Authorization"].startswith("Bearer "))
        self.assertTrue(llm_call.kwargs["headers"]["Authorization"].endswith("copilot-token"))


if __name__ == "__main__":
    unittest.main()
