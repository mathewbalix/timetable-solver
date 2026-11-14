from flask import Flask, render_template, request, redirect, url_for, session, flash
from solver import generate_timetable_schedule

app = Flask(__name__)
app.secret_key = "kansanga_seed_secret_key_v9"

# Store generated schedule in server memory so it never exceeds browser cookie limits
SERVER_STATE = {
    "schedule": []
}

DEFAULT_ROOMS = [
    "S1 A", "S1 B", "S1 C",
    "S2 A", "S2 B", "S2 C",
    "S3 A", "S3 B", "S3 C",
    "S4 A", "S4 B", "S4 C",
    "Computer Lab", "Physics Lab", "Biology Lab", "Chemistry Lab", "Art Room", "Music Room"
]

DEFAULT_TEACHERS = [
    {"name": "Mr. Kato", "subject": "Mathematics", "classes": ["S1", "S2"]},
    {"name": "Ms. Akello", "subject": "Mathematics", "classes": ["S3", "S4"]},
    {"name": "Mr. Mugisha", "subject": "Mathematics", "classes": ["S1", "S3"]},
    {"name": "Ms. Namayanja", "subject": "Mathematics", "classes": ["S2", "S4"]},
    {"name": "Mr. Okot", "subject": "Mathematics", "classes": ["S1", "S4"]},

    {"name": "Ms. Namukasa", "subject": "English", "classes": ["S1", "S2"]},
    {"name": "Mr. Ouma", "subject": "English", "classes": ["S3", "S4"]},
    {"name": "Ms. Alupo", "subject": "English", "classes": ["S1", "S3"]},
    {"name": "Mr. Ssempijja", "subject": "English", "classes": ["S2", "S4"]},
    {"name": "Ms. Amongin", "subject": "English", "classes": ["S1", "S4"]},

    {"name": "Dr. Okello", "subject": "Physics", "classes": ["S3", "S4"]},
    {"name": "Mr. Byaruhanga", "subject": "Physics", "classes": ["S1", "S2"]},
    {"name": "Ms. Kiconco", "subject": "Physics", "classes": ["S2", "S3"]},

    {"name": "Mrs. Nanteza", "subject": "Chemistry", "classes": ["S3", "S4"]},
    {"name": "Mr. Waiswa", "subject": "Chemistry", "classes": ["S1", "S2"]},
    {"name": "Ms. Kigozi", "subject": "Chemistry", "classes": ["S2", "S4"]},

    {"name": "Mr. Lule", "subject": "Biology", "classes": ["S3", "S4"]},
    {"name": "Ms. Nabukenya", "subject": "Biology", "classes": ["S1", "S2"]},
    {"name": "Dr. Mwesigwa", "subject": "Biology", "classes": ["S2", "S3"]},

    {"name": "Mr. Kigozi", "subject": "History", "classes": ["S1", "S2", "S3"]},
    {"name": "Ms. Ageno", "subject": "History", "classes": ["S2", "S4"]},
    {"name": "Mr. Kasujja", "subject": "Geography", "classes": ["S1", "S3", "S4"]},
    {"name": "Ms. Namubiru", "subject": "Geography", "classes": ["S2", "S3"]},
    {"name": "Mr. Bitature", "subject": "Geography", "classes": ["S1", "S2", "S4"]},

    {"name": "Mrs. Nambi", "subject": "ICT", "classes": ["S1", "S2", "S3", "S4"]},
    {"name": "Mr. Turyamubona", "subject": "ICT", "classes": ["S1", "S3"]},

    {"name": "Rev. Kakooza", "subject": "CRE", "classes": ["S1", "S2", "S3", "S4"]},
    {"name": "Mr. Lwanga", "subject": "Moral Education", "classes": ["S1", "S2"]},

    {"name": "Ms. Atim", "subject": "Entrepreneurship", "classes": ["S3", "S4"]},
    {"name": "Mr. Mbidde", "subject": "Entrepreneurship", "classes": ["S1", "S2"]},
    {"name": "Mr. Mukasa", "subject": "Agriculture", "classes": ["S1", "S2", "S3"]},
    {"name": "Ms. Kyomuhendo", "subject": "Agriculture", "classes": ["S2", "S4"]},

    {"name": "Ms. Nabakooza", "subject": "Luganda", "classes": ["S1", "S2", "S3", "S4"]},
    {"name": "Mr. Ddungu", "subject": "French", "classes": ["S1", "S2", "S3", "S4"]},
    {"name": "Ms. Busingye", "subject": "Literature", "classes": ["S2", "S3", "S4"]},
    {"name": "Mr. Kikambi", "subject": "Art", "classes": ["S1", "S2", "S3", "S4"]},
    {"name": "Ms. Nabalema", "subject": "Art", "classes": ["S2", "S3"]},
    {"name": "Mr. Kigozi Music", "subject": "Music", "classes": ["S1", "S2"]},
    {"name": "Mr. Ssenyondo", "subject": "Physics", "classes": ["S1", "S4"]},
    {"name": "Ms. Nakiwala", "subject": "Mathematics", "classes": ["S2", "S3"]}
]

