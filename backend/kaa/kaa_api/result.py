from app.api import bp
from flask import jsonify, request
from app.api.tra import main


@bp.route('/result', methods=['GET'])
def get_results():
    model = request.args.get('model')

    make = request.args.get('make')
    bg = request.args.get('bg')
    car_id = request.args.get('id')
    car_url = f'https://www.beforward.jp/{make}/{model}/{bg}/id/{car_id}/'
    print(car_url)
    # car_url='https://www.beforward.jp/toyota/mark-x/bg558249/id/1506853/' => sold
    response = jsonify(main(car_url))
    response.status_code = 200
    return response
