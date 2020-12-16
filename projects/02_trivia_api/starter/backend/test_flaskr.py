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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','test','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # Sample new question 
        self.new_question = {
            'question': 'What is the highest mountain in the world?',
            'answer': 'Mount Everest',
            'category': 3,
            'difficulty score': 3
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    ##### Tests for getting categories ####
    def test_get_categories(self):
        """ This test represents successfully getting the list of categories """
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_404_categories_not_found(self):
        """ This test represents unsuccessful result for getting the categories """
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    ##### Tests for getting paginated questions ####
    def test_get_questions(self):
        """ This test represents successfully getting the list of questions with pagination (every 10 questions)
            Checks to make sure it returns a list of questions, number of total questions, 
            current category and categories."""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        questions = Question.query.order_by(Question.id).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], len(questions))
        self.assertTrue(data['categories'])
        
    def test_404_no_question_found(self):
        """ This test represents not finding any questions when getting paginated questions """
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    ##### Tests for deleting a question ####
    def test_delete_question(self):
        """ This test represents deleting a question """
        res = self.client().delete('/questions/6')
        data = json.loads(res.data)

        questions = Question.query.order_by(Question.id).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], len(questions))

    def test_422_question_doesnt_exist_to_delete(self):
        """ This test represents if the question does not exist that is to be deleted """
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    ##### Tests for creating a new question ####
    def test_create_new_question(self):
        """ This test represents adding a new question """
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_405_not_allowed_to_create_new_question(self):
        """ This test represents if the user is not allowed to create a new question """
        res = self.client().post('/questions/12', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    ##### Tests for searching for a term in the questions ####
    def test_get_question_search_with_results(self):
        """ This test represents if successfully getting questions using search term """
        res = self.client().post('/questions', json={'searchTerm': 'Mountain'})
        data = json.loads(res.data)

        questions = Question.query.all
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])


    def test_get_question_search_without_results(self):
        """ This test represents if there are no results for the search """
        res = self.client().post('/questions', json={'searchTerm': 'applejacks'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']),0)
        self.assertEqual(data['total_questions'], 0)

    ##### Tests to get questions based on the category ####
    def test_get_questions_by_category_with_questions(self):
        """ This test represents successfully getting the questions based on the selected
        category """
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'],1)    

    def test_get_questions_by_category_without_questions(self):
        """ This test represents if there are no questions for that category """
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'],1000)  

    ##### Tests to play game ####
    def test_play_game(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()