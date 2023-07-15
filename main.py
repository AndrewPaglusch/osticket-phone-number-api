from flask import Flask, request, jsonify
import pymysql
import os
from waitress import serve

app = Flask(__name__)

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    phone_number = data.get('phone_number')

    # Load MySQL configuration from environment variables
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST')
    database = os.getenv('MYSQL_DB')

    connection = pymysql.connect(host=host, user=user, password=password, db=database)

    try:
        with connection.cursor() as cursor:
            # Execute user query
            cursor.execute(
                """SELECT c.firstname, c.lastname, c.company 
                   FROM ost_user__cdata AS c 
                   JOIN ost_user AS u ON c.user_id = u.id 
                   WHERE c.maincellphone = %s OR c.homephone = %s OR c.officephone = %s""",
                (phone_number, phone_number, phone_number)
            )
            user = cursor.fetchone()

            # Execute organization query
            cursor.execute(
                """SELECT o.name 
                   FROM ost_organization AS o
                   JOIN ost_organization__cdata AS c ON o.id = c.org_id 
                   WHERE c.phone = %s""",
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
        return jsonify(result), 200
    else:
        return jsonify({"error": "No user or organization found"}), 404

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000)
