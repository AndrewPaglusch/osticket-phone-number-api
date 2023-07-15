from flask import Flask, request, jsonify
import pymysql
import os
from waitress import serve
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    phone_number = data.get('phone_number')

    # Strip characters from the phone number
    phone_number = phone_number.replace('(', '').replace(')', '').replace('-', '')

    # Load MySQL configuration from environment variables
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST')
    database = os.getenv('MYSQL_DB')

    # Log MySQL configuration
    logging.info(f"Connecting to MySQL: {user}@{host}/{database}")

    connection = pymysql.connect(host=host, user=user, password=password, db=database)

    try:
        with connection.cursor() as cursor:
            # Execute user query
            cursor.execute(
                """SELECT c.firstname, c.lastname, c.company
                   FROM ost_user__cdata AS c
                   JOIN ost_user AS u ON c.user_id = u.id
                   WHERE REPLACE(REPLACE(REPLACE(c.maincellphone, '(', ''), ')', ''), '-', '') = %s
                   OR REPLACE(REPLACE(REPLACE(c.homephone, '(', ''), ')', ''), '-', '') = %s
                   OR REPLACE(REPLACE(REPLACE(c.officephone, '(', ''), ')', ''), '-', '') = %s""",
                (phone_number, phone_number, phone_number)
            )
            user = cursor.fetchone()

            # Execute organization query
            cursor.execute(
                """SELECT o.name
                   FROM ost_organization AS o
                   JOIN ost_organization__cdata AS c ON o.id = c.org_id
                   WHERE REPLACE(REPLACE(REPLACE(c.phone, '(', ''), ')', ''), '-', '') = %s""",
                (phone_number,)
            )
            organization = cursor.fetchone()

    finally:
        connection.close()

    if user or organization:
        result = {}
        if user:
            result['user'] = {
                'firstname': user[0] or "",
                'lastname': user[1] or "",
                'company': user[2] or "",
            }
        if organization:
            result['organization'] = {
                'name': organization[0] or "",
            }
        logging.info(f"Lookup result for phone number {phone_number}: {result}")
        return jsonify(result), 200
    else:
        logging.warning(f"No user or organization found for phone number {phone_number}")
        return jsonify({"error": "No user or organization found"}), 404

if __name__ == '__main__':
    logging.info("Starting the application...")
    serve(app, host="0.0.0.0", port=5000)
