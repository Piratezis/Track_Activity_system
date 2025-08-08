import asyncio
import pathlib
from models import User, TelegramAccount
from manager import FileManager, ChatAnalyzer

# ______________________________________________________________________
# Ввод данных
storage_dir = pathlib.Path('storage')
api_id = '25290973'
api_hash = '35b85b1a818c842836e7f5fb0bdcadb7'
phone_number = '+79935474292'
chat_url = 'https://t.me/you_biohackages'


#______________________________________________________________________________

async def run():
    user = User(name="Илья Волков", phone_number=phone_number,
                storage_dir=storage_dir)

    telegram_account = TelegramAccount(user, api_id, api_hash)
    await telegram_account.connect()

    telegram_chat = telegram_account.chats.get(chat_url)
    if not telegram_chat:
        telegram_chat = await telegram_account.add_chat(chat_url)

    print(
        f"\nСбор и анализ сообщений...")
    messages = await telegram_chat.get_messages()

    file_manager = FileManager()
    file_manager.save(telegram_chat.storage_path, messages)

    saved_data = file_manager.load(telegram_chat.storage_path)

    if saved_data:
        user_id_to_name_map = {msg['user_id']: msg['author_name'] for msg in
                               saved_data if msg.get('user_id') is not None}

        analyzer = ChatAnalyzer()

        print(f"\n-Анализ чата '{telegram_chat.chat_url}' -")

        replies_from, replies_to = analyzer.analyze_replies(saved_data)
        most_active_replier_id, most_replied_id = analyzer.get_most_active_repliers(
            replies_from, replies_to)
        questions = analyzer.analyze_questions(saved_data)

        most_active_replier_name = user_id_to_name_map.get(
            most_active_replier_id, "Неизвестный")
        most_replied_name = user_id_to_name_map.get(most_replied_id,
                                                    "Неизвестный")

        print(f"Кто чаще всех отвечал: {most_active_replier_name}")
        print(f"Кто чаще всех получал ответы: {most_replied_name}")

        questions_by_name = {user_id_to_name_map.get(uid, "Неизвестный"): count
                             for uid, count in questions.items()}
        print(
            f"Количество вопросов от каждого пользователя: {questions_by_name}")


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except ValueError as e:
        print(f"Ошибка: Не удалось найти чат '{chat_url}'. Проверьте URL или username. {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
