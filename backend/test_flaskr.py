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
        self.database_path = "postgresql://{}:{}@{}:{}/{}".format('postgres', 'jimi', 'localhost', '5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            'question' : 'Who are you?',
            'answer': 'I am you',
            'category':'1',
            'difficulty':'5'
        }
        self.quiz = {
            'quiz_category': {'type':'science', 'id':'5'},
            'previous_questions': [2, 4, 6]
        }
        self.search = {
            'searchTerm':'soccer'
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
    def test_405_if_categories_method_is_wrong(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Method not allowed')
        

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])
        
    def test_405_if_get_questions_method_is_wrong(self):
        res = self.client().patch('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Method not allowed')

    def test_delete_question(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
        
        current_question = Question.query.filter(Question.id == 5).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['message'])
    
    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')


    def test_add_questions(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_405_if_add_questions_method_is_wrong(self):
        res = self.client().delete('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Method not allowed')
    
    
    def test_search_questions(self):
        res = self.client().post('/questions', json=self.search)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    def test_400_if_searched_question_is_absent(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        responses = None
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Bad request')

    
    def test_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        
        questions = Question.query.filter(Question.category == 1).all()
        current_category = Category.query.get(1)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['currentCategory'], True)
        self.assertTrue(data['questions'], True)
        self.assertTrue(data['totalQuestions'], True)
        
        
    def test_400_if_category_is_wrong(self):
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Bad request')
    
    
    def test_quizzes(self):
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        
    def test_quizzes_wrong_method(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Method not allowed')
        
    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()