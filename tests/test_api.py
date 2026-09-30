import unittest

from fastapi import HTTPException

from app import ChatRequest, chat, health


class ChatbotApiTests(unittest.TestCase):
    def test_health(self) -> None:
        result = health()
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["trained"])

    def test_chat(self) -> None:
        response = chat(ChatRequest(message="hello"))
        self.assertEqual(response.intent, "greeting")
        self.assertTrue(response.reply)

    def test_rejects_blank_message(self) -> None:
        with self.assertRaises(HTTPException) as context:
            chat(ChatRequest(message=" "))
        self.assertEqual(context.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
