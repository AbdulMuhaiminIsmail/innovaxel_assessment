from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Body, Depends, FastAPI, HTTPException

import models
from database import engine, get_db


models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Event Registration API")


@app.post("/create_event")
async def create_event(
    event_name: str = Body(...), 
    total_seats: int = Body(...), 
    event_date: datetime = Body(...),
    db: Session = Depends(get_db)
):
    try:
        if total_seats <= 0:
            raise HTTPException(status_code=400, detail="Total seats must be greater than 0.")
        
        if event_date.replace(tzinfo=None) <= datetime.utcnow():
            raise HTTPException(status_code=400, detail="The event must be scheduled in future.")
        
        existing_event = db.query(models.Event).filter(
            models.Event.event_name == event_name
        ).first()
        
        if existing_event:
            raise HTTPException(status_code=400, detail="The event with same name already exists.")
        
        event = models.Event(
            event_name=event_name,
            total_seats=total_seats,
            available_seats=total_seats,
            event_date=event_date.replace(tzinfo=None)
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event  
    
    except HTTPException:
        raise
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An exception occured: {e}")
    

@app.post("/reg_event")
async def reg_event(
    user_name: str = Body(...), 
    event_id: int = Body(...),
    db: Session = Depends(get_db)
):
    try:
        event_record = db.query(models.Event).filter(
            models.Event.event_id == event_id
        ).with_for_update().first()

        if not event_record:
            raise HTTPException(status_code=400, detail="No event exists with this event_id.")
        
        if event_record.available_seats <= 0:
            raise HTTPException(status_code=400, detail="No seats available for this event.")
        
        reg_record = db.query(models.Registration).filter(
                models.Registration.user_name == user_name,
                models.Registration.event_id == event_id
        ).first()
            
        if reg_record:
            raise HTTPException(status_code=400, detail="User has already registered for this event.")
        
        registration = models.Registration(
            user_name=user_name, 
            event_id=event_id
        )
        
        db.add(registration)
        event_record.available_seats -= 1

        db.commit()
        db.refresh(registration)

        return registration
    
    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An exception occured: {e}")
    

@app.get("/view_events")
async def view_events(
    sort_by_date: bool = False, 
    filter_upcoming: bool = False,
    db: Session = Depends(get_db)
):
    try:
        events = db.query(models.Event)

        if filter_upcoming:
            events = events.filter(models.Event.event_date > datetime.utcnow())

        if sort_by_date:
            events = events.order_by(models.Event.event_date.asc())

        events = events.all()
        
        for event in events:
            event.total_registrations = event.total_seats - event.available_seats

        return events
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An exception occured: {e}")
    

@app.delete("/cancel_registration")
async def cancel_registration(
    event_id: int, 
    user_name: str,
    db: Session = Depends(get_db)
):
    try:
        reg_record = db.query(models.Registration).filter(
            models.Registration.event_id == event_id,
            models.Registration.user_name == user_name
        ).first()

        if not reg_record:
            raise HTTPException(status_code=400, detail="The event does not exist or the user is not registered for the event.")
        
        event_record = db.query(models.Event).filter(
            models.Event.event_id == event_id
        ).with_for_update().first()

        db.delete(reg_record)

        event_record.available_seats += 1

        db.commit()

        return {
            "status_code": 200,
            "message": "Registration cancelled successfully."
        }
    
    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An exception occured: {e}")