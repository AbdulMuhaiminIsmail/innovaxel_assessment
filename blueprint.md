# Schema and Constraints
Events (event_id, name, seats, date)
name is UNIQUE
seats > 0
date > current_date

Registrations (reg_id, event_id, user_name, timestamp)
user_name must not exist already
available_seats must be > 0

# APIs
@app.post("/create_event"):
async def create_event(name: str, seats: int, date: DateTime):
	add entry in the events table
	return event_id

@app.post("/reg_event"):
async def reg_event(user_name: str, event_id: uuid)
	add entry in the registrations table
	return reg_id

@app.get("/view_events"):
async def view_events(sort_by_date = None, filter_upcoming = None):
	display all events (optional sort or filter)
	EVENT_ID | EVENT_NAME | DATE | AVAILABLE_SEATS | TOTAL_REGISTRATIONS

@app.delete("/cancel_registration"):
async def cancel_registration(event_id, user_name)
	lock, remove the entry from registrations, unlock
	lock, increment seats in events table, unlock
	



