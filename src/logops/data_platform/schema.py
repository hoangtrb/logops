"""Typed definitions of the 14 dataset tables: the single source of truth for ingest, DQ and tests.

Column order matches the CSV header. Types are DuckDB type names. Foreign keys may be empty in
the CSV; they load as NULL and the DQ step flags them (`fk_missing`) instead of failing ingest.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TableSchema:
    name: str
    columns: dict[str, str]  # column -> DuckDB type, in CSV order
    primary_key: tuple[str, ...]  # composite for the monthly metrics tables
    foreign_keys: dict[str, str] = field(default_factory=dict)  # column -> parent table

    @property
    def csv_name(self) -> str:
        return f"{self.name}.csv"


TABLES: dict[str, TableSchema] = {
    t.name: t
    for t in [
        TableSchema(
            name="customers",
            primary_key=("customer_id",),
            columns={
                "customer_id": "VARCHAR",
                "customer_name": "VARCHAR",
                "customer_type": "VARCHAR",
                "credit_terms_days": "INTEGER",
                "primary_freight_type": "VARCHAR",
                "account_status": "VARCHAR",
                "contract_start_date": "DATE",
                "annual_revenue_potential": "INTEGER",
            },
        ),
        TableSchema(
            name="routes",
            primary_key=("route_id",),
            columns={
                "route_id": "VARCHAR",
                "origin_city": "VARCHAR",
                "origin_state": "VARCHAR",
                "destination_city": "VARCHAR",
                "destination_state": "VARCHAR",
                "typical_distance_miles": "INTEGER",
                "base_rate_per_mile": "DOUBLE",
                "fuel_surcharge_rate": "DOUBLE",
                "typical_transit_days": "INTEGER",
            },
        ),
        TableSchema(
            name="facilities",
            primary_key=("facility_id",),
            columns={
                "facility_id": "VARCHAR",
                "facility_name": "VARCHAR",
                "facility_type": "VARCHAR",
                "city": "VARCHAR",
                "state": "VARCHAR",
                "latitude": "DOUBLE",
                "longitude": "DOUBLE",
                "dock_doors": "INTEGER",
                "operating_hours": "VARCHAR",
            },
        ),
        TableSchema(
            name="drivers",
            primary_key=("driver_id",),
            columns={
                "driver_id": "VARCHAR",
                "first_name": "VARCHAR",
                "last_name": "VARCHAR",
                "hire_date": "DATE",
                "termination_date": "DATE",
                "license_number": "VARCHAR",
                "license_state": "VARCHAR",
                "date_of_birth": "DATE",
                "home_terminal": "VARCHAR",
                "employment_status": "VARCHAR",
                "cdl_class": "VARCHAR",
                "years_experience": "INTEGER",
            },
        ),
        TableSchema(
            name="trucks",
            primary_key=("truck_id",),
            columns={
                "truck_id": "VARCHAR",
                "unit_number": "VARCHAR",  # identifier, not a measure
                "make": "VARCHAR",
                "model_year": "INTEGER",
                "vin": "VARCHAR",
                "acquisition_date": "DATE",
                "acquisition_mileage": "INTEGER",
                "fuel_type": "VARCHAR",
                "tank_capacity_gallons": "INTEGER",
                "status": "VARCHAR",
                "home_terminal": "VARCHAR",
            },
        ),
        TableSchema(
            name="trailers",
            primary_key=("trailer_id",),
            columns={
                "trailer_id": "VARCHAR",
                "trailer_number": "VARCHAR",  # identifier, not a measure
                "trailer_type": "VARCHAR",
                "length_feet": "INTEGER",
                "model_year": "INTEGER",
                "vin": "VARCHAR",
                "acquisition_date": "DATE",
                "status": "VARCHAR",
                "current_location": "VARCHAR",
            },
        ),
        TableSchema(
            name="loads",
            primary_key=("load_id",),
            foreign_keys={
                "customer_id": "customers",
                "route_id": "routes",
            },
            columns={
                "load_id": "VARCHAR",
                "customer_id": "VARCHAR",
                "route_id": "VARCHAR",
                "load_date": "DATE",
                "load_type": "VARCHAR",
                "weight_lbs": "INTEGER",
                "pieces": "INTEGER",
                "revenue": "DOUBLE",
                "fuel_surcharge": "DOUBLE",
                "accessorial_charges": "DOUBLE",  # money; source values happen to be whole dollars
                "load_status": "VARCHAR",
                "booking_type": "VARCHAR",
            },
        ),
        TableSchema(
            name="trips",
            primary_key=("trip_id",),
            foreign_keys={
                "load_id": "loads",
                "driver_id": "drivers",
                "truck_id": "trucks",
                "trailer_id": "trailers",
            },
            columns={
                "trip_id": "VARCHAR",
                "load_id": "VARCHAR",
                "driver_id": "VARCHAR",
                "truck_id": "VARCHAR",
                "trailer_id": "VARCHAR",
                "dispatch_date": "DATE",
                "actual_distance_miles": "INTEGER",
                "actual_duration_hours": "DOUBLE",
                "fuel_gallons_used": "DOUBLE",
                "average_mpg": "DOUBLE",
                "idle_time_hours": "DOUBLE",
                "trip_status": "VARCHAR",
            },
        ),
        TableSchema(
            name="delivery_events",
            primary_key=("event_id",),
            foreign_keys={
                "load_id": "loads",
                "trip_id": "trips",
                "facility_id": "facilities",
            },
            columns={
                "event_id": "VARCHAR",
                "load_id": "VARCHAR",
                "trip_id": "VARCHAR",
                "event_type": "VARCHAR",
                "facility_id": "VARCHAR",
                "scheduled_datetime": "TIMESTAMP",
                "actual_datetime": "TIMESTAMP",
                "detention_minutes": "INTEGER",
                "on_time_flag": "BOOLEAN",
                "location_city": "VARCHAR",
                "location_state": "VARCHAR",
            },
        ),
        TableSchema(
            name="fuel_purchases",
            primary_key=("fuel_purchase_id",),
            foreign_keys={
                "trip_id": "trips",
                "truck_id": "trucks",
                "driver_id": "drivers",
            },
            columns={
                "fuel_purchase_id": "VARCHAR",
                "trip_id": "VARCHAR",
                "truck_id": "VARCHAR",
                "driver_id": "VARCHAR",
                "purchase_date": "TIMESTAMP",
                "location_city": "VARCHAR",
                "location_state": "VARCHAR",
                "gallons": "DOUBLE",
                "price_per_gallon": "DOUBLE",
                "total_cost": "DOUBLE",
                "fuel_card_number": "VARCHAR",
            },
        ),
        TableSchema(
            name="maintenance_records",
            primary_key=("maintenance_id",),
            foreign_keys={
                "truck_id": "trucks",
            },
            columns={
                "maintenance_id": "VARCHAR",
                "truck_id": "VARCHAR",
                "maintenance_date": "DATE",
                "maintenance_type": "VARCHAR",
                "odometer_reading": "INTEGER",
                "labor_hours": "DOUBLE",
                "labor_cost": "DOUBLE",
                "parts_cost": "DOUBLE",
                "total_cost": "DOUBLE",
                "facility_location": "VARCHAR",
                "downtime_hours": "DOUBLE",
                "service_description": "VARCHAR",
            },
        ),
        TableSchema(
            name="safety_incidents",
            primary_key=("incident_id",),
            foreign_keys={
                "trip_id": "trips",
                "truck_id": "trucks",
                "driver_id": "drivers",
            },
            columns={
                "incident_id": "VARCHAR",
                "trip_id": "VARCHAR",
                "truck_id": "VARCHAR",
                "driver_id": "VARCHAR",
                "incident_date": "TIMESTAMP",
                "incident_type": "VARCHAR",
                "location_city": "VARCHAR",
                "location_state": "VARCHAR",
                "at_fault_flag": "BOOLEAN",
                "injury_flag": "BOOLEAN",
                "vehicle_damage_cost": "DOUBLE",
                "cargo_damage_cost": "DOUBLE",
                "claim_amount": "DOUBLE",
                "preventable_flag": "BOOLEAN",
                "description": "VARCHAR",
            },
        ),
        TableSchema(
            name="driver_monthly_metrics",
            primary_key=("driver_id", "month"),
            foreign_keys={
                "driver_id": "drivers",
            },
            columns={
                "driver_id": "VARCHAR",
                "month": "DATE",
                "trips_completed": "INTEGER",
                "total_miles": "INTEGER",
                "total_revenue": "DOUBLE",
                "average_mpg": "DOUBLE",
                "total_fuel_gallons": "DOUBLE",
                "on_time_delivery_rate": "DOUBLE",
                "average_idle_hours": "DOUBLE",
            },
        ),
        TableSchema(
            name="truck_utilization_metrics",
            primary_key=("truck_id", "month"),
            foreign_keys={
                "truck_id": "trucks",
            },
            columns={
                "truck_id": "VARCHAR",
                "month": "DATE",
                "trips_completed": "INTEGER",
                "total_miles": "INTEGER",
                "total_revenue": "DOUBLE",
                "average_mpg": "DOUBLE",
                "maintenance_events": "INTEGER",
                "maintenance_cost": "DOUBLE",
                "downtime_hours": "DOUBLE",
                "utilization_rate": "DOUBLE",
            },
        ),
    ]
}
