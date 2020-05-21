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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs

  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  @app.after_request
  def after_request(response):
      # response.headers.add( 'Access-Control-Allow-Origin', '*')
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
      return response

  

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow

  '''

  # @app.route('/')
  # def index():
  #   return "<h1>Hello, Trivia!<h1/>"
  '''
  
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
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
  





  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  def questions_pagination(request,selection):
    page = request.args.get('page', 1 , type = int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  
  @app.route('/questions', methods = ['GET'])
  def get_all_questions():

    questions = Question.query.order_by(Question.id).all()
    current_questions = questions_pagination(request= request, selection=questions)

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
      'categories' : categories_list
    })
    

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>' , methods = ['DELETE'])
  def delete_questoin(question_id):

    print(question_id)
    question_to_delete = Question.query.filter(Question.id == question_id).one_or_none()
    if question_to_delete is None:
      abort(422)
    
    question_to_delete.delete()
    return jsonify({
      'success': True,
      'deleted': question_id
    })


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods= ['POST'])
  def create_question():

    data = request.get_json()
    print(data['difficulty'])
    try:
      new_question = Question (
        question = data['question'],
        answer = data['answer'],
        category = data['category'],
        difficulty = (data['difficulty'])
      )
    except:
      abort(404)
    
    new_question.insert()

    questions = Question.query.order_by(Question.id).all()
    current_questions = questions_pagination(request=request , selection= questions)

    return jsonify({
        'success': True,
        'created': new_question.id,
        'questions': current_questions,
        'total_questions': len(questions)
      })
    

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods = ['post'])
  def search_for_question():

    data = request.get_json()

    search_term = data.get('searchTerm', None)

    questions_list = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
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
        'current_category' : categories_list
      })


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def questoins_based_on_category(category_id):

    current_category = Category.query.get(category_id)
    current_questoins = Question.query.filter_by(category = category_id).all()
    print(current_questoins)

    if current_questoins is None:
      abort(404)

    questions_found = questions_pagination(request= request , selection= current_questoins)

    # questions_found = []
    # for question in current_questoins:
    #   questions_found.append({
    #       'id': question.id,
    #       'question': question.question,
    #       'answer': question.answer,
    #       'category': question.category,
    #       'difficulty': question.difficulty
    #   })
    # questions_list = questions_pagination(request= request, selection= questions_found)
    
    if len(questions_found) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions_found,
      'total_questions': len(current_questoins),
      'current_category' : category_id
      })




  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play():

    data = request.get_json()
    print(data)
    previous_questions = data.get('previous_questions', None)
    quiz_category = data.get('quiz_category', None)

    try:
      if not previous_questions:
        if quiz_category:
          questions_list = Question.query.filter(Question.category == quiz_category['id']).all()
        else:
          questions_list = Question.query.all()    
      else:
        if quiz_category:
          questions_list = Question.query.filter(Question.category == quiz_category['id']).filter(Question.id.notin_(previous_questions)).all()
        else:
          questions_list = Question.query.filter(Question.id.notin_(previous_questions)).all()

      questions_formatted = [question.format() for question in questions_list]
      if len(questions_formatted) == 0:
        abort(404)
      random_question = questions_formatted[random.randint(0, len(questions_formatted))]
    except:
      abort(404)
    # for q in questions_formatted:
    #   print(q)
    #   print('##')
    # print('#########################')
    # print(questions_formatted[1])
    # # random_question = questions_formatted[0]
    
    return jsonify({
        'success': True,
        'question': random_question
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
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
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "method not allowed"
      }), 400

  return app

    