DEFAULT_SUBJECTS = [
    {"name": "Mathematics", "class_level": "S1", "periods": 4},
    {"name": "English", "class_level": "S1", "periods": 4},
    {"name": "Physics", "class_level": "S1", "periods": 3},
    {"name": "Chemistry", "class_level": "S1", "periods": 3},
    {"name": "Biology", "class_level": "S1", "periods": 3},
    {"name": "History", "class_level": "S1", "periods": 2},
    {"name": "Geography", "class_level": "S1", "periods": 2},
    {"name": "ICT", "class_level": "S1", "periods": 2},
    {"name": "Agriculture", "class_level": "S1", "periods": 2},
    {"name": "CRE", "class_level": "S1", "periods": 2},
    {"name": "Art", "class_level": "S1", "periods": 2},
    {"name": "Luganda", "class_level": "S1", "periods": 2},

    {"name": "Mathematics", "class_level": "S2", "periods": 4},
    {"name": "English", "class_level": "S2", "periods": 4},
    {"name": "Physics", "class_level": "S2", "periods": 3},
    {"name": "Chemistry", "class_level": "S2", "periods": 3},
    {"name": "Biology", "class_level": "S2", "periods": 3},
    {"name": "History", "class_level": "S2", "periods": 2},
    {"name": "Geography", "class_level": "S2", "periods": 2},
    {"name": "ICT", "class_level": "S2", "periods": 2},
    {"name": "Agriculture", "class_level": "S2", "periods": 2},
    {"name": "CRE", "class_level": "S2", "periods": 2},
    {"name": "Art", "class_level": "S2", "periods": 2},
    {"name": "French", "class_level": "S2", "periods": 2},

    {"name": "Mathematics", "class_level": "S3", "periods": 4},
    {"name": "English", "class_level": "S3", "periods": 4},
    {"name": "Physics", "class_level": "S3", "periods": 3},
    {"name": "Chemistry", "class_level": "S3", "periods": 3},
    {"name": "Biology", "class_level": "S3", "periods": 3},
    {"name": "History", "class_level": "S3", "periods": 2},
    {"name": "Geography", "class_level": "S3", "periods": 2},
    {"name": "Entrepreneurship", "class_level": "S3", "periods": 2},
    {"name": "CRE", "class_level": "S3", "periods": 2},
    {"name": "Literature", "class_level": "S3", "periods": 2},

    {"name": "Mathematics", "class_level": "S4", "periods": 4},
    {"name": "English", "class_level": "S4", "periods": 4},
    {"name": "Physics", "class_level": "S4", "periods": 3},
    {"name": "Chemistry", "class_level": "S4", "periods": 3},
    {"name": "Biology", "class_level": "S4", "periods": 3},
    {"name": "History", "class_level": "S4", "periods": 2},
    {"name": "Geography", "class_level": "S4", "periods": 2},
    {"name": "Entrepreneurship", "class_level": "S4", "periods": 2},
    {"name": "French", "class_level": "S4", "periods": 2},
    {"name": "Luganda", "class_level": "S4", "periods": 2}
]

@app.route("/", methods=["GET", "POST"])
def index():
    if "rooms" not in session or not session["rooms"]:
        session["rooms"] = list(DEFAULT_ROOMS)
    if "teachers" not in session or not session["teachers"]:
        session["teachers"] = list(DEFAULT_TEACHERS)
    if "subjects" not in session or not session["subjects"]:
        session["subjects"] = list(DEFAULT_SUBJECTS)
    if "teacher_constraints" not in session:
        session["teacher_constraints"] = [
            {"teacher": "Mr. Kato", "max_daily": 4, "pref": "Morning Only"},
            {"teacher": "Ms. Namukasa", "max_daily": 4, "pref": "Any Time"},
            {"teacher": "Dr. Okello", "max_daily": 3, "pref": "Lab Preferred"}
        ]

    error_message = request.args.get("error")

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_teacher":
            t_name = request.form.get("teacher_name")
            t_subj = request.form.get("teacher_subject")
            t_classes = request.form.getlist("teacher_classes")
            if t_name and t_classes:
                teachers = session["teachers"]
                teachers.append({"name": t_name, "subject": t_subj, "classes": t_classes})
                session["teachers"] = teachers

        elif action == "delete_teacher":
            t_name = request.form.get("teacher_name")
            session["teachers"] = [t for t in session["teachers"] if t["name"] != t_name]

        elif action == "add_room":
            r_name = request.form.get("room_name")
            if r_name and r_name not in session["rooms"]:
                rooms = session["rooms"]
                rooms.append(r_name)
                session["rooms"] = rooms

        elif action == "delete_room":
            r_name = request.form.get("room_name")
            session["rooms"] = [r for r in session["rooms"] if r != r_name]

        elif action == "add_constraint":
            c_teacher = request.form.get("constraint_teacher")
            c_max = request.form.get("constraint_max", 4)
            c_pref = request.form.get("constraint_pref", "Any Time")
            if c_teacher:
                constraints = session["teacher_constraints"]
                constraints.append({"teacher": c_teacher, "max_daily": int(c_max), "pref": c_pref})
                session["teacher_constraints"] = constraints

        elif action == "generate":
            res = generate_timetable_schedule(
                session["teachers"],
                session["rooms"],
                session["subjects"],
                session["teacher_constraints"]
            )
            if res["status"] == "success":
                SERVER_STATE["schedule"] = res["schedule"]
                return redirect(url_for("index"))
            else:
                return redirect(url_for("index", error=res["message"]))

        return redirect(url_for("index"))

    schedule = SERVER_STATE["schedule"]
    selected_teacher = request.args.get("filter_teacher", "")
    selected_room = request.args.get("filter_room", "")

    filtered_schedule = schedule
    if selected_teacher:
        filtered_schedule = [s for s in schedule if s["teacher"] == selected_teacher]
    elif selected_room:
        filtered_schedule = [s for s in schedule if s["room"] == selected_room]

    return render_template(
        "index.html",
        rooms=session.get("rooms", []),
        teachers=session.get("teachers", []),
        subjects=session.get("subjects", []),
        constraints=session.get("teacher_constraints", []),
        schedule=filtered_schedule,
        master_schedule=schedule,
        error_message=error_message,
        selected_teacher=selected_teacher,
        selected_room=selected_room
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)