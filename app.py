from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_scss import Scss
import random

#app init
app = Flask(__name__)


#db init
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///daily_scrum.db'
db = SQLAlchemy(app)


#model czlonka zespolu
class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    was_picked = db.Column(db.Boolean, unique=False, default=False)

    def __repr__(self) -> str:
        return f"Team member {self.id}"

with app.app_context():
    db.create_all()


# do wywal
# # home
# @app.route("/")
# def home():
#     return render_template("index.html")



# POST - dodaj czlonka zespolu
@app.route("/team-members", methods=['POST'])
def add_team_member():

    current_new_team_member = request.form['name']
    try:
        new_team_member = TeamMember(name=current_new_team_member)
        db.session.add(new_team_member)
        db.session.commit()
        return redirect("/team-members")
    except Exception as e:
        return f"Problem z dodaniem osoby {e}"
   

    # data = request.get_json()

    # # walidacja danych
    # if not data: 
    #     return jsonify({"message": "Brak body requestu"}), 400
    
    # name = data.get("name")
    # if not name:
    #     return jsonify({"message": "Pole 'name' jest wymagane"}), 400
    
    # if not isinstance(name, str):
    #     return jsonify({"message": "Pole 'name' musi byc stringiem"}), 400
    # name = request.form['name']



    # return jsonify({"message": f'dodano czlonka zespolu {new_team_member.name}'}), 201



#GET - pobierz wszystkich czlonkow zespolu
@app.route("/team-members", methods=["GET"])
def get_all_team_members():
    team_members = TeamMember.query.all()
    team_members_serialized = []

    for team_member in team_members:
        team_member_data = {
            "id": team_member.id,
            "name": team_member.name,
            "was_picked": team_member.was_picked
            }
        team_members_serialized.append(team_member_data)
    
    # if len(team_members_serialized) < 1:
    #     return {"message": "brak czlonkow zespolu"}
    
    return render_template("index.html", team_members_serialized=team_members_serialized)


# GET ID - pobierz czlonka zespolu po ID
@app.route("/team-members/<int:id>")
def get_team_member_by_id(id):
    team_member = TeamMember.query.get_or_404(id)
    
    return jsonify({
        "id": team_member.id,
        "name": team_member.name,
        "was_picked": team_member.was_picked
    })



# UPDATE - PUT
@app.route("/team-members/<int:id>", methods=["PUT"])
def update_team_member(id):
    team_member_to_update = TeamMember.query.get_or_404(id)

    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"message": "Pole 'name' jest wymagane"}), 400

    team_member_to_update.name = data['name'].strip()
    db.session.commit()

    return jsonify({"message": f"team member {team_member_to_update.name} updated"})




#DELETE - Usun czlonka zespolu
@app.route("/team-members/<int:id>/delete", methods=['POST'])
def delete_team_member_id(id):
    team_member_to_delete = TeamMember.query.get(id)

    db.session.delete(team_member_to_delete)
    db.session.commit()

    return redirect("/team-members")

    return None

    # return jsonify({"message": f"usunięto czlonka zespolu:{team_member_to_delete.name}"})



'''Funkcja ma losowac osobe sposrod tych ktorzy maja flage FALSE dla was_picked, zmienic flage na True dla wylosowanych,
dac znac jesli dostepni sie skoncza i nalezy zresetowac losowanie '''

# pobierz TYLKO dostepnych (was_picked = False)
# wsrod wszystkich dostepnych wybierz losowego i go zwrocic
# jesli nie ma zadnych dostepnych zwroc komunikat "message":"wszyscy zostali wybrani"


@app.route("/team-members/random", methods=["GET"])
def pick_random_team_member():
    # GET czlonkowie zespolu z flaga was_picked = FALSE
    available_members = TeamMember.query.filter_by(was_picked=False).all()

    # jesli wszyscy maja flage was_picked == True, zwroc info
    if len(available_members) == 0:
        return redirect("/team-members")
        return {"message": "wszyscy zostali wybrani, resetuj"}

    #wylosuj osobe i ustaw flage na TRUE
    random_member_in_available = random.choice(available_members)
    random_member_in_available.was_picked = True
    if random_member_in_available:
        try:
            db.session.commit()
            return redirect("/team-members")
        except Exception:
            return f"wystapil blad"

    # serializacja wyniku - osoba wybrana
    random_team_member_from_available = []

    random_team_member_from_available.append({
            "id": random_member_in_available.id,
            "name": random_member_in_available.name,
            "was_picked": random_member_in_available.was_picked
        })

    return jsonify({"Wylosowany/a do prowadzenia:": random_team_member_from_available})



# PUT RESETUJ FLAGE was_picked na False dla wszystkich
@app.route("/team-members/was-picked/reset", methods=["POST"])
def reset_flag_was_picked_for_all():
    team_members_with_flag_to_change_to_false = TeamMember.query.all()


    for team_member in team_members_with_flag_to_change_to_false:
        team_member.was_picked = False
    db.session.commit()

    return redirect("/team-members")

    return jsonify({"message": "zresetowano flage u wszystkich"})



# PUT zmien was_picked na True lub False
@app.route("/team-members/was-picked/<int:id>", methods=["PUT"])
def change_flag_was_picked_for_team_member(id):
    team_member_with_flag_to_change = TeamMember.query.get_or_404(id)
    
    if team_member_with_flag_to_change.was_picked == True:
        team_member_with_flag_to_change.was_picked = False
    else:
        team_member_with_flag_to_change.was_picked = True
    db.session.commit()

    return jsonify({"message": f"team member {team_member_with_flag_to_change.name} updated"})




if __name__ == "__main__":
    app.run(port=8000, debug=True)

