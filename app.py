from flask import Flask, jsonify, request

app = Flask(__name__)


# Simulated data
class Event:
    def __init__(self, id, title):
        self.id = id
        self.title = title

    def to_dict(self):
        return {"id": self.id, "title": self.title}


events = [
    Event(1, "Tech Meetup"),
    Event(2, "Python Workshop"),
]


# Helper: look up an event by id so the lookup logic isn't repeated in each route
def find_event(event_id):
    return next((e for e in events if e.id == event_id), None)


# Helper: generate the next id. Uses max id (not len) so ids stay unique after deletes
def next_id():
    return max((e.id for e in events), default=0) + 1


# GET / - JSON welcome message
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Event Management API!"}), 200


# GET /events - return all events as a JSON array
@app.route("/events", methods=["GET"])
def get_events():
    return jsonify([e.to_dict() for e in events]), 200


# POST /events - create a new event from JSON input
@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json(silent=True)

    # Input validation: body must be JSON and include a non-empty title
    if not data or not str(data.get("title", "")).strip():
        return jsonify({"error": "Request body must be JSON with a 'title' field"}), 400

    new_event = Event(next_id(), data["title"].strip())
    events.append(new_event)
    return jsonify(new_event.to_dict()), 201


# PATCH /events/<id> - update the title of an event
@app.route("/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": f"Event {event_id} not found"}), 404

    data = request.get_json(silent=True)
    if not data or not str(data.get("title", "")).strip():
        return jsonify({"error": "Request body must be JSON with a 'title' field"}), 400

    event.title = data["title"].strip()
    return jsonify(event.to_dict()), 200


# DELETE /events/<id> - remove an event from the list
@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": f"Event {event_id} not found"}), 404

    events.remove(event)
    # 204 No Content: success with an empty body
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)