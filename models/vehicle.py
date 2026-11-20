
class Vehicle:

    def __init__(
        self,
        registration,
        vehicle_type,
        make,
        model,
        year,
        current_mileage=0,
        status="Available",
        vehicle_id=None
    ):
        self.vehicle_id = vehicle_id
        self.registration = registration.strip().upper()
        self.vehicle_type = vehicle_type
        self.make = make
        self.model = model
        self.year = year
        self.current_mileage = current_mileage
        self.status = status

    def to_dict(self):
        return {
            "registration": self.registration,
            "vehicle_type": self.vehicle_type,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "current_mileage": self.current_mileage,
            "status": self.status
        }
