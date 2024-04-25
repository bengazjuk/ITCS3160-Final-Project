## ITCS 3160-0002, Spring 2024
## Marco Vieira, marco.vieira@charlotte.edu
## University of North Carolina at Charlotte
 
## IMPORTANT: this file includes the Python implementation of the REST API
## It is in this file that you should implement the functionalities/transactions   

import flask
import logging, psycopg2, time

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user = "scott",
        password = "tiger",
        host = "db",
        port = "5432",
        database = "dbproj"
    )
    
    return db






##########################################################
## ENDPOINTS
##########################################################


@app.route('/')
def landing_page():
    return """

    Hello World (Python)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    ITCS 3160-002, Spring 2024<br/>
    <br/>
    """

##
## Demo GET
##
## Obtain all users in JSON format
##
## To use it, access:
##
## http://localhost:8080/users/
##

@app.route('/users/', methods=['GET'])
def get_all_users():
    logger.info('GET /users')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM users') 
        rows = cur.fetchall()

        logger.debug('GET /users - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'user_id': row[0], 'username': row[1], 'password': row[2], 'email': row[3], 'role': row[4]} 
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Demo GET
##
## Obtain user with username <username>
##
## To use it, access:
##
## http://localhost:8080/users/ssmith
##

@app.route('/users/<username>/', methods=['GET'])
def get_user(username):
    logger.info('GET /users/<username>')

    logger.debug('username: {username}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM users where username = %s', (username,)) #change from (SELECT username, name, city FROM users)
        rows = cur.fetchall()

        row = rows[0]

        logger.debug('GET /users/<username> - parse')
        logger.debug(row)
        content = {'user_id': row[0], 'username': row[1], 'password': row[2], 'email': row[3], 'role': row[4]} #changed

        response = {'status': StatusCodes['success'], 'results': content}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users/<username> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Demo POST
##
## Add a new user in a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/users/ -H 'Content-Type: application/json' -d '{"city": "London", "username": "ppopov", "name": "Peter Popov"}'
##

@app.route('/users/', methods=['POST'])
def add_users():
    logger.info('POST /users')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /users - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'username' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'username value not in payload'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'INSERT INTO users (username, name, city) VALUES (%s, %s, %s)'
    values = (payload['username'], payload['city'], payload['name'])

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted users {payload["username"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Demo PUT
##
## Update a user based on a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X PUT http://localhost:8080/users/ssmith -H 'Content-Type: application/json' -d '{"city": "Raleigh"}'
##

@app.route('/users/<username>', methods=['PUT'])
def update_users(username):
    logger.info('PUT /users/<username>')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /users/<username> - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'city' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'city is required to update'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'UPDATE users SET city = %s WHERE username = %s'
    values = (payload['city'], username)

    try:
        res = cur.execute(statement, values)
        response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

        # commit the transaction
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

@app.route('/auctions/', methods=['POST'])
def create_auction():
    logger.info('POST /auctions/')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /auctions/ - payload: {payload}')

    # validate required fields in the payload
    if 'title' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'title is required'}
    if 'description' not in payload:
        response = {'description': StatusCodes['api_error'], 'results': 'description is required'}
        return flask.jsonify(response)
    if 'end_time' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'end_time is required'}
        return flask.jsonify(response)
    if 'status' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'status is required'}
        return flask.jsonify(response)
    
    # prepare sql statement and values
    statement = 'INSERT INTO auctions (title, description, end_time, status) VALUES (%s, %s, %s, %s) RETURNING auction_id'
    values = (payload['title'], payload['description'], payload['end_time'], payload['status'])

    try:
        # execute the statement and fetch newly created auction_id
        cur.execute(statement, values)
        auction_id = cur.fetchone()[0]
        # commit transaction
        conn.commit()
        #return success response with the newly created auction ID
        response = {'status': StatusCodes['success'], 'results': {'auction_id': auction_id}}
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /auctions/ - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        #rollback in case of error
        conn.rollback()
    finally:
        # close the connection
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/auctions/list', methods = ['GET'])
def get_open_auctions():
    logger.info('GET /auctions/open/')

    # connect to the database
    conn = db_connection()
    cur = conn.cursor()

    try:
        # query databsae to display all open auctions
        cur.execute('SELECT * FROM auctions WHERE status = %s', ('open',))
        rows = cur.fetchall()

        # parse the rows and create list of open auctions
        open_auctions = []
        for row in rows:
            auction = {
                'auction_id': row[0],
                'title': row[1],
                'description': row[2],
                'end_time': row[3],
                'status': row[4]
            }
            open_auctions.append(auction)
        
        #create the response dictionary
        response = {
            'status': StatusCodes['success'],
            'results': open_auctions
        }
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auctionsopen/ - error: {error}')
        response = {
            'status': StatusCodes['internal_error'],
            'errors': str(error)
        }
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)

@app.route('/auctions/search/', methods=['GET'])
def search_auction():
    logger.info('GET /auctions/search/')

    # Retrieve the query parameters from the request
    auction_id = flask.request.args.get('auction_id')
    title = flask.request.args.get('title')
    description = flask.request.args.get('description')

    # Validate that at least one search parameter is provided
    if not auction_id and not title and not description:
        response = {
            'status': StatusCodes['api_error'],
            'results': 'At least one search parameter (auction_id, title, or description) must be provided'
        }
        return flask.jsonify(response)

    # Connect to the database
    conn = db_connection()
    cur = conn.cursor()

    try:
        # Prepare the base SQL query and values list
        sql_query = 'SELECT * FROM auctions WHERE'
        conditions = []
        values = []

        # Add conditions and values based on the provided query parameters
        if auction_id:
            conditions.append(' auction_id = %s')
            values.append(auction_id)
        if title:
            conditions.append(' title ILIKE %s')  # Case-insensitive search using ILIKE
            values.append(f'%{title}%')
        if description:
            conditions.append(' description ILIKE %s')  # Case-insensitive search using ILIKE
            values.append(f'%{description}%')

        # Join conditions with AND clause to form the final SQL query
        sql_query += ' AND '.join(conditions)

        # Execute the query with the specified values
        cur.execute(sql_query, values)
        rows = cur.fetchall()

        # Parse the rows and create a list of auction dictionaries
        auctions = []
        for row in rows:
            auction = {
                'auction_id': row[0],
                'title': row[1],
                'description': row[2],
                'end_time': row[3],
                'status': row[4]
            }
            auctions.append(auction)

        # Create the response dictionary
        response = {
            'status': StatusCodes['success'],
            'results': auctions
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auctions/search/ - error: {error}')
        response = {
            'status': StatusCodes['internal_error'],
            'errors': str(error)
        }

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()

    # Return the JSON response
    return flask.jsonify(response)

@app.route('/auction/details/')
def list_auction_details():


##########################################################
## MAIN
##########################################################
if __name__ == "__main__":

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    time.sleep(1) # just to let the DB start before this print :-)

    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.1 online: http://localhost:8080/users/\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)



