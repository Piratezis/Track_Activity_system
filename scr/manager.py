# """Задачи на файл.
# 1) Принты на логи
# 2) Вынести переменные
# 3) Проверка на все исключения
# 4) Интеграция логики узлов
# 5) СТандарты
# """

import json
from pyvis.network import Network
from pathlib import Path
from typing import List, Dict, Any, Tuple
from loguru import logger
from scr.config import (
    LogMessages,
    GraphVisualizationSettings,
    FileTemplates,
    PythonSettings,
    DateFormat,
    QUESTION_KEYWORDS,
    Extensions,
)
import smtplib
from email.message import EmailMessage
from scr.enums import EdgeType, AnalysisAttributes, MessageKeys, ChatObjectAttributes
from scr.models import Mistaken, Chat, Graph
import networkx as nx
import os

from datetime import datetime


# Работа с pdf
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import ParagraphStyle


#
# # _____________________________________________________________________________
class ChatAnalyzer:
    """
    Анализатор графа чата с использованием NetworkX
    Включает существующие методы анализа
    """

    def __init__(self, graph):
        self.graph = graph
        self.nx_graph = self.convert_to_nx_graph()

    def convert_to_nx_graph(self) -> nx.DiGraph:
        """Конвертирует внутренний Graph в NetworkX граф"""
        G = nx.DiGraph()

        # Добавляем узлы (пользователей)
        for user_id, knot in self.graph.users.items():
            G.add_node(user_id, username=knot.username)

        # Добавляем рёбра (взаимодействия)
        for edge in self.graph.edges.values():
            G.add_edge(
                edge.from_user.user_id,
                edge.to_user.user_id,
                type=edge.edge_type,
                content=edge.content,
            )

        return G

    def _get_top_users_with_names(
        self, metric_dict: Dict[int, Any], count: int = 10
    ) -> List[Dict]:
        """Возвращает топ пользователей с именами и значениями метрик"""
        top_users = []
        for user_id, value in sorted(
            metric_dict.items(), key=lambda x: x[1], reverse=True
        )[:count]:
            username = (
                self.graph.users[user_id].username
                if user_id in self.graph.users
                else str(user_id)
            )
            top_users.append(
                {
                    AnalysisAttributes.USER_ID: user_id,
                    AnalysisAttributes.USERNAME: username,
                    AnalysisAttributes.VALUE: value,
                }
            )
        return top_users

    def analyze_replies(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Анализ ответов в чате
        Возвращает: (кто_отвечал, кому_отвечали)
        """
        # Фильтруем только REPLY связи
        reply_edges = [
            (u, v)
            for u, v, attr in self.nx_graph.edges(data=True)
            if attr.get("type") == EdgeType.REPLY
        ]

        reply_G = nx.DiGraph()
        reply_G.add_edges_from(reply_edges)

        replies_from = dict(reply_G.out_degree())  # Кто отвечал
        replies_to = dict(reply_G.in_degree())  # Кому отвечали

        return replies_from, replies_to

    def get_detailed_reply_analysis(self) -> Dict[str, Any]:
        """Детальный анализ ответов с топ-10 пользователями"""
        replies_from, replies_to = self.analyze_replies()

        return {
            AnalysisAttributes.TOP_REPLIERS: self._get_top_users_with_names(
                replies_from, 10
            ),
            AnalysisAttributes.TOP_REPLIED_TO: self._get_top_users_with_names(
                replies_to, 10
            ),
            AnalysisAttributes.TOTAL_REPLIES: sum(replies_from.values()),
        }

    def analyze_questions(self, question_keywords: List[str] = None) -> Dict[int, int]:
        """
        Анализ вопросов в чате
        """
        if question_keywords is None:
            question_keywords = QUESTION_KEYWORDS

        question_count = {}

        for edge in self.graph.edges.values():
            if edge.edge_type == EdgeType.MESSAGE and edge.content:
                text = edge.content.lower()

                # Проверяем на вопросы
                is_question = text.endswith("?") or any(
                    keyword in text for keyword in question_keywords
                )

                if is_question:
                    user_id = edge.from_user.user_id
                    question_count[user_id] = question_count.get(user_id, 0) + 1

        return question_count

    def get_detailed_question_analysis(self) -> Dict[str, Any]:
        """Детальный анализ вопросов с топ-10 пользователями"""
        question_stats = self.analyze_questions()

        return {
            AnalysisAttributes.TOP_QUESTION_ASKERS: self._get_top_users_with_names(
                question_stats, 10
            ),
            AnalysisAttributes.TOTAL_QUESTIONS: sum(question_stats.values()),
        }

    def get_most_active_users(self) -> List[Tuple[int, int]]:
        """Самые активные пользователи по исходящим связям"""
        out_degree = dict(self.nx_graph.out_degree())
        return sorted(out_degree.items(), key=lambda x: x[1], reverse=True)

    def get_most_popular_users(self) -> List[Tuple[int, int]]:
        """Самые популярные пользователи по входящим связям"""
        in_degree = dict(self.nx_graph.in_degree())
        return sorted(in_degree.items(), key=lambda x: x[1], reverse=True)

    def get_detailed_activity_analysis(self) -> Dict[str, Any]:
        """Детальный анализ активности с топ-10 пользователями"""
        out_degree = dict(self.nx_graph.out_degree())
        in_degree = dict(self.nx_graph.in_degree())
        total_degree = dict(self.nx_graph.degree())

        return {
            AnalysisAttributes.TOP_ACTIVE_USERS: self._get_top_users_with_names(
                out_degree, 10
            ),
            AnalysisAttributes.TOP_POPULAR_USERS: self._get_top_users_with_names(
                in_degree, 10
            ),
            AnalysisAttributes.TOP_ENGAGED_USERS: self._get_top_users_with_names(
                total_degree, 10
            ),
        }

    def calculate_centrality_metrics(self) -> Dict[str, Any]:
        """Расчет различных метрик центральности"""
        degree_centrality = nx.degree_centrality(self.nx_graph)
        betweenness_centrality = nx.betweenness_centrality(self.nx_graph)
        closeness_centrality = nx.closeness_centrality(self.nx_graph)
        eigenvector_centrality = nx.eigenvector_centrality(self.nx_graph, max_iter=1000)

        return {
            AnalysisAttributes.DEGREE_CENTRALITY: self._get_top_users_with_names(
                degree_centrality, 10
            ),
            AnalysisAttributes.BETWEENNESS_CENTRALITY: self._get_top_users_with_names(
                betweenness_centrality, 10
            ),
            AnalysisAttributes.CLOSENESS_CENTRALITY: self._get_top_users_with_names(
                closeness_centrality, 10
            ),
            AnalysisAttributes.EIGENVECTOR_CENTRALITY: self._get_top_users_with_names(
                eigenvector_centrality, 10
            ),
        }

    def find_opinion_leaders(self) -> Dict[str, Any]:
        """Находит лидеров мнений в чате с детальной информацией"""

        # 1. Самые активные писатели (исходящие связи)
        active_writers = self.get_most_active_users()[:10]

        # 2. Самые популярные (входящие связи)
        popular_users = self.get_most_popular_users()[:10]

        # 3. Анализ ответов
        replies_from, replies_to = self.analyze_replies()
        most_replied_to = (
            max(replies_to.items(), key=lambda x: x[1])[0] if replies_to else None
        )

        # 4. Центральность по посредничеству (betweenness)
        betweenness = nx.betweenness_centrality(self.nx_graph)
        top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        return {
            AnalysisAttributes.TOP_ACTIVE_WRITERS: self._get_top_users_with_names(
                dict(active_writers), 10
            ),
            AnalysisAttributes.TOP_POPULAR_USERS: self._get_top_users_with_names(
                dict(popular_users), 10
            ),
            AnalysisAttributes.MOST_INFLUENTIAL: most_replied_to,
            AnalysisAttributes.TOP_BETWEENNESS_LEADERS: self._get_top_users_with_names(
                betweenness, 5
            ),
            AnalysisAttributes.NETWORK_HUBS: self._get_top_users_with_names(
                nx.degree_centrality(self.nx_graph), 5
            ),
        }

    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """
        Возвращает все метрики в формате JSON для отчета
        Включает топ-10 пользователей по каждой категории
        """
        return {
            AnalysisAttributes.SUMMARY: {
                AnalysisAttributes.TOTAL_USERS: len(self.graph.users),
                AnalysisAttributes.TOTAL_INTERACTIONS: len(self.graph.edges),
                AnalysisAttributes.TOTAL_MESSAGES: sum(
                    dict(self.nx_graph.out_degree()).values()
                ),
            },
            AnalysisAttributes.ACTIVITY_ANALYSIS: self.get_detailed_activity_analysis(),
            AnalysisAttributes.REPLY_ANALYSIS: self.get_detailed_reply_analysis(),
            AnalysisAttributes.QUESTION_ANALYSIS: self.get_detailed_question_analysis(),
            AnalysisAttributes.CENTRALITY_METRICS: self.calculate_centrality_metrics(),
            AnalysisAttributes.OPINION_LEADERS: self.find_opinion_leaders(),
            AnalysisAttributes.NETWORK_PROPERTIES: {
                AnalysisAttributes.DENSITY: nx.density(self.nx_graph),
                AnalysisAttributes.AVERAGE_CLUSTERING: nx.average_clustering(
                    self.nx_graph.to_undirected()
                ),
                AnalysisAttributes.IS_CONNECTED: nx.is_weakly_connected(self.nx_graph),
                AnalysisAttributes.NUMBER_OF_COMPONENTS: nx.number_weakly_connected_components(
                    self.nx_graph
                ),
            },
        }

    def get_user_activity_stats(self, user_id: int) -> Dict[str, int]:
        """
        Возвращает статистику активности пользователя в графе.

        Содержит три основные метрики:
        - out_degree: количество исходящих взаимодействий (активность пользователя)
        - in_degree: количество входящих взаимодействий (популярность пользователя)
        - total_degree: общее количество взаимодействий

        Parameters:
            user_id (int): идентификатор пользователя

        Returns:
            Dict[str, int]: словарь с метриками активности. Возвращает пустой словарь
            если пользователь не найден в графе.
        """
        if user_id not in self.nx_graph:
            return {}

        return {
            AnalysisAttributes.OUT_DEGREE: self.nx_graph.out_degree(user_id),
            AnalysisAttributes.IN_DEGREE: self.nx_graph.in_degree(user_id),
            AnalysisAttributes.TOTAL_DEGREE: self.nx_graph.degree(user_id),
        }


# _____________________________________________________________________________
class FileManager:
    """
    Класс для управления файлами: сохранения и загрузки данных.
    Работает с объектами pathlib.Path для удобства и надежности.
    """

    def __init__(self, base_storage_dir: Path):  # Ожидает Path для корневой директории
        self.base_storage_dir = base_storage_dir
        self.base_storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            LogMessages.INFO_BASE_DIRECTORY_CREATED.format(
                directory_path=self.base_storage_dir
            )
        )

    def create_object_dir(self, obj_dir_name: str, parent_dir: Path):
        """
        Создает директорию для объекта внутри указанной родительской директории.

        Args:
            obj_dir_name (str): Имя папки.
            parent_dir (pathlib.Path): Родительская директория, где будет создана папка.

        Returns:
            pathlib.Path: Полный путь к созданной директории.
        """
        new_dir_path = parent_dir / obj_dir_name
        new_dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(
            LogMessages.INFO_DIRECTORY_CREATED.format(directory_path=new_dir_path)
        )
        return new_dir_path

    def save_chat_json(self, chat: Chat, data: List[Dict[str, Any]]) -> Path:
        """
        Сохраняет данные чата в JSON-файл в папке, соответствующей дате выгрузки.
        Возвращает полный Path к сохраненному файлу.
        """
        # Валидация входных параметров
        Mistaken.validate_all(chat, Chat, param_name="chat")
        Mistaken.validate_all(data, list, param_name="data")
        dir_datetime_date = datetime.now().strftime(DateFormat.DATE_FORMAT)
        # Создаем полный путь к папке с датой выгрузки
        logger.info(
            LogMessages.INFO_CHAT_STORAGE_PATH.format(storage_path=chat.storage_path)
        )
        dir_path = chat.storage_path / dir_datetime_date

        # Создаем директорию. exist_ok=True предотвращает ошибку, если папка уже существует
        dir_path.mkdir(parents=True, exist_ok=True)

        # Имя файла включает точное время, чтобы не перезаписывать выгрузки в один день
        file_timestamp = datetime.now().strftime(DateFormat.DATETIME_FORMAT)
        file_name = FileTemplates.CHAT_FILENAME.format(
            chat_id=chat.chat_id,
            social_account=chat.social_account.name,
            date=file_timestamp,
            extension=Extensions.CHAT_FILE_EXTENSION,
        )
        file_path = dir_path / file_name

        try:
            with open(
                file_path,
                PythonSettings.FILE_WRITE_MODE,
                encoding=PythonSettings.ENCODING_UTF8,
            ) as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(LogMessages.INFO_CHAT_DATA_SAVED.format(file_path=file_path))
            return file_path
        except IOError as e:
            logger.error(
                LogMessages.ERROR_CHAT_DATA_SAVING.format(chat_name=chat.name, error=e)
            )
            raise

    def load_chat_json(self, file_path: Path) -> List[Dict[str, Any]] | None:
        """
        Загружает данные из JSON-файла.
        """
        try:
            if not file_path.exists():
                logger.warning(
                    LogMessages.WARNING_FILE_NOT_FOUND.format(file_path=file_path)
                )
                return None

            with open(
                file_path,
                PythonSettings.FILE_READ_MODE,
                encoding=PythonSettings.ENCODING_UTF8,
            ) as f:
                data = json.load(f)
                logger.info(
                    LogMessages.INFO_DATA_LOADED_SUCCESS.format(
                        count=len(data), file_path=file_path
                    )
                )
                return data
        except json.JSONDecodeError as e:
            logger.error(
                LogMessages.ERROR_JSON_DECODE.format(file_path=file_path, error=e)
            )
        except IOError as e:
            logger.error(
                LogMessages.ERROR_FILE_READING.format(file_path=file_path, error=e)
            )
        return None

    def save_metrics_to_directory(
        self,
        analyzer: ChatAnalyzer,
        directory_path: Path,
        base_name: str,
        additional_name: str,
        extension: str,
    ) -> Path:

        try:
            # Создаем директорию если не существует
            directory_path.mkdir(parents=True, exist_ok=True)

            filename = FileTemplates.METRICS_FILENAME.format(
                base_name=base_name,
                additional_name=additional_name,
                date=datetime.now().strftime(DateFormat.TIME_FORMAT),
                extension=extension,
            )

            # Полный путь к файлу
            file_path = directory_path / filename

            # Получаем метрики и сохраняем
            metrics = analyzer.get_comprehensive_metrics()

            with open(
                file_path,
                PythonSettings.FILE_WRITE_MODE,
                encoding=PythonSettings.ENCODING_UTF8,
            ) as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)

            logger.info(LogMessages.INFO_METRICS_SAVED.format(file_path=file_path))
            return file_path

        except Exception as e:
            logger.error(
                LogMessages.ERROR_METRICS_SAVING.format(
                    directory_path=directory_path, error=e
                )
            )
            raise

    def create_pdf_report(
        self,
        metrics_data: dict,
        chat_name: str,
        phone_number: str,
        analysis_dir: Path,
        base_name: str,
        additional_name: str,
        extension: str,
        graph_file: str | None = None,
    ) -> Path:
        """
        Создает PDF-отчет из данных анализа чата.
        """
        try:
            # Получаем текущую дату-время для имени файла (во избежание перезаписи)
            report_date = datetime.now().strftime(DateFormat.DATETIME_FORMAT)

            # Формируем имя файла
            file_name = FileTemplates.PDF_REPORT_FILENAME.format(
                chat_name=chat_name,
                phone_number=phone_number,
                base_name=base_name,
                additional_name=additional_name,
                report_date=report_date,
                extension=extension,
            )

            # Сохраняем в указанную папку анализа
            analysis_dir.mkdir(parents=True, exist_ok=True)
            file_path = analysis_dir / file_name

            # Создаем PDF документ
            # Используем шрифт с поддержкой кириллицы

            pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
            doc = SimpleDocTemplate(str(file_path), pagesize=letter)
            styles = getSampleStyleSheet()
            styles["Normal"].fontName = "DejaVuSans"
            styles["Title"].fontName = "DejaVuSans"
            # Обновляем существующий стиль вместо добавления с тем же именем
            if "Heading2" in styles.byName:
                styles["Heading2"].fontName = "DejaVuSans"
            else:
                styles.add(
                    ParagraphStyle(
                        name="Heading2", parent=styles["Normal"], fontName="DejaVuSans"
                    )
                )
            story = []

            # Добавляем заголовок
            title = LogMessages.PDF_REPORT_TITLE.format(chat_name=chat_name)
            story.append(Paragraph(title, styles["Title"]))

            # Ссылка на граф (если есть)
            if graph_file:
                story.append(
                    Paragraph(
                        f"<a href='{graph_file}'>Открыть интерактивный граф</a>",
                        styles["Normal"],
                    )
                )

            # Раздел: Сводка
            summary = metrics_data.get(AnalysisAttributes.SUMMARY, {})
            story.append(Paragraph("Сводка", styles["Heading2"]))
            story.append(
                Paragraph(
                    f"Всего пользователей: {summary.get(AnalysisAttributes.TOTAL_USERS, 0)}",
                    styles["Normal"],
                )
            )
            story.append(
                Paragraph(
                    f"Всего взаимодействий: {summary.get(AnalysisAttributes.TOTAL_INTERACTIONS, 0)}",
                    styles["Normal"],
                )
            )
            story.append(
                Paragraph(
                    f"Всего сообщений: {summary.get(AnalysisAttributes.TOTAL_MESSAGES, 0)}",
                    styles["Normal"],
                )
            )

            def add_top_section(title: str, items: list):
                story.append(Paragraph(title, styles["Heading2"]))
                for user in (items or [])[:10]:
                    uname = user.get(AnalysisAttributes.USERNAME, "-")
                    val = user.get(AnalysisAttributes.VALUE, 0)
                    story.append(Paragraph(f"• {uname}: {val}", styles["Normal"]))

            activity = metrics_data.get(AnalysisAttributes.ACTIVITY_ANALYSIS, {})
            add_top_section(
                "Топ-активных (исходящие)",
                activity.get(AnalysisAttributes.TOP_ACTIVE_USERS, []),
            )
            add_top_section(
                "Топ-популярных (входящие)",
                activity.get(AnalysisAttributes.TOP_POPULAR_USERS, []),
            )
            add_top_section(
                "Топ-вовлечённых (total)",
                activity.get(AnalysisAttributes.TOP_ENGAGED_USERS, []),
            )

            replies = metrics_data.get(AnalysisAttributes.REPLY_ANALYSIS, {})
            add_top_section(
                "Кто больше отвечает", replies.get(AnalysisAttributes.TOP_REPLIERS, [])
            )
            add_top_section(
                "Кому больше отвечают",
                replies.get(AnalysisAttributes.TOP_REPLIED_TO, []),
            )

            questions = metrics_data.get(AnalysisAttributes.QUESTION_ANALYSIS, {})
            add_top_section(
                "Кто больше задаёт вопросов",
                questions.get(AnalysisAttributes.TOP_QUESTION_ASKERS, []),
            )

            centrality = metrics_data.get(AnalysisAttributes.CENTRALITY_METRICS, {})
            add_top_section(
                "Degree centrality",
                centrality.get(AnalysisAttributes.DEGREE_CENTRALITY, []),
            )
            add_top_section(
                "Betweenness centrality",
                centrality.get(AnalysisAttributes.BETWEENNESS_CENTRALITY, []),
            )
            add_top_section(
                "Closeness centrality",
                centrality.get(AnalysisAttributes.CLOSENESS_CENTRALITY, []),
            )
            add_top_section(
                "Eigenvector centrality",
                centrality.get(AnalysisAttributes.EIGENVECTOR_CENTRALITY, []),
            )

            doc.build(story)
            logger.info(LogMessages.INFO_PDF_REPORT_SAVED.format(file_path=file_path))
            return file_path
        except Exception as e:
            logger.error(LogMessages.ERROR_PDF_REPORT_CREATION.format(error=e))
            return None

    def send_pdf_report_via_email(
        self,
        pdf_path: Path,
        to_email: str,
        subject: str = "Chat Analysis Report",
        body: str = "Отчет во вложении.",
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        use_tls: bool = True,
    ) -> bool:
        """
        Отправляет PDF-отчет на указанный email, используя библиотеку email и smtplib.
        SMTP-параметры можно передать явно или через переменные окружения.
        """
        try:
            Mistaken.validate_all(pdf_path, Path, param_name="pdf_path")
            Mistaken.validate_all(to_email, str, param_name="to_email")
            if not pdf_path.exists():
                logger.error(
                    LogMessages.WARNING_FILE_NOT_FOUND.format(file_path=pdf_path)
                )
                return False

            smtp_host = smtp_host or os.getenv("SMTP_HOST")
            smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
            smtp_user = smtp_user or os.getenv("SMTP_USER")
            smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")

            Mistaken.validate_all(smtp_host, str, param_name="SMTP_HOST")

            msg = EmailMessage()
            msg["From"] = smtp_user if smtp_user else "no-reply@example.com"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body)

            with open(pdf_path, "rb") as f:
                data = f.read()
            msg.add_attachment(
                data,
                maintype="application",
                subtype="pdf",
                filename=pdf_path.name,
            )

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if use_tls:
                    server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(LogMessages.ERROR_PDF_REPORT_CREATION.format(error=e))
            return False


# _____________________________________________________________________________


class GraphCreator:
    """Создает граф из сырых данных чата"""

    def __init__(self):
        self.graph = Graph()
        self.message_to_user = {}  # Для связи message_id -> user_id
        self.username_to_user = {}  # Для поиска по упоминаниям

    @staticmethod
    def visualize_and_save_file(
        graph: Graph,
        directory_path: Path,
        base_name: str,
        additional_name: str,
        extension: str,
    ):
        """
        Визуализация графа и сохранение HTML в указанной директории
        """
        # Подготовка сети
        net = Network(
            height=GraphVisualizationSettings.NETWORK_HEIGHT,
            width=GraphVisualizationSettings.NETWORK_WIDTH,
            bgcolor=GraphVisualizationSettings.NETWORK_BGCOLOR,
            font_color=GraphVisualizationSettings.NETWORK_FONT_COLOR,
            directed=GraphVisualizationSettings.NETWORK_DIRECTED,
            notebook=GraphVisualizationSettings.NETWORK_NOTEBOOK,
        )

        # Добавляем узлы
        for user_id, knot in graph.users.items():
            is_anon = str(user_id).startswith("anon_")
            color = (
                GraphVisualizationSettings.ANONYMOUS_USER_COLOR
                if is_anon
                else GraphVisualizationSettings.REGULAR_USER_COLOR
            )
            shape = (
                GraphVisualizationSettings.ANONYMOUS_USER_SHAPE
                if is_anon
                else GraphVisualizationSettings.REGULAR_USER_SHAPE
            )
            net.add_node(
                user_id,
                label=knot.username,
                color=color,
                shape=shape,
                size=25,
                title=f"ID: {user_id}, name: {knot.username}",
            )

        # Добавляем рёбра
        for edge in graph.edges.values():
            color = {
                EdgeType.MESSAGE: GraphVisualizationSettings.MESSAGE_COLOR,
                EdgeType.REPLY: GraphVisualizationSettings.REPLY_COLOR,
                EdgeType.MENTION: GraphVisualizationSettings.MENTION_COLOR,
                EdgeType.REACTION: GraphVisualizationSettings.REACTION_COLOR,
            }.get(
                edge.edge_type,
            )

            title = str(edge.edge_type.name)
            if getattr(edge, "content", None):
                title += f": {edge.content}"

            net.add_edge(
                edge.from_user.user_id,
                edge.to_user.user_id,
                color=color,
                width=GraphVisualizationSettings.EDGE_WIDTH,
                title=title,
                arrows=GraphVisualizationSettings.ARROWS_DIRECTION,
            )

        # Формирование пути к файлу
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.exception("Не удалось создать директорию %s", directory_path)
            raise

        # Составляем имя файла
        # Обрезаем пробелы и небезопасные символы в именах

        filename = FileTemplates.GRAPH_VISUALIZATION.format(
            base_name=base_name,
            additional_name=additional_name,
            graph_date=datetime.now().strftime(DateFormat.TIME_FORMAT),
            extension=extension,
        )
        file_path = directory_path / filename

        # Сохраняем HTML без автоматического открытия (pyvis.write_html)
        try:
            net.write_html(str(file_path))
        except Exception:
            logger.exception("Ошибка при сохранении файла визуализации %s", file_path)
            raise

        # # Открываем в браузере отдельно
        # webbrowser.open(f"{GraphVisualizationSettings.BROWSER_URL_PREFIX}{file_path.resolve()}")
        return file_path

    def process_data(self, messages: list) -> Graph:
        """Основной метод обработки данных"""
        for msg in messages:
            user_id = msg.get(MessageKeys.USER_ID)
            username = msg.get(MessageKeys.AUTHOR_NAME, MessageKeys.UNKNOWN_AUTHOR)
            message_id = msg.get(MessageKeys.MESSAGE_ID)

            # Для анонимных пользователей генерируем отрицательный ID
            if user_id is None:
                user_id = -abs(message_id)  # Отрицательный ID

            # Создаем пользователя если его нет
            if user_id not in self.graph.users:
                if user_id < 0:  # Анонимный пользователь
                    user_name = f"Anonymous_{abs(user_id)}"  # Без знака минус
                else:
                    user_name = username

                user = self.graph.add_user(user_id, user_name)
                self.username_to_user[user_name.lower()] = user

            # Запоминаем связь сообщение -> пользователь
            self.message_to_user[message_id] = user_id
            self.process_message(msg)

        return self.graph

    def process_message(self, msg: dict) -> None:
        """Обрабатывает одно сообщение и его связи"""
        sender_id = self.get_or_create_sender(msg)

        # Обрабатываем reply_to связь
        if msg[MessageKeys.REPLY_TO_ID] is not None:
            self.process_reply(sender_id, msg)

        # Обрабатываем mentions (@username)
        self.process_mentions(sender_id, msg[MessageKeys.MESSAGE_TEXT])

        # Обрабатываем реакции, если есть
        self.process_reactions(sender_id, msg)

    def get_or_create_sender(self, msg: dict) -> int:
        """Возвращает или создаёт отправителя сообщения (user_id)"""
        user_id = msg.get(MessageKeys.USER_ID)
        username = msg.get(MessageKeys.AUTHOR_NAME) or "Anonymous"
        message_id = msg.get(MessageKeys.MESSAGE_ID)

        # Отладочная информация (удалите или замените логированием в продакшне)
        print(f"Message keys: {list(msg.keys())}")
        print(f"User ID: {user_id}, Username: {username}")
        if msg.get("chat") is not None:
            print(f"Chat data: {msg.get('chat')}")
        if msg.get("from") is not None:
            print(f"From data: {msg.get('from')}")

        # Если user_id отсутствует, но есть объект чата — используем данные чата
        if user_id is None and (
            ChatObjectAttributes.ID in msg or msg.get("chat") is not None
        ):
            # пытаемся получить id и название чата из разных полей
            chat_field = msg.get("chat") or {}
            user_id = (
                msg.get(ChatObjectAttributes.ID)
                or chat_field.get(ChatObjectAttributes.ID)
                or None
            )
            username = (
                msg.get(ChatObjectAttributes.TITLE)
                or msg.get(ChatObjectAttributes.NAME)
                or chat_field.get(ChatObjectAttributes.TITLE)
                or chat_field.get(ChatObjectAttributes.NAME)
                or username
            )
            print(f"Using chat as sender: ID={user_id}, Name={username}")

        # Если user_id всё ещё отсутствует — создаём анонимного пользователя с отрицательным уникальным ID
        if user_id is None:
            # безопасно получить целочисленный base для генерации отрицательного id
            try:
                anon_base = (
                    abs(int(message_id)) if message_id is not None else abs(id(msg))
                )
            except (TypeError, ValueError):
                anon_base = abs(id(msg))
            user_id = -anon_base
            print(f"Creating anonymous user: ID={user_id}")

            if user_id not in self.graph.users:
                user = self.graph.add_user(user_id, f"Anonymous_{anon_base}")
                # сохраняем сопоставление по нормализованному имени
                self.username_to_user[username.lower()] = user
            return user_id

        # Приводим к целому типу и нормализуем username
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            # В редком случае некорректного user_id — fallback в анонимного
            try:
                anon_base = (
                    abs(int(message_id)) if message_id is not None else abs(id(msg))
                )
            except (TypeError, ValueError):
                anon_base = abs(id(msg))
            user_id = -anon_base
            print(f"Invalid user_id, fallback to anonymous: ID={user_id}")

            if user_id not in self.graph.users:
                user = self.graph.add_user(user_id, f"Anonymous_{anon_base}")
                self.username_to_user[username.lower()] = user
            return user_id

        # Гарантируем, что username непустой строкой
        username = username or f"user_{user_id}"

        # Добавляем пользователя в граф при отсутствии и сохраняем сопоставление по имени
        if user_id not in self.graph.users:
            user = self.graph.add_user(user_id, username)
            self.username_to_user[username.lower()] = user

        return user_id

    def process_reply(self, sender_id: int, msg: dict) -> None:
        """Обрабатывает ответ на сообщение"""
        reply_to_msg_id = msg.get(MessageKeys.REPLY_TO_ID)
        if reply_to_msg_id and reply_to_msg_id in self.message_to_user:
            receiver_id = self.message_to_user[reply_to_msg_id]
            if receiver_id is not None:
                self.graph.add_interaction(
                    edge_type=EdgeType.REPLY,
                    from_user_id=sender_id,  # int
                    to_user_id=receiver_id,  # int
                    content=msg.get(MessageKeys.MESSAGE_TEXT, ""),
                )

    def process_mentions(self, sender_id: int, message_text: str) -> None:
        """Обрабатывает упоминания в тексте"""
        for mention in self.extract_mentions(message_text):
            mentioned_user = self.username_to_user.get(mention.lower())
            if mentioned_user:
                self.graph.add_interaction(
                    edge_type=EdgeType.MENTION,
                    from_user_id=sender_id,  # int
                    to_user_id=mentioned_user.user_id,  # int
                    content=f"@{mention}",
                )

    def process_reactions(self, sender_id: int, msg: dict) -> None:
        """Добавляет связи реакций (реагирующий -> автор сообщения)"""
        reactions = msg.get(MessageKeys.REACTIONS)
        if not reactions:
            return
        author_id = sender_id
        for reactor_name in reactions:
            # Ищем пользователя по username
            mentioned_user = self.username_to_user.get(str(reactor_name).lower())
            if mentioned_user:
                self.graph.add_interaction(
                    edge_type=EdgeType.REACTION,
                    from_user_id=mentioned_user.user_id,
                    to_user_id=author_id,
                    content=str(reactor_name),
                )

    @staticmethod
    def extract_mentions(text: str) -> list:
        """Извлекает упоминания из текста"""
        import re

        return [m.lower() for m in re.findall(r"@(\w+)", text)]
