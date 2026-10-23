"""Sample data for EventEase.

This module is the **single source of truth** for the demo dataset.  It is
used to

* insert the data through SQLAlchemy (`backend/app/db/seed.py`),
* generate `database/seed.sql` (`backend/scripts/generate_sql.py`),

so the SQL script and the Python seeder can never drift apart.

All event dates are expressed as an offset (in days) from "today" which keeps
the dashboard meaningful whenever the project is initialised: there are always
completed, ongoing and upcoming events.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

# --------------------------------------------------------------------------
# Organizers
# --------------------------------------------------------------------------
ORGANIZERS: list[dict] = [
    {
        "organizer_name": "Aarav Mehta",
        "email": "aarav.mehta@eventease.edu",
        "phone": "+91-98765-43210",
        "organization_name": "Nexus Tech Club",
    },
    {
        "organizer_name": "Priya Nair",
        "email": "priya.nair@eventease.edu",
        "phone": "+91-98765-43211",
        "organization_name": "Cultural Committee",
    },
    {
        "organizer_name": "Rahul Verma",
        "email": "rahul.verma@eventease.edu",
        "phone": "+91-98765-43212",
        "organization_name": "Sports Council",
    },
    {
        "organizer_name": "Sneha Iyer",
        "email": "sneha.iyer@eventease.edu",
        "phone": "+91-98765-43213",
        "organization_name": "MBA Society",
    },
    {
        "organizer_name": "Arjun Rao",
        "email": "arjun.rao@eventease.edu",
        "phone": "+91-98765-43214",
        "organization_name": "Innovation Lab",
    },
    {
        "organizer_name": "Kavya Reddy",
        "email": "kavya.reddy@eventease.edu",
        "phone": "+91-98765-43215",
        "organization_name": "Department of Computer Science",
    },
]

# --------------------------------------------------------------------------
# Venues
# --------------------------------------------------------------------------
VENUES: list[dict] = [
    {
        "venue_name": "Main Auditorium",
        "location": "North Campus, Academic Block A",
        "capacity": 500,
        "venue_type": "Auditorium",
        "availability_status": "Available",
    },
    {
        "venue_name": "Innovation Lab",
        "location": "Engineering Block, Level 2",
        "capacity": 120,
        "venue_type": "Laboratory",
        "availability_status": "Available",
    },
    {
        "venue_name": "Central Stadium",
        "location": "Sports Complex, South Ground",
        "capacity": 2000,
        "venue_type": "Stadium",
        "availability_status": "Available",
    },
    {
        "venue_name": "Seminar Hall 1",
        "location": "Academic Block, Room 104",
        "capacity": 80,
        "venue_type": "Seminar Hall",
        "availability_status": "Maintenance",
    },
    {
        "venue_name": "Open Air Amphitheatre",
        "location": "South Garden",
        "capacity": 350,
        "venue_type": "Amphitheatre",
        "availability_status": "Available",
    },
    {
        "venue_name": "Computer Lab 3",
        "location": "CSE Block, Room 305",
        "capacity": 60,
        "venue_type": "Computer Lab",
        "availability_status": "Available",
    },
    {
        "venue_name": "Convention Centre",
        "location": "City Convention Centre, Exhibition Road",
        "capacity": 750,
        "venue_type": "Convention Centre",
        "availability_status": "Available",
    },
    {
        "venue_name": "Community Hall",
        "location": "Block C, Ground Floor",
        "capacity": 150,
        "venue_type": "Community Hall",
        "availability_status": "Unavailable",
    },
    {
        "venue_name": "Design Studio",
        "location": "Architecture Block, Studio 2",
        "capacity": 45,
        "venue_type": "Studio",
        "availability_status": "Available",
    },
    # No event is booked in this venue yet - the LEFT JOIN demo and the venue
    # utilisation report show a row with zero events.
    {
        "venue_name": "Open Rooftop Terrace",
        "location": "Administration Building, Level 4",
        "capacity": 250,
        "venue_type": "Terrace",
        "availability_status": "Available",
    },
]

# --------------------------------------------------------------------------
# Attendees
# --------------------------------------------------------------------------
ATTENDEES: list[dict] = [
    {"full_name": "Aarav Sharma", "email": "aarav.sharma@student.edu", "phone": "+91-98100-10001", "organization": "CSE Department"},
    {"full_name": "Meera Krishnan", "email": "meera.krishnan@student.edu", "phone": "+91-98100-10002", "organization": "ECE Department"},
    {"full_name": "Rohan Gupta", "email": "rohan.gupta@student.edu", "phone": "+91-98100-10003", "organization": "Mechanical Department"},
    {"full_name": "Ishita Bansal", "email": "ishita.bansal@student.edu", "phone": "+91-98100-10004", "organization": "MBA Department"},
    {"full_name": "Aditya Kulkarni", "email": "aditya.kulkarni@student.edu", "phone": "+91-98100-10005", "organization": "CSE Department"},
    {"full_name": "Fatima Sheikh", "email": "fatima.sheikh@student.edu", "phone": "+91-98100-10006", "organization": "Civil Engineering"},
    {"full_name": "Daniel Fernandes", "email": "daniel.fernandes@student.edu", "phone": "+91-98100-10007", "organization": "BBA Department"},
    {"full_name": "Neha Joshi", "email": "neha.joshi@student.edu", "phone": "+91-98100-10008", "organization": "Design Department"},
    {"full_name": "Vikram Singh", "email": "vikram.singh@student.edu", "phone": "+91-98100-10009", "organization": "Physics Department"},
    {"full_name": "Ananya Pillai", "email": "ananya.pillai@student.edu", "phone": "+91-98100-10010", "organization": "CSE Department"},
    {"full_name": "Rohit Malhotra", "email": "rohit.malhotra@student.edu", "phone": "+91-98100-10011", "organization": "Management Studies"},
    {"full_name": "Sneha Patil", "email": "sneha.patil@student.edu", "phone": "+91-98100-10012", "organization": "ECE Department"},
    {"full_name": "Karan Mehta", "email": "karan.mehta@student.edu", "phone": "+91-98100-10013", "organization": "Sports - Athletics"},
    {"full_name": "Priyanka Das", "email": "priyanka.das@student.edu", "phone": "+91-98100-10014", "organization": "Biotechnology"},
    {"full_name": "Manish Agarwal", "email": "manish.agarwal@student.edu", "phone": "+91-98100-10015", "organization": "CSE Department"},
    {"full_name": "Tanvi Shah", "email": "tanvi.shah@student.edu", "phone": "+91-98100-10016", "organization": "Architecture"},
    {"full_name": "Arjun Menon", "email": "arjun.menon@student.edu", "phone": "+91-98100-10017", "organization": "Finance"},
    {"full_name": "Ritika Jain", "email": "ritika.jain@student.edu", "phone": "+91-98100-10018", "organization": "Chemistry"},
    {"full_name": "Sameer Ansari", "email": "sameer.ansari@student.edu", "phone": "+91-98100-10019", "organization": "Civil Engineering"},
    {"full_name": "Pooja Nair", "email": "pooja.nair@student.edu", "phone": "+91-98100-10020", "organization": "CSE Department"},
    {"full_name": "Rahul Yadav", "email": "rahul.yadav@student.edu", "phone": "+91-98100-10021", "organization": "Electronics"},
    {"full_name": "Divya Menon", "email": "divya.menon@student.edu", "phone": "+91-98100-10022", "organization": "Humanities"},
    {"full_name": "Sanjay Gupta", "email": "sanjay.gupta@student.edu", "phone": "+91-98100-10023", "organization": "Mechanical Department"},
    {"full_name": "Aisha Khan", "email": "aisha.khan@student.edu", "phone": "+91-98100-10024", "organization": "CSE Department"},
    {"full_name": "Varun Joshi", "email": "varun.joshi@student.edu", "phone": "+91-98100-10025", "organization": "Sports - Cricket"},
    {"full_name": "Meghna Joshi", "email": "meghna.joshi@student.edu", "phone": "+91-98100-10026", "organization": "Design Department"},
    {"full_name": "Nithin Kamath", "email": "nithin.kamath@student.edu", "phone": "+91-98100-10027", "organization": "MBA Department"},
    {"full_name": "Radhika Iyer", "email": "radhika.iyer@student.edu", "phone": "+91-98100-10028", "organization": "Biotechnology"},
    {"full_name": "Suraj Pandey", "email": "suraj.pandey@student.edu", "phone": "+91-98100-10029", "organization": "Physics Department"},
    {"full_name": "Anjali Thomas", "email": "anjali.thomas@student.edu", "phone": "+91-98100-10030", "organization": "Psychology"},
    {"full_name": "Harsh Vardhan", "email": "harsh.vardhan@student.edu", "phone": "+91-98100-10031", "organization": "CSE Department"},
    {"full_name": "Bhavna Shah", "email": "bhavna.shah@student.edu", "phone": "+91-98100-10032", "organization": "Sociology"},
    {"full_name": "Yash Choudhary", "email": "yash.choudhary@student.edu", "phone": "+91-98100-10033", "organization": "Economics"},
    {"full_name": "Nandini Rao", "email": "nandini.rao@student.edu", "phone": "+91-98100-10034", "organization": "Architecture"},
    # The last three attendees have not registered for anything yet - they make
    # the "attendees without registration" report and the LEFT JOIN demo show
    # a meaningful result.
    {"full_name": "Kabir Anand", "email": "kabir.anand@student.edu", "phone": "+91-98100-10035", "organization": "CSE Department"},
    {"full_name": "Riya Bhattacharya", "email": "riya.bhattacharya@student.edu", "phone": "+91-98100-10036", "organization": "Biotechnology"},
    {"full_name": "Dev Sharma", "email": "dev.sharma@student.edu", "phone": "+91-98100-10037", "organization": "Physics Department"},
]


@dataclass
class RegistrationSeed:
    """One registration (and optionally one payment) of the demo dataset."""

    attendee: int  # 1-based index into ATTENDEES
    status: str = "Registered"
    attendance: str = "Not Marked"
    ticket_type: str = "General"
    amount: float | None = None  # ticket price actually paid (None -> event price)
    payment_status: str | None = None  # None -> free event, no payment row
    payment_method: str = "UPI"
    days_before_event: int = 7


@dataclass
class EventSeed:
    key: str
    event_name: str
    description: str
    event_category: str
    organizer: int
    venue: int
    day_offset: int
    start_time: str
    end_time: str
    capacity: int
    ticket_price: float
    event_status: str
    registrations: list[RegistrationSeed] = field(default_factory=list)


# --------------------------------------------------------------------------
# Events (20 events, 5 categories, all four statuses, free + paid events)
# --------------------------------------------------------------------------
EVENTS: list[EventSeed] = [
    EventSeed(
        key="E01",
        event_name="Opening Tech Summit 2026",
        description="Flagship annual summit covering cloud, AI and developer tooling with industry keynotes.",
        event_category="Technical",
        organizer=1,
        venue=1,
        day_offset=-45,
        start_time="10:00:00",
        end_time="16:00:00",
        capacity=450,
        ticket_price=750,
        event_status="Completed",
        registrations=[
            RegistrationSeed(1, "Confirmed", "Present", "VIP", payment_status="Completed", payment_method="Card", days_before_event=30),
            RegistrationSeed(2, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=28),
            RegistrationSeed(5, "Confirmed", "Present", "Student", amount=375, payment_status="Completed", payment_method="UPI", days_before_event=25),
            RegistrationSeed(10, "Confirmed", "Present", "General", payment_status="Completed", payment_method="Bank Transfer", days_before_event=22),
            RegistrationSeed(15, "Confirmed", "Absent", "General", payment_status="Completed", payment_method="Cash", days_before_event=20),
            RegistrationSeed(20, "Confirmed", "Present", "Student", amount=375, payment_status="Completed", payment_method="UPI", days_before_event=18),
            RegistrationSeed(24, "Confirmed", "Present", "General", payment_status="Refunded", payment_method="Card", days_before_event=15),
            RegistrationSeed(31, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=12),
        ],
    ),
    EventSeed(
        key="E02",
        event_name="Annual Cultural Night",
        description="Inter-department cultural programme with dance, drama and music performances.",
        event_category="Cultural",
        organizer=2,
        venue=1,
        day_offset=-12,
        start_time="18:00:00",
        end_time="22:00:00",
        capacity=480,
        ticket_price=300,
        event_status="Completed",
        registrations=[
            RegistrationSeed(3, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=20),
            RegistrationSeed(7, "Confirmed", "Present", "VIP", payment_status="Completed", payment_method="Card", days_before_event=18),
            RegistrationSeed(8, "Confirmed", "Present", "General", payment_status="Completed", payment_method="Cash", days_before_event=15),
            RegistrationSeed(12, "Confirmed", "Absent", "Student", amount=150, payment_status="Completed", payment_method="UPI", days_before_event=11),
            RegistrationSeed(18, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=9),
            RegistrationSeed(26, "Confirmed", "Present", "General", payment_status="Pending", payment_method="UPI", days_before_event=6),
            RegistrationSeed(33, "Confirmed", "Present", "VIP", payment_status="Completed", payment_method="Bank Transfer", days_before_event=4),
        ],
    ),
    EventSeed(
        key="E03",
        event_name="Spring Product Launch",
        description="Product and strategy launch event for the MBA society with investor panels.",
        event_category="Business",
        organizer=4,
        venue=1,
        day_offset=12,
        start_time="10:00:00",
        end_time="13:00:00",
        capacity=300,
        ticket_price=1200,
        event_status="Upcoming",
        registrations=[
            RegistrationSeed(4, "Confirmed", "Not Marked", "VIP", payment_status="Completed", payment_method="Card", days_before_event=10),
            RegistrationSeed(11, "Confirmed", "Not Marked", "General", payment_status="Pending", payment_method="Bank Transfer", days_before_event=8),
        ],
    ),
    EventSeed(
        key="E04",
        event_name="Startup Investor Meetup",
        description="Free open meetup connecting student founders with seed-stage investors.",
        event_category="Business",
        organizer=4,
        venue=1,
        day_offset=30,
        start_time="15:00:00",
        end_time="18:00:00",
        capacity=200,
        ticket_price=0,
        event_status="Upcoming",
        registrations=[],
    ),
    EventSeed(
        key="E05",
        event_name="Python and FastAPI Workshop",
        description="Hands-on workshop building and documenting a REST API with FastAPI and SQLAlchemy.",
        event_category="Workshop",
        organizer=1,
        venue=2,
        day_offset=-30,
        start_time="10:00:00",
        end_time="13:00:00",
        capacity=100,
        ticket_price=250,
        event_status="Completed",
        registrations=[
            RegistrationSeed(1, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=18),
            RegistrationSeed(5, "Confirmed", "Present", "Student", amount=125, payment_status="Completed", payment_method="UPI", days_before_event=16),
            RegistrationSeed(15, "Confirmed", "Present", "General", payment_status="Completed", payment_method="Card", days_before_event=14),
            RegistrationSeed(20, "Confirmed", "Absent", "General", payment_status="Completed", payment_method="Cash", days_before_event=11),
            RegistrationSeed(24, "Confirmed", "Present", "Student", amount=125, payment_status="Completed", payment_method="UPI", days_before_event=9),
            RegistrationSeed(31, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=5),
        ],
    ),
    EventSeed(
        key="E06",
        event_name="Cloud Architecture Bootcamp",
        description="Two day bootcamp on container orchestration, service meshes and cost optimisation.",
        event_category="Technical",
        organizer=5,
        venue=2,
        day_offset=7,
        start_time="09:30:00",
        end_time="16:30:00",
        capacity=90,
        ticket_price=900,
        event_status="Upcoming",
        registrations=[
            RegistrationSeed(2, "Confirmed", "Not Marked", "Early Bird", amount=700, payment_status="Completed", payment_method="Card", days_before_event=6),
            RegistrationSeed(10, "Confirmed", "Not Marked", "General", payment_status="Pending", payment_method="UPI", days_before_event=5),
            RegistrationSeed(21, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="Cash", days_before_event=3),
            RegistrationSeed(29, "Registered", "Not Marked", "Student", amount=450, payment_status="Pending", payment_method="UPI", days_before_event=2),
            RegistrationSeed(31, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="UPI", days_before_event=1),
        ],
    ),
    EventSeed(
        key="E07",
        event_name="AI and ML Model Lab",
        description="Practical lab on feature engineering, model evaluation and deployment pipelines.",
        event_category="Technical",
        organizer=5,
        venue=2,
        day_offset=21,
        start_time="10:00:00",
        end_time="16:00:00",
        capacity=80,
        ticket_price=650,
        event_status="Upcoming",
        registrations=[
            RegistrationSeed(5, "Confirmed", "Not Marked", "General", payment_status="Completed", payment_method="UPI", days_before_event=12),
            RegistrationSeed(15, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="UPI", days_before_event=9),
            RegistrationSeed(24, "Registered", "Not Marked", "Student", amount=325, payment_status="Pending", payment_method="Cash", days_before_event=4),
            RegistrationSeed(34, "Waitlisted", "Not Marked", "General", payment_status=None, days_before_event=2),
        ],
    ),
    EventSeed(
        key="E08",
        event_name="Inter-College Cricket Tournament",
        description="T20 style tournament between twelve college teams played over a full day.",
        event_category="Sports",
        organizer=3,
        venue=3,
        day_offset=-8,
        start_time="07:00:00",
        end_time="18:00:00",
        capacity=1500,
        ticket_price=200,
        event_status="Completed",
        registrations=[
            RegistrationSeed(13, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=25),
            RegistrationSeed(25, "Confirmed", "Present", "General", payment_status="Completed", payment_method="Cash", days_before_event=20),
            RegistrationSeed(9, "Confirmed", "Absent", "Student", amount=100, payment_status="Completed", payment_method="UPI", days_before_event=14),
            RegistrationSeed(22, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=10),
            RegistrationSeed(27, "Confirmed", "Present", "General", payment_status="Completed", payment_method="Card", days_before_event=8),
            RegistrationSeed(30, "Confirmed", "Present", "General", payment_status="Refunded", payment_method="UPI", days_before_event=3),
        ],
    ),
    EventSeed(
        key="E09",
        event_name="Annual Sports Day Finals",
        description="Track and field finals with the college athletics team selections.",
        event_category="Sports",
        organizer=3,
        venue=3,
        day_offset=25,
        start_time="08:00:00",
        end_time="17:00:00",
        capacity=1800,
        ticket_price=150,
        event_status="Upcoming",
        registrations=[],
    ),
    EventSeed(
        key="E10",
        event_name="Research Paper Reading Group",
        description="Free weekly reading group presenting recent papers from the database systems community.",
        event_category="Workshop",
        organizer=6,
        venue=4,
        day_offset=-20,
        start_time="14:00:00",
        end_time="16:00:00",
        capacity=60,
        ticket_price=0,
        event_status="Completed",
        registrations=[
            RegistrationSeed(6, "Confirmed", "Present", "Free", days_before_event=9),
            RegistrationSeed(14, "Confirmed", "Present", "Free", days_before_event=7),
            RegistrationSeed(28, "Confirmed", "Absent", "Free", days_before_event=4),
        ],
    ),
    EventSeed(
        key="E11",
        event_name="Standup Comedy Night",
        description="An evening of student stand-up performances with an open mic segment.",
        event_category="Cultural",
        organizer=2,
        venue=5,
        day_offset=5,
        start_time="19:00:00",
        end_time="21:30:00",
        capacity=320,
        ticket_price=399,
        event_status="Upcoming",
        registrations=[
            RegistrationSeed(3, "Confirmed", "Not Marked", "General", payment_status="Completed", payment_method="UPI", days_before_event=4),
            RegistrationSeed(8, "Confirmed", "Not Marked", "VIP", payment_status="Pending", payment_method="Card", days_before_event=3),
            RegistrationSeed(23, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="Cash", days_before_event=2),
            RegistrationSeed(26, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="UPI", days_before_event=2),
            RegistrationSeed(32, "Waitlisted", "Not Marked", "General", payment_status=None, days_before_event=1),
        ],
    ),
    EventSeed(
        key="E12",
        event_name="Folk Music Fusion Evening",
        description="Traditional folk instruments fused with contemporary bands.",
        event_category="Cultural",
        organizer=2,
        venue=5,
        day_offset=-35,
        start_time="18:30:00",
        end_time="21:30:00",
        capacity=300,
        ticket_price=250,
        event_status="Completed",
        registrations=[
            RegistrationSeed(12, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=20),
            RegistrationSeed(16, "Confirmed", "Present", "VIP", payment_status="Completed", payment_method="Card", days_before_event=17),
            RegistrationSeed(22, "Confirmed", "Absent", "General", payment_status="Completed", payment_method="Cash", days_before_event=9),
            RegistrationSeed(33, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=5),
        ],
    ),
    EventSeed(
        key="E13",
        event_name="Data Structures Lab Session",
        description="Problem solving lab on trees, graphs and dynamic programming.",
        event_category="Technical",
        organizer=6,
        venue=6,
        day_offset=-5,
        start_time="11:00:00",
        end_time="13:00:00",
        capacity=55,
        ticket_price=100,
        event_status="Completed",
        registrations=[
            RegistrationSeed(1, "Confirmed", "Present", "Student", amount=50, payment_status="Completed", payment_method="UPI", days_before_event=9),
            RegistrationSeed(5, "Confirmed", "Present", "Student", amount=50, payment_status="Completed", payment_method="Cash", days_before_event=8),
            RegistrationSeed(15, "Confirmed", "Absent", "General", payment_status="Completed", payment_method="UPI", days_before_event=7),
            RegistrationSeed(20, "Confirmed", "Present", "Student", amount=50, payment_status="Completed", payment_method="UPI", days_before_event=4),
            RegistrationSeed(31, "Confirmed", "Present", "Student", amount=50, payment_status="Completed", payment_method="UPI", days_before_event=2),
            RegistrationSeed(13, "Confirmed", "Present", "General", payment_status="Completed", payment_method="UPI", days_before_event=3),
        ],
    ),
    EventSeed(
        key="E14",
        event_name="TypeScript Fundamentals",
        description="Hands-on session covering generics, type narrowing and typed API contracts.",
        event_category="Workshop",
        organizer=1,
        venue=6,
        day_offset=3,
        start_time="10:00:00",
        end_time="12:30:00",
        capacity=50,
        ticket_price=350,
        event_status="Upcoming",
        registrations=[
            RegistrationSeed(10, "Confirmed", "Not Marked", "General", payment_status="Completed", payment_method="UPI", days_before_event=3),
            RegistrationSeed(21, "Confirmed", "Not Marked", "General", payment_status="Pending", payment_method="Cash", days_before_event=2),
            RegistrationSeed(29, "Registered", "Not Marked", "Student", amount=175, payment_status="Pending", payment_method="UPI", days_before_event=1),
            RegistrationSeed(34, "Waitlisted", "Not Marked", "General", payment_status=None, days_before_event=1),
        ],
    ),
    EventSeed(
        key="E15",
        event_name="Global Education Expo",
        description="Free education expo with university representatives and scholarship desks.",
        event_category="Business",
        organizer=4,
        venue=7,
        day_offset=-60,
        start_time="09:00:00",
        end_time="18:00:00",
        capacity=700,
        ticket_price=0,
        event_status="Completed",
        registrations=[
            RegistrationSeed(4, "Confirmed", "Present", "Free", days_before_event=30),
            RegistrationSeed(11, "Confirmed", "Present", "Free", days_before_event=26),
            RegistrationSeed(17, "Confirmed", "Absent", "Free", days_before_event=18),
            RegistrationSeed(27, "Confirmed", "Present", "Free", days_before_event=10),
        ],
    ),
    EventSeed(
        key="E16",
        event_name="Robotics Championship 2026",
        description="Inter-college robotics competition with autonomous and line-following categories.",
        event_category="Technical",
        organizer=5,
        venue=7,
        day_offset=40,
        start_time="09:00:00",
        end_time="17:00:00",
        capacity=600,
        ticket_price=500,
        event_status="Upcoming",
        registrations=[
            RegistrationSeed(2, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="UPI", days_before_event=12),
            RegistrationSeed(19, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="Cash", days_before_event=7),
            RegistrationSeed(23, "Registered", "Not Marked", "Student", amount=250, payment_status="Pending", payment_method="UPI", days_before_event=4),
            RegistrationSeed(32, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="UPI", days_before_event=1),
        ],
    ),
    EventSeed(
        key="E17",
        event_name="Alumni Reunion Dinner",
        description="Evening reunion dinner for batch alumni with a chief guest address.",
        event_category="Cultural",
        organizer=2,
        venue=8,
        day_offset=-2,
        start_time="19:00:00",
        end_time="22:00:00",
        capacity=140,
        ticket_price=800,
        event_status="Completed",
        registrations=[
            RegistrationSeed(6, "Confirmed", "Present", "VIP", payment_status="Completed", payment_method="Bank Transfer", days_before_event=25),
            RegistrationSeed(13, "Confirmed", "Absent", "General", payment_status="Completed", payment_method="UPI", days_before_event=14),
            RegistrationSeed(25, "Confirmed", "Present", "General", payment_status="Pending", payment_method="Cash", days_before_event=5),
        ],
    ),
    EventSeed(
        key="E18",
        event_name="UI UX Design Sprint",
        description="Five hour design sprint producing a clickable prototype for a campus product.",
        event_category="Workshop",
        organizer=1,
        venue=9,
        day_offset=9,
        start_time="10:00:00",
        end_time="15:00:00",
        capacity=40,
        ticket_price=450,
        event_status="Upcoming",
        registrations=[
            RegistrationSeed(8, "Confirmed", "Not Marked", "General", payment_status="Completed", payment_method="UPI", days_before_event=5),
            RegistrationSeed(16, "Registered", "Not Marked", "Student", amount=225, payment_status="Pending", payment_method="UPI", days_before_event=2),
            RegistrationSeed(26, "Registered", "Not Marked", "General", payment_status="Pending", payment_method="Card", days_before_event=1),
        ],
    ),
    EventSeed(
        key="E19",
        event_name="48 Hour Campus Hackathon",
        description="Free 48 hour build sprint judged on impact, craft and pitch.",
        event_category="Technical",
        organizer=1,
        venue=7,
        day_offset=0,
        start_time="09:00:00",
        end_time="18:00:00",
        capacity=500,
        ticket_price=0,
        event_status="Ongoing",
        registrations=[
            RegistrationSeed(5, "Confirmed", "Not Marked", "Free", days_before_event=14),
            RegistrationSeed(10, "Confirmed", "Not Marked", "Free", days_before_event=12),
            RegistrationSeed(15, "Confirmed", "Not Marked", "Free", days_before_event=10),
            RegistrationSeed(24, "Registered", "Not Marked", "Free", days_before_event=6),
            RegistrationSeed(31, "Registered", "Not Marked", "Free", days_before_event=3),
            RegistrationSeed(34, "Registered", "Not Marked", "Free", days_before_event=2),
        ],
    ),
    EventSeed(
        key="E20",
        event_name="Robotics Masterclass",
        description="Advanced masterclass on inverse kinematics - cancelled by the resource team.",
        event_category="Technical",
        organizer=5,
        venue=2,
        day_offset=15,
        start_time="10:00:00",
        end_time="14:00:00",
        capacity=60,
        ticket_price=550,
        event_status="Cancelled",
        registrations=[
            RegistrationSeed(21, "Cancelled", "Not Marked", "General", payment_status="Refunded", payment_method="UPI", days_before_event=9),
            RegistrationSeed(29, "Cancelled", "Not Marked", "General", payment_status="Refunded", payment_method="Card", days_before_event=6),
        ],
    ),
]


def today() -> date:
    return date.today()


def event_date(event: EventSeed, reference: date | None = None) -> date:
    return (reference or today()) + timedelta(days=event.day_offset)


def registration_date(event: EventSeed, seed: RegistrationSeed, reference: date | None = None) -> datetime:
    base = event_date(event, reference)
    return datetime.combine(base - timedelta(days=seed.days_before_event), time(hour=10, minute=0))


def payment_date(event: EventSeed, seed: RegistrationSeed, reference: date | None = None) -> datetime:
    return registration_date(event, seed, reference) + timedelta(days=1, hours=2)
