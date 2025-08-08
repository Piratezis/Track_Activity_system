import json
import pathlib


class FileManager:
    def save(self, file_path, data):
        path = file_path
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"{path}")

    def load(self, file_path):
        path = file_path
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data


class ChatAnalyzer:
    def analyze_replies(self, chat_data):
        replies_from = {}
        replies_to = {}

        message_map = {msg['message_id']: msg['user_id'] for msg in chat_data}

        for message in chat_data:
            author_id = message.get('user_id')
            reply_to_id = message.get('reply_to_message_id')

            if author_id and reply_to_id:
                if author_id not in replies_from:
                    replies_from[author_id] = 0
                replies_from[author_id] += 1

                original_author_id = message_map.get(reply_to_id)
                if original_author_id:
                    if original_author_id not in replies_to:
                        replies_to[original_author_id] = 0
                    replies_to[original_author_id] += 1
        return replies_from, replies_to

    def get_most_active_repliers(self, replies_from, replies_to):
        most_replied = max(replies_to, key=replies_to.get, default=None)
        most_active_replier = max(replies_from, key=replies_from.get,
                                  default=None)
        return most_active_replier, most_replied

    def analyze_questions(self, chat_data):
        questions_by_user = {}
        question_keywords = ["?", "кто?", "что?", "где?", "когда?", "почему?",
                             "как?"]

        for message in chat_data:
            text = message.get('message_text', '').lower()
            author_id = message.get('user_id')

            is_question = any(keyword in text for keyword in
                              question_keywords) or text.endswith('?')

            if is_question and author_id:
                if author_id not in questions_by_user:
                    questions_by_user[author_id] = 0
                questions_by_user[author_id] += 1
        return questions_by_user
