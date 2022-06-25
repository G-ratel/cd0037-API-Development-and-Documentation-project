from array import array
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response

    def categoryDic():
        categories = Category.query.all();

        resultData = {}
        for category in categories:
            resultData[category.id] = category.type
        return resultData


    @app.route('/categories')
    def get_categories():

        return jsonify(
            { "categories" : categoryDic() }
        )

    
    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        
        questions = Question.query.all();
        formatted_questions = [question.format() for question in questions]

        return jsonify(
            {
                "categories":categoryDic(),
                'questions': formatted_questions[start:end],
                'totalQuestions':len(formatted_questions),
                'currentCategory': Category.query.get(questions[0].category).type if len(questions)>0 else None
            }
        )

    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
    
        try:
            question = Question.query.filter_by(id=question_id).one()
            Question.delete(question);

            return jsonify(
                {
                    "message":'Question deleted successfully'
                }
            )
        except:
            abort(404)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        question_data = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')

        if(question_data==None): abort(400, {"message":"Question required"}) 
        if(answer==None): abort(400, {"message":"Answer required"}) 
        if(difficulty==None): abort(400, {"message":"Question difficulty required"}) 
        if(category==None): abort(400, {"message":"Category required"}) 

        try:
            question = Question(question=question_data, answer=answer, difficulty=difficulty, category=category)
            Question.insert(question)
            return jsonify(
                {"message":'Question added successfully'}
            )
        except Exception as e: 
            print(e)
            abort(400)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        searchTerm = body.get('searchTerm')
        search = "%{}%".format(searchTerm)

        try:
            search_query = Question.query.filter(Question.question.ilike(search))
            questions = search_query.all();
            formatted_questions = [question.format() for question in questions]
            
            return jsonify({
                'success': True,
                'questions':formatted_questions,
                'totalQuestions':search_query.count(),
                'currentCategory': Category.query.get(questions[0].category).type if len(questions)>0 else None
            });
        except Exception as e: 
            print(e)
            abort(400)

    @app.route('/categories/<category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        try:
            questions = Question.query.filter(Question.category==category_id).all();
            formatted_questions = [question.format() for question in questions]
            return jsonify({
                'success': True,
                'questions':formatted_questions,
            });
        except Exception as e: 
            print(e)
            abort(400)

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        body = request.get_json()
        previous_questions = body.get('previous_questions', [],)
        quiz_category = body.get('quiz_category')

        try:
            question = Question.query.filter(
                Question.category==quiz_category['id'], 
                Question.id.not_in(previous_questions)
            ).order_by(func.random()).first();

            return jsonify({
                'success': True,
                'question':question.format(),
            });
        except Exception as e: 
            print(e)
            abort(400)

    @app.errorhandler(404)
    def not_found(error):
        message=None 
        if('message' in error.description):
            message = error.description['message']

        return jsonify({
            'success': False,
            'error':404,
            'message': message if message!=None else 'Resource not found',
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        message=None 
        if('message' in error.description):
            message = error.description['message']

        return jsonify({
            'success': False,
            'error': 400,
            'message': message if message!=None else 'Bad request',
        }), 400

    return app

