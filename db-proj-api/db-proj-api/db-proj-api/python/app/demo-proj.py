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
        cur.execute('SELECT * FROM users') #changed
        rows = cur.fetchall()

        logger.debug('GET /users - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'user_id': row[0], 'username': row[1], 'password': row[2], 'email': row[3], 'role': row[4]} #changed
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

    # Validate payload fields
    if 'username' not in payload or 'role' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'Required fields missing'}
        return flask.jsonify(response)

    # Insert user into the users table
    statement = 'INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s) RETURNING user_id'
    values = (payload['username'], payload.get('password', ''), payload.get('email', ''), payload['role'])

    try:
        cur.execute(statement, values)
        user_id = cur.fetchone()[0]  # Get the ID of the newly inserted user

        # If the user is a seller, insert them into the sellers table
        if payload['role'] == 'Seller':
            cur.execute('INSERT INTO sellers (users_user_id, seller_name) VALUES (%s, %s)', (user_id, payload['username']))

        # If the user is a buyer, insert them into the buyers table
        elif payload['role'] == 'Buyer':
            cur.execute('INSERT INTO buyers (users_user_id, buyer_name) VALUES (%s, %s)', (user_id, payload['username']))

        # Commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted user {payload["username"]} with role {payload["role"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
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

# ADD ITEM TO AUCTION 
@app.route('/auctions/add_item', methods=['POST'])
def add_item_to_auction():
    logger.info('POST /auctions/add_item')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /auctions/add_item - payload: {payload}')

    # Validate payload fields
    if 'auction_id' not in payload or 'item_name' not in payload or 'minimum_price' not in payload or 'sellers_user_id' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'Required fields missing'}
        return flask.jsonify(response)

    try:
        # Insert item into the items table
        cur.execute('INSERT INTO items (item_name, minimum_price, auctions_auction_id, sellers_users_user_id) VALUES (%s, %s, %s, %s) RETURNING item_id',
                    (payload['item_name'], payload['minimum_price'], payload['auction_id'], payload['sellers_user_id']))
        item_id = cur.fetchone()[0]  # Get the ID of the newly inserted item
        conn.commit()

        response = {'status': StatusCodes['success'], 'results': 'Item added successfully', 'item_id': item_id}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /auctions/add_item - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    conn.close()
    return flask.jsonify(response)

########## Outbid Notifcation Function ##########
@app.route('/auctions/bid', methods=['POST'])
def place_bid():
    logger.info('POST /auctions/bid')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /auctions/bid - payload: {payload}')

    # Validate payload fields
    if 'auctions_auction_id' not in payload or 'bid_amount' not in payload or 'buyers_user_id' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'Required fields missing'}
        return flask.jsonify(response)

    # Check if the bid amount is higher than the current highest bid
    cur.execute('SELECT MAX(bid_amount) FROM bids WHERE auctions_auction_id = %s', (payload['auctions_auction_id'],))
    current_highest_bid = cur.fetchone()[0]

    if current_highest_bid is None or payload['bid_amount'] > current_highest_bid:
        statement = 'INSERT INTO bids (bid_amount, bid_time, items_item_id, auctions_auction_id, buyers_users_user_id) VALUES (%s, NOW(), %s, %s, %s)'
        values = (payload['bid_amount'], payload['items_item_id'], payload['auctions_auction_id'], payload['buyers_user_id'])

        try:
            cur.execute(statement, values)
            conn.commit()

            # Check if there are previous bids from the buyer
            cur.execute('SELECT bid_amount FROM bids WHERE auctions_auction_id = %s AND buyers_users_user_id = %s ORDER BY bid_time DESC LIMIT 1', (payload['auctions_auction_id'], payload['buyers_user_id']))
            previous_bid = cur.fetchone()
            if previous_bid and previous_bid[0] < payload['bid_amount']:
                # Notify the previous bidder that they've been outbid
                previous_bidder_id = get_previous_bidder_id(cur, payload['auctions_auction_id'], payload['buyers_user_id'])
                if previous_bidder_id:
                    message_content = f'Your bid of ${previous_bid[0]} has been outbid in auction {payload["auctions_auction_id"]}'
                    send_notification(cur, message_content, 'Outbid', payload['buyers_user_id'], previous_bidder_id)
                    conn.commit()

            response = {'status': StatusCodes['success'], 'results': 'Bid placed successfully'}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'POST /auctions/bid - error: {error}')
            response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
            conn.rollback()

    else:
        response = {'status': StatusCodes['api_error'], 'results': 'Bid amount must be higher than current highest bid'}

    conn.close()
    return flask.jsonify(response)

