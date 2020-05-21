import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        # response.headers.add( 'Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,PATCH,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():

        categories = Category.query.order_by(Category.id).all()
        if categories is None:
            abort(404)
        print(categories)
        categories_list = []
        for category in categories:
            categories_list.append(
                category.type
            )

        return jsonify({
            'success': True,
            'categories': categories_list
        })

    def questions_pagination(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route('/questions', methods=['GET'])
    def get_all_questions():

        questions = Question.query.order_by(Question.id).all()
        current_questions = questions_pagination(
            request=request, selection=questions)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.id).all()
        if categories is None:
            abort(404)

        categories_list = []
        for category in categories:
            categories_list.append(
                category.type
            )

        return jsonify({

            'success': True,
            'questions': current_questions,
            'number_of_total_questions': len(questions),
            'current_category': categories_list,
            'categories': categories_list
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questoin(question_id):

        print(question_id)
        question_to_delete = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question_to_delete is None:
            abort(422)

        question_to_delete.delete()
        return jsonify({
            'success': True,
            'deleted': question_id
        })

    @app.route('/questions', methods=['POST'])
    def create_question():

        data = request.get_json()
        print(data['difficulty'])
        try:
            new_question = Question(
                question=data['question'],
                answer=data['answer'],
                category=data['category'],
                difficulty=(data['difficulty'])
            )
        except:
            abort(404)

        new_question.insert()

        questions = Question.query.order_by(Question.id).all()
        current_questions = questions_pagination(
            request=request, selection=questions)

        return jsonify({
            'success': True,
            'created': new_question.id,
            'questions': current_questions,
            'total_questions': len(questions)
        })

    @app.route('/questions/search', methods=['post'])
    def search_for_question():

        data = request.get_json()

        search_term = data.get('searchTerm', None)

        questions_list = Question.query.filter(
            Question.question.ilike('%' + search_term + '%')).all()
        questions_found = [question.format() for question in questions_list]

        if len(questions_list) == 0:
            abort(404)

        all_questions_count = Question.query.count()
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        categories_list = []
        for category in categories:
            categories_list.append(
                category.type
            )

            return jsonify({
                'success': True,
                'questions': questions_found,
                'total_questions': all_questions_count,
                'current_category': categories_list
            })

    @app.route('/categories/<int:category_id>/questions')
    def questoins_based_on_category(category_id):

        current_category = Category.query.get(category_id)
        current_questoins = Question.query.filter_by(
            category=category_id).all()
        print(current_questoins)

        if current_questoins is None:
            abort(404)

        questions_found = questions_pagination(
            request=request, selection=current_questoins)

        if len(questions_found) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions_found,
            'total_questions': len(current_questoins),
            'current_category': category_id
        })

    @app.route('/quizzes', methods=['POST'])
    def play():

        data = request.get_json()
        print(data)
        previous_questions = data.get('previous_questions', None)
        quiz_category = data.get('quiz_category', None)

        try:
            if not previous_questions:
                if quiz_category:
                    questions_list = Question.query.filter(
                        Question.category == quiz_category['id']).all()
                else:
                    questions_list = Question.query.all()
            else:
                if quiz_category:
                    questions_list = Question.query.filter(
                      Question.category == quiz_category['id']).filter(
                        Question.id.notin_(previous_questions)).all()
                else:
                    questions_list = Question.query.filter(
                        Question.id.notin_(previous_questions)).all()

            questions_formatted = [question.format()
                                   for question in questions_list]
            if len(questions_formatted) == 0:
                abort(404)
            random_question = questions_formatted[random.randint(
                0, len(questions_formatted))]
        except:
            abort(404)

        return jsonify({
            'success': True,
            'question': random_question
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 400

    return app
