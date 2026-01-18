from flask import Flask, request, jsonify
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



# home
@app.route("/")
def home():
    return {"message": "Hello world"}



# POST - dodaj czlonka zespolu
@app.route("/team-members", methods=['POST'])
def add_team_member():
    data = request.get_json()
    new_team_member = TeamMember(name=data['name'])
    db.session.add(new_team_member)
    db.session.commit()

    return jsonify({"message": f'dodano czlonka zespolu {new_team_member.name}'}, 201)



#GET - pobierz wszystkich czlonkow zespolu
@app.route("/team-members", methods=["GET"])
def get_all_team_members():
    team_members = TeamMember.query.all()
    output = []

    for team_member in team_members:
        team_member_data = {
            "id": team_member.id,
            "name": team_member.name,
            "was picked": team_member.was_picked
            }
        output.append(team_member_data)
    
    if len(output) < 1:
        return {"message": "brak czlonkow zespolu"}
    
    return {"team members": output}


# GET ID - pobierz czlonka zespolu po ID
@app.route("/team-members/<int:id>")
def get_team_member_by_id(id):
    team_member = TeamMember.query.get_or_404(id)
    
    return jsonify({
        "id": team_member.id,
        "name": team_member.name,
        "was picked": team_member.was_picked
    })



# UPDATE - PUT
@app.route("/team-members/<int:id>", methods=["PUT"])
def update_team_member(id):
    team_member_to_update = TeamMember.query.get_or_404(id)

    data = request.get_json(id)

    team_member_to_update.name = data['name']
    # team_member_to_update.was_picked = data['was_picked'] - czy to bedzie potrzebne? moze lepiej nie dawac mozliwosci update flagi 
    db.session.commit()

    return jsonify({"message": f"team member {team_member_to_update.name} updated"})




#DELETE - Usun czlonka zespolu
@app.route("/team-members/<int:id>", methods=['DELETE'])
def delete_team_memberid(id):
    team_member_to_delete = TeamMember.query.get(id)

    try:
        db.session.delete(team_member_to_delete)
        db.session.commit()
    except Exception:
        return {"message": f"nie znaleziono czlonka zespolu o tym id"}


    return jsonify({"message": f"usunięto czlonka zespolu:{team_member_to_delete.name}"})



'''----------------TODO DO ZMIANY JUTRO-=-=-----------'''

'''Funkcja ma losowac osobe sposrod tych ktorzy maja flage FALSE dla was_picked, zmienic flage na True dla wylosowanych '''

# pobierz TYLKO dostepnych (was_picked = False)
# wsrod wszystkich dostepnych wybierz losowego i go zwrocic
# jesli nie ma zadnych dostepnych zwroc komunikat "message":"wszyscy zostali wybrani"


@app.route("/team-members/random", methods=["GET"])
def pick_random_team_member():
    # GET czlonkowie zespolu z flaga was_picked = FALSE
    available_members = TeamMember.query.filter_by(was_picked=False).all()

    # jesli wszyscy zostali wybrani zwroc info o tym
    if len(available_members) == 0:
        return {"message": "wszyscy zostali wybrani, resetuj"}

    #obiekt LOSOWEJ OSOBY Z FLAGA NA FALSE
    random_member_in_available = random.choice(available_members)
    random_member_in_available.was_picked = True
    db.session.commit()

    # serializacja wyniku - osoba wybrana
    random_team_member_from_available = []

    random_team_member_from_available.append({
            "id": random_member_in_available.id,
            "name": random_member_in_available.name,
            "was_picked": random_member_in_available.was_picked
        })

    return jsonify({"Losowy członek zespolu, ktory jeszcze nie byl wybrany:": random_team_member_from_available})


'''^^^^^^^----------------TODO DO ZMIANY JUTRO-=-=-----------^^^^^^^^'''



# PUT was_picked dla wszystkich na bazie
@app.route("/team-member/was-picked/reset", methods=["PUT"])
def reset_flag_was_picked_for_all():
    team_memberrs_with_flag_to_change_to_false = TeamMember.query.all()

    for team_member in team_memberrs_with_flag_to_change_to_false:
        team_member.was_picked = False
        db.session.commit()

    return jsonify({"message": "ok"})






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





# GET tylko tych którzy maja False dla was_picked - Tych chce pod losowanie randomowego
@app.route("/only-was-picked", methods=["GET"])
def get_only_was_picked():
    # zapisz w zmiennej tylko tych ktorzy maja flage False na was_picked
    team_members = TeamMember.query.filter_by(was_picked=True).all()

    output_picked = []

    for team_member in team_members:
        output_picked.append({
            "id": team_member.id,
            "name": team_member.name,
            "was_picked": team_member.was_picked
        })

    return jsonify({"message": output_picked})



if __name__ == "__main__":
    app.run(debug=True)

