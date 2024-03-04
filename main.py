from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    #transforming the data from db in to dictionary for it to be transformed to json in the return for the API

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/random', methods=["GET"])
def get_random_cafe():
    all_caffes = Cafe.query.all()
    cafe = random.choice(all_caffes)
    #returning a jason from the DB, for the API using flask's jsonify instead of a template
    #the hard codede way
    # return jsonify(cafe={
    #    # "id": cafe.id,  #omiting the ID
    #     "name": cafe.name,
    #     "map_url": cafe.map_url,
    #     "img_url": cafe.img_url,
    #     "location" :cafe.location,
    #     #creating a subcategory of the facilities
    #     "amenities":{
    #         "seats": cafe.seats,
    #         "has_toilet": cafe.has_toilet,
    #         "has_wifi": cafe.has_wifi,
    #         "has_sockets": cafe.has_sockets,
    #         "can_take_calls": cafe.can_take_calls,
    #         "coffee_price": cafe.coffee_price
    #     }
    # })
    return jsonify(cafe = cafe.to_dict())

#returning all cafes as a jason using the method from the db class model
@app.route('/all', methods= ['GET'])
def all_cafes():
    all_cafes = Cafe.query.all()
    return jsonify(cafes= [cafe.to_dict() for cafe in all_cafes])


@app.route('/search', methods=['GET'])
def search():
#the url is like: localhost:5000/search?loc=NameOfThePlace
    location = request.args.get("loc")#get the arg from the url
    searched_cafes = Cafe.query.filter_by(location = location).all() #search the column in db based on the arg found
    if searched_cafes:
        return jsonify(cafes= [cafe.to_dict() for cafe in searched_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

# HTTP POST - Create Record

@app.route("/add", methods=['GET', 'POST'])
def add_cofe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        has_sockets=bool(request.form.get("sockets")),
        can_take_calls=bool(request.form.get("calls")),
        coffee_price=request.form.get("coffee_price"),
    )

    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response = {"success": "Successfully added the cafe"})



# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    cafe_id=cafe_id
    cofe_to_update=db.get_or_404(Cafe, cafe_id)
    new_price = request.args.get("new_price")
    cofe_to_update.coffee_price = new_price
    db.session.commit()
    return jsonify(response = {"success": "The price has been successfully updated"})

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(port=8000, debug=True)
