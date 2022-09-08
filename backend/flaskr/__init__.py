from crypt import methods
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, collection):
    page = request.args.get(request, 1,type=int)
    start = (page - 1) * 10
    end =  start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in collection]
    formatted_questions = questions[start:end]
    
    return formatted_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs!!!!!!!!!
    """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        category_list = {}
        try:
            for category in categories:
                category_list.update({category.id : category.type })
            return jsonify ({
                'success': True,
                'categories': category_list
            })
        except:
            abort(400)



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_question():
        categories = Category.query.all()
        questions = Question.query.all() 
        try:
            category_list = {}
            for category in categories:
                category_list.update({category.id : category.type })
            formatted_questions = [question.format() for question in questions]
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * 10
            end = start + QUESTIONS_PER_PAGE
            return jsonify ({
                'success': True,
                'currentCategory': 'All',
                'categories': category_list,
                'questions': formatted_questions[start:end],
                'totalQuestions': len(questions)
            })
        except:
            abort(400)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    
    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        
        current_question = Question.query.filter(Question.id == question_id).one_or_none()
        if current_question is None:
            abort(404)
        try:
            current_question.delete()
            return jsonify({
                'success': True,
                'message': 'deleted'
            })
        except:
            abort(400)
        
        

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods = ['POST'])
    def add_question():
        body = request.get_json()
        try:
            if body.get('question'):
                new_question_text = body.get('question')
                new_question_answer = body.get('answer')
                new_question_category = body.get('category')
                new_question_difficulty = body.get('difficulty')

                new_question = Question(question=new_question_text, answer=new_question_answer, category=new_question_category, difficulty=new_question_difficulty)
                new_question.insert()
                
                return jsonify ({
                    'success':True
                })
                
            else:
                search_term = body.get('searchTerm')
                search_term = "%{0}%".format(search_term)
                responses = Question.query.filter(Question.question.ilike(search_term)).all()
                if responses is None:
                    abort(404)
                responses = [response.format() for response in responses] 
                count = (len(responses))
                
                return jsonify ({
                    'success':True,
                    'questions':responses,
                    'totalQuestions':count,
                    'currentCategory':'All'
                    
                })
        except:
            abort(400)
    
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions')
    def get_questions(id):
        categories = Category.query.all()
        formatted_categories = [case.format() for case in categories] 
        try:
            questions = Question.query.filter(Question.category == id).all()
            current_category = Category.query.get(id)
            category_name = current_category.type
            if category_name is None:
                abort(404)
            
                
            formatted_questions = paginate(request, questions)
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * 10
            end = start + QUESTIONS_PER_PAGE
            return jsonify ({
                'success': True,
                'currentCategory': category_name,
                'questions': formatted_questions[start:end],
                'totalQuestions': len(Question.query.all())
            })
        except:
            abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_game():
        body = request.get_json()
        try:
            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
    
            official_questions = Question.query.filter(Question.category == quiz_category['id']).all()
   
            official_questions = [official_question.id for official_question in official_questions]

            question = Question.query.get(random.choice(official_questions))
            question = question.format()
            print(question)
            return jsonify ({
                    'success': True,
                    'question': question
                })
        except:
            abort(400)
        
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify ({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
        
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify ({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400
        
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify ({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422
    
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify ({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500
        
    
    return app

