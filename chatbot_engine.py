import json
from rapidfuzz import fuzz

from db import get_connection


class ChatbotEngine:

    def __init__(self):

        self.db = get_connection()
        self.cursor = self.db.cursor(dictionary=True)

    
    # SESSION MANAGEMENT
    
    def create_session_if_not_exists(self, session_id, user_id=None):

        self.cursor.execute(
            """
            SELECT session_id
            FROM chat_sessions
            WHERE session_id = %s
            """,
            (session_id,)
        )

        session = self.cursor.fetchone()

        if not session:

            self.cursor.execute(
                """
                INSERT INTO chat_sessions
                (
                    session_id,
                    user_id,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    'active'
                )
                """,
                (
                    session_id,
                    user_id
                )
            )

            self.db.commit()

    # CHAT MESSAGE STORAGE

    def save_message(
        self,
        session_id,
        sender,
        message
    ):

        self.cursor.execute(
            """
            INSERT INTO chat_messages
            (
                session_id,
                sender,
                message
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                session_id,
                sender,
                message
            )
        )

        self.db.commit()

    # CHAT LOGS

    def save_log(
        self,
        session_id,
        intent_id,
        question,
        response,
        response_type
    ):

        self.cursor.execute(
            """
            INSERT INTO chat_logs
            (
                session_id,
                intent_id,
                user_question,
                bot_response,
                response_type
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                session_id,
                intent_id,
                question,
                response,
                response_type
            )
        )

        self.db.commit()

    # FAQ SEARCH

    def get_faq_answer(self, question):

        self.cursor.execute(
            """
            SELECT
                faq_id,
                question,
                answer
            FROM chat_faqs
            WHERE status = 1
            """
        )

        faqs = self.cursor.fetchall()

        best_score = 0
        best_answer = None

        for faq in faqs:

            score = fuzz.token_sort_ratio(
                question.lower(),
                faq["question"].lower()
            )

            if score > best_score:

                best_score = score
                best_answer = faq["answer"]

        if best_score >= 75:
            return best_answer

        return None

    # COURSE MATCHING

    def get_course_response(
        self,
        session_id,
        question
    ):

        self.cursor.execute(
            """
            SELECT
                keyword,
                course_id
            FROM chat_course_keywords
            """
        )

        keywords = self.cursor.fetchall()

        q = question.lower()

        for item in keywords:

            if item["keyword"].lower() in q:

                course_id = item["course_id"]

                self.cursor.execute(
                    """
                    SELECT *
                    FROM courses
                    WHERE id = %s
                    """,
                    (course_id,)
                )

                course = self.cursor.fetchone()

                if not course:
                    return None

                self.update_context(
                    session_id,
                    course_id
                )

                response = f"""
Course: {course['title']}

Duration: {course['duration']}
Mode: {course['mode']}
Language: {course['language']}
Category: {course['category']}

Description:
{course['description']}
"""

                return response

        return None

    # CONTEXT UPDATE

    def update_context(
        self,
        session_id,
        course_id
    ):

        self.cursor.execute(
            """
            INSERT INTO chat_context
            (
                session_id,
                current_course_id
            )
            VALUES
            (
                %s,
                %s
            )
            ON DUPLICATE KEY UPDATE
            current_course_id = VALUES(current_course_id)
            """,
            (
                session_id,
                course_id
            )
        )

        self.db.commit()

           # GET CONTEXT

    def get_context(
        self,
        session_id
    ):

        self.cursor.execute(
            """
            SELECT current_course_id
            FROM chat_context
            WHERE session_id = %s
            """,
            (session_id,)
        )

        return self.cursor.fetchone()

    # HANDLE FOLLOW-UP QUESTIONS

    def handle_followup(
        self,
        session_id,
        question
    ):

        context = self.get_context(session_id)

        if not context:
            return None

        course_id = context["current_course_id"]

        self.cursor.execute(
            """
            SELECT *
            FROM courses
            WHERE id = %s
            """,
            (course_id,)
        )

        course = self.cursor.fetchone()

        if not course:
            return None

        q = question.lower()

        if "duration" in q:
            return f"Duration: {course['duration']}"

        if "mode" in q:
            return f"Mode: {course['mode']}"

        if "language" in q:
            return f"Language: {course['language']}"

        if "fee" in q or "price" in q:
            return f"Course Fee: {course['price']}"

        return None

    # INTENT RESPONSE

    def get_intent_response(self, question):

        self.cursor.execute(
            """
            SELECT
                ck.keyword,
                ck.intent_id
            FROM chat_keywords ck
            JOIN chat_intents ci
                ON ck.intent_id = ci.intent_id
            WHERE ci.status = 1
            """
        )

        keywords = self.cursor.fetchall()

        q = question.lower()

        for item in keywords:

            if item["keyword"].lower() in q:

                self.cursor.execute(
                    """
                    SELECT response_text
                    FROM chat_responses
                    WHERE intent_id = %s
                    LIMIT 1
                    """,
                    (item["intent_id"],)
                )

                response = self.cursor.fetchone()

                if response:

                    return {
                        "intent_id": item["intent_id"],
                        "response": response["response_text"]
                    }

        return None
    
    # FALLBACK

    def get_fallback(self):

        self.cursor.execute(
            """
            SELECT response_text
            FROM chat_fallbacks
            ORDER BY RAND()
            LIMIT 1
            """
        )

        row = self.cursor.fetchone()

        if row:
            return row["response_text"]

        return "Sorry, I couldn't understand your question."

    # UNANSWERED QUESTIONS

    def save_unanswered(
        self,
        session_id,
        question
    ):

        self.cursor.execute(
            """
            INSERT INTO chat_unanswered_questions
            (
                session_id,
                question
            )
            VALUES
            (
                %s,
                %s
            )
            """,
            (
                session_id,
                question
            )
        )

        self.db.commit()

    # MAIN PROCESS METHOD

    def process(
        self,
        session_id,
        question,
        user_id=None
    ):

        self.create_session_if_not_exists(
            session_id,
            user_id
        )

        self.save_message(
            session_id,
            "user",
            question
        )

        faq_response = self.get_faq_answer(question)

        if faq_response:

            self.save_message(
                session_id,
                "bot",
                faq_response
            )

            self.save_log(
                session_id,
                None,
                question,
                faq_response,
                "faq"
            )

            return {
                "success": True,
                "response": faq_response,
                "response_type": "faq",
                "session_id": session_id
            }

        course_response = self.get_course_response(
            session_id,
            question
        )

            # MAIN PROCESS METHOD

    def process(
        self,
        session_id,
        question,
        user_id=None
    ):

        self.create_session_if_not_exists(
            session_id,
            user_id
        )

        self.save_message(
            session_id,
            "user",
            question
        )

        # FAQ RESPONSE

        faq_response = self.get_faq_answer(question)

        if faq_response:

            self.save_message(
                session_id,
                "bot",
                faq_response
            )

            self.save_log(
                session_id,
                None,
                question,
                faq_response,
                "faq"
            )

            return {
                "success": True,
                "response": faq_response,
                "response_type": "faq",
                "session_id": session_id
            }

        # COURSE RESPONSE

        course_response = self.get_course_response(
            session_id,
            question
        )

        if course_response:

            self.save_message(
                session_id,
                "bot",
                course_response
            )

            self.save_log(
                session_id,
                None,
                question,
                course_response,
                "course"
            )

            return {
                "success": True,
                "response": course_response,
                "response_type": "course",
                "session_id": session_id
            }

        # FOLLOW-UP RESPONSE

        followup_response = self.handle_followup(
            session_id,
            question
        )

        if followup_response:

            self.save_message(
                session_id,
                "bot",
                followup_response
            )

            self.save_log(
                session_id,
                None,
                question,
                followup_response,
                "context"
            )

            return {
                "success": True,
                "response": followup_response,
                "response_type": "context",
                "session_id": session_id
            }

        # INTENT RESPONSE

        intent_response = self.get_intent_response(
            question
        )

        if intent_response:

            response_text = intent_response["response"]

            self.save_message(
                session_id,
                "bot",
                response_text
            )

            self.save_log(
                session_id,
                intent_response["intent_id"],
                question,
                response_text,
                "intent"
            )

            return {
                "success": True,
                "response": response_text,
                "response_type": "intent",
                "session_id": session_id
            }

        # FALLBACK RESPONSE

        fallback_response = self.get_fallback()

        self.save_unanswered(
            session_id,
            question
        )

        self.save_message(
            session_id,
            "bot",
            fallback_response
        )

        self.save_log(
            session_id,
            None,
            question,
            fallback_response,
            "fallback"
        )

        return {
            "success": True,
            "response": fallback_response,
            "response_type": "fallback",
            "session_id": session_id
        }