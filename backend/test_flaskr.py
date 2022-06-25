import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', '12345','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_can_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        categories = data['categories'];

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(categories)
        self.assertEqual(categories['2'], 'Art')

    def test_can_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['categories'])
        self.assertIsNotNone(data['totalQuestions'])
        self.assertGreater(len(data['questions']), 0)

    def test_can_delete_question(self):
        question = Question(question='Hey', answer='a', difficulty=4, category=1)
        Question.insert(question)
        questionId = question.id;

        res = self.client().delete('/questions/' + str(questionId))

        self.assertEqual(res.status_code, 200)

    def test_cannot_delete_non_existing_question(self):
        question = Question(question='Hey', answer='a', difficulty=4, category=1)
        Question.insert(question)
        questionId = question.id;

        self.client().delete('/questions/' + str(questionId))
        res = self.client().delete('/questions/' + str(questionId))

        self.assertEqual(res.status_code, 404)
        
    def test_can_add_questions(self):
        res = self.client().post('/questions', json={
            "question": "How are you?",
            "answer": "abc",
            "difficulty": 4,
            "category": 5
        })

        self.assertEqual(res.status_code, 200)
       
    def test_cannot_add_question_without_category(self):
        res = self.client().post('/questions', json={
            "question": "How are you?",
            "answer": "abc",
            "difficulty": 4
        })

        self.assertEqual(res.status_code, 400)
       
    def test_can_search_question(self):
        question = Question(question='Your Hobby is Orange, Sleep', answer='a', difficulty=4, category=1)
        Question.insert(question)
        
        res = self.client().post('/questions/search', json={
            "searchTerm": "orange"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['questions']), 0)

    def test_can_get_question_by_id(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['questions']), 0)    

    def test_can_get_quizzes(self):
        res = self.client().post('/quizzes', json={
            "previous_questions":[21],
            "quiz_category": {
            "id":"5",
            "type": "Entertainment"
        }})

        self.assertEqual(res.status_code, 200)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()