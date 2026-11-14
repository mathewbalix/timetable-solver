import pandas as pd
from ortools.sat.python import cp_model

def generate_timetable_schedule(teachers, rooms, subjects, teacher_constraints=None):
    model = cp_model.CpModel()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods = [
        {"id": 1, "name": "Period 1", "time": "8:00 - 9:20"},
        {"id": 2, "name": "Period 2", "time": "9:20 - 10:40"},
        {"id": 3, "name": "Period 3", "time": "11:00 - 12:20"},
        {"id": 4, "name": "Period 4", "time": "12:20 - 1:00"},
        {"id": 5, "name": "Period 5", "time": "2:00 - 3:30"},
        {"id": 6, "name": "Period 6", "time": "3:30 - 5:00"}
    ]

    teacher_list = teachers
    room_list = rooms
    parsed_subjects = subjects

    if not teacher_list or not room_list or not parsed_subjects:
        return {"status": "error", "message": "Please provide valid teachers, rooms, and subjects."}

    streams = ["A", "B", "C"]
    lessons = []
    
    for subj in parsed_subjects:
        class_level = subj.get('class_level', 'S1')
        subject_name = subj['name']
        num_periods = int(subj.get('periods', 3))
        
        subject_lower = subject_name.lower()
        if class_level in ["S3", "S4"]:
            if "physics" in subject_lower:
                lab_room = "Physics Lab"
            elif "chem" in subject_lower:
                lab_room = "Chemistry Lab"
            elif "bio" in subject_lower:
                lab_room = "Biology Lab"
            elif "ict" in subject_lower or "computer" in subject_lower:
                lab_room = "Computer Lab"
            elif "art" in subject_lower or "design" in subject_lower:
                lab_room = "Art Room"
            else:
                lab_room = None
        else:
            if "ict" in subject_lower or "computer" in subject_lower:
                lab_room = "Computer Lab"
            else:
                lab_room = None

        for stream in streams:
            stream_room = lab_room if lab_room else f"{class_level} {stream}"
            
            matching_teachers = [
                t['name'] for t in teacher_list 
                if t.get('subject', '').lower() in subject_lower and class_level in t.get('classes', ['S1', 'S2', 'S3', 'S4'])
            ]
            if not matching_teachers:
                matching_teachers = [t['name'] for t in teacher_list if t.get('subject', '').lower() in subject_lower]
            if not matching_teachers:
                matching_teachers = [teacher_list[0]['name']]
                
            assigned_teacher = matching_teachers[hash(stream) % len(matching_teachers)]

            for _ in range(num_periods):
                lessons.append({
                    'id': len(lessons),
                    'subject': f"{subject_name} ({class_level} {stream})",
                    'teacher': assigned_teacher,
                    'room': stream_room if stream_room in room_list else f"{class_level} A"
                })

    total_slots = len(days) * len(periods)
    if len(lessons) > total_slots * len(room_list):
        return {"status": "error", "message": "Too many subject lessons requested for available time slots and rooms!"}

    slot_vars = {}
    for lesson in lessons:
        l_id = lesson['id']
        slot_vars[l_id] = model.NewIntVar(0, total_slots - 1, f"slot_{l_id}")

    # Teacher conflict constraint
    for d_idx in range(len(days)):
        for p_idx in range(len(periods)):
            slot_idx = d_idx * len(periods) + p_idx
            for t in [item['name'] for item in teacher_list]:
                teacher_lessons = []
                for lesson in lessons:
                    if lesson['teacher'] == t:
                        l_id = lesson['id']
                        is_slot = model.NewBoolVar(f"t_{t}_l_{l_id}_s_{slot_idx}")
                        model.Add(slot_vars[l_id] == slot_idx).OnlyEnforceIf(is_slot)
                        model.Add(slot_vars[l_id] != slot_idx).OnlyEnforceIf(is_slot.Not())
                        teacher_lessons.append(is_slot)
                if teacher_lessons:
                    model.Add(sum(teacher_lessons) <= 1)

    # Room conflict constraint
    for d_idx in range(len(days)):
        for p_idx in range(len(periods)):
            slot_idx = d_idx * len(periods) + p_idx
            for r in room_list:
                room_lessons = []
                for lesson in lessons:
                    if lesson['room'] == r:
                        l_id = lesson['id']
                        is_slot = model.NewBoolVar(f"r_{r}_l_{l_id}_s_{slot_idx}")
                        model.Add(slot_vars[l_id] == slot_idx).OnlyEnforceIf(is_slot)
                        model.Add(slot_vars[l_id] != slot_idx).OnlyEnforceIf(is_slot.Not())
                        room_lessons.append(is_slot)
                if room_lessons:
                    model.Add(sum(room_lessons) <= 1)

    solver = cp_model.CpSolver()
    # Increased timeout to 20 seconds to allow the solver to handle all 40 teachers & streams
    solver.parameters.max_time_in_seconds = 20.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        schedule_records = []
        for lesson in lessons:
            l_id = lesson['id']
            s_val = solver.Value(slot_vars[l_id])
            d_idx = s_val // len(periods)
            p_idx = s_val % len(periods)
            
            schedule_records.append({
                "day": days[d_idx],
                "period": periods[p_idx]["name"],
                "time": periods[p_idx]["time"],
                "subject": lesson['subject'],
                "teacher": lesson['teacher'],
                "room": lesson['room']
            })
        return {
            "status": "success",
            "schedule": schedule_records,
            "clashes": 0
        }
    else:
        return {"status": "error", "message": "Could not find a conflict-free timetable within the time limit. Try reducing a few period weights."}