def get_previous_bidder_id(cur, auction_id, current_bidder_id):
    cur.execute('SELECT DISTINCT buyers_users_user_id FROM bids WHERE auction_id = %s AND buyers_users_user_id != %s ORDER BY bid_time DESC LIMIT 1', (auction_id, current_bidder_id))
    row = cur.fetchone()
    if row:
        return row[0]
    return None

def send_notification(cur, message_content, notification_type, sender_user_id, receiver_user_id):
    statement = 'INSERT INTO notifications (message_content, notification_type, sender_user_id, receiver_user_id, notification_time) VALUES (%s, %s, %s, %s, NOW())'
    values = (message_content, notification_type, sender_user_id, receiver_user_id)
    cur.execute(statement, values)

########## Close Auction ##########
from datetime import datetime

@app.route('/auctions/close/<int:auction_id>/', methods=['PUT'])
def close_auction(auction_id):
    logger.info(f'PUT /auctions/close/{auction_id}')
    
    # Get the current date and time
    current_datetime = datetime.now()
    
    conn = db_connection()
    cur = conn.cursor()
    
    try:
        # Retrieve the end time of the auction from the database
        cur.execute('SELECT end_time FROM auctions WHERE auction_id = %s', (auction_id,))
        end_time = cur.fetchone()[0]
        
        # Check if the current datetime is after the specified end time
        if current_datetime > end_time:
            cur.execute('UPDATE auctions SET status = %s WHERE auction_id = %s', ('closed', auction_id))
            conn.commit()
            
            # Determine the winner based on the highest bid
            cur.execute('SELECT buyers_users_user_id, MAX(bid_amount) FROM bids WHERE auction_id = %s GROUP BY buyers_users_user_id ORDER BY MAX(bid_amount) DESC LIMIT 1', (auction_id,))
            winner_info = cur.fetchone()
            winner_id, winning_amount = winner_info[0], winner_info[1]
            
            # Update auction details with winner information
            cur.execute('UPDATE auctions SET winner_user_id = %s, winning_amount = %s WHERE auction_id = %s', (winner_id, winning_amount, auction_id))
            conn.commit()
            
            response = {'status': StatusCodes['success'], 'results': f'Auction {auction_id} closed successfully'}
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Auction cannot be closed yet'}
        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /auctions/close/{auction_id} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
        
    finally:
        if conn is not None:
            conn.close()
    
    return flask.jsonify(response)

########## Cancel Auction ##########
@app.route('/auctions/cancel/<int:auction_id>/', methods=['PUT'])
def cancel_auction(auction_id):
    logger.info(f'PUT /auctions/cancel/{auction_id}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Update the status of the auction to 'cancelled'
        cur.execute('UPDATE auctions SET status = %s WHERE auction_id = %s', ('cancelled', auction_id))
        conn.commit()

        # Get all users interested in this auction
        cur.execute('SELECT DISTINCT buyers_users_user_id FROM bids WHERE auctions_auction_id = %s', (auction_id,))
        interested_users = cur.fetchall()

        # Send notification to each interested user
        for user_id in interested_users:
            message_content = f'The auction {auction_id} has been cancelled.'
            send_notification(cur, message_content, 'Auction Cancelled', sender_user_id=None, receiver_user_id=user_id[0])
            conn.commit()

        response = {'status': StatusCodes['success'], 'results': f'Auction {auction_id} cancelled successfully'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /auctions/cancel/{auction_id} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


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
