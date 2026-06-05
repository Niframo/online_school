import json
import os
import csv
from datetime import datetime
from models import Student, Teacher, Course, Module, Lesson

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class SchoolManager:
    def __init__(self, filename="school_data.json"):
        self.filename = filename
        self.students = {}
        self.teachers = {}
        self.courses = {}
        
        self._next_student_id = 1
        self._next_teacher_id = 1
        self._next_course_id = 1
        self._next_module_id = 1
        self._next_lesson_id = 1
        
        self.load_data()

    def save_data(self):
        data = {
            "students": {k: v.to_dict() for k, v in self.students.items()},
            "teachers": {k: v.to_dict() for k, v in self.teachers.items()},
            "courses": {k: v.to_dict() for k, v in self.courses.items()},
            "counters": {
                "student_id": self._next_student_id,
                "teacher_id": self._next_teacher_id,
                "course_id": self._next_course_id,
                "module_id": self._next_module_id,
                "lesson_id": self._next_lesson_id
            }
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if not os.path.exists(self.filename):
            return False
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.students = {int(k): Student.from_dict(v) for k, v in data.get("students", {}).items()}
                self.teachers = {int(k): Teacher.from_dict(v) for k, v in data.get("teachers", {}).items()}
                self.courses = {int(k): Course.from_dict(v) for k, v in data.get("courses", {}).items()}
                
                c = data.get("counters", {})
                self._next_student_id = c.get("student_id", 1)
                self._next_teacher_id = c.get("teacher_id", 1)
                self._next_course_id = c.get("course_id", 1)
                self._next_module_id = c.get("module_id", 1)
                self._next_lesson_id = c.get("lesson_id", 1)
                return True
        except (json.JSONDecodeError, IOError):
            return False

    def add_module_to_course(self, course_id, title):
        course = self.courses.get(course_id)
        if not course:
            return print("Курс не найден.")
        
        course.modules.append(Module(self._next_module_id, title))
        self._next_module_id += 1
        self.save_data()
        print(f"Модуль '{title}' добавлен.")

    def add_lesson_to_module(self, course_id, module_id, title):
        course = self.courses.get(course_id)
        if not course:
            return print("Курс не найден.")
        
        module = next((m for m in course.modules if m.id == module_id), None)
        if not module:
            return print("Модуль не найден.")
            
        module.lessons.append(Lesson(self._next_lesson_id, title))
        self._next_lesson_id += 1
        self.save_data()
        print(f"Урок '{title}' добавлен в модуль '{module.title}'.")

    def assign_homework_grade(self, course_id, module_id, lesson_id, student_id, grade):
        course = self.courses.get(course_id)
        if not course or student_id not in self.students:
            return print("Курс или студент не найдены.")
        if student_id not in course.student_ids:
            return print("Студент не зачислен на этот курс.")

        for mod in course.modules:
            if mod.id == module_id:
                for lesson in mod.lessons:
                    if lesson.id == lesson_id:
                        lesson.homework_grades[student_id] = grade
                        self.save_data()
                        return print(f"Оценка {grade} выставлена.")
        print("Модуль или урок не найдены.")

    def calculate_final_grade(self, course, student_id):
        grades = [lesson.homework_grades[student_id] 
                  for mod in course.modules 
                  for lesson in mod.lessons 
                  if student_id in lesson.homework_grades]
        return round(sum(grades) / len(grades), 2) if grades else 0

    def complete_course(self, course_id):
        course = self.courses.get(course_id)
        if not course or course.status == "завершён":
            return print("Курс не найден или уже завершён.")

        course.status = "завершён"
        course.end_date = datetime.now().strftime("%Y-%m-%d")
        
        for sid in course.student_ids:
            student = self.students.get(sid)
            if student:
                student.history.append({
                    "course_id": course.id,
                    "course_title": course.title,
                    "grade": self.calculate_final_grade(course, sid)
                })
        self.save_data()
        print(f"Курс '{course.title}' завершён.")

    def show_teacher_report(self, teacher_id):
        teacher = self.teachers.get(teacher_id)
        if not teacher:
            return print("Преподаватель не найден.")
            
        t_courses = [c for c in self.courses.values() if c.teacher_id == teacher_id]
        active = [c for c in t_courses if c.status == "активен"]
        completed = [c for c in t_courses if c.status == "завершён"]
        
        print(f"\n--- Отчёт: {teacher.name} ---")
        print(f"Активных курсов: {len(active)}")
        for c in completed:
            avg = sum(self.calculate_final_grade(c, s) for s in c.student_ids) / len(c.student_ids) if c.student_ids else 0
            print(f" - {c.title} (Завершён: {c.end_date}) | Средняя: {round(avg, 2)}")

    def export_student_report_csv(self, student_id):
        student = self.students.get(student_id)
        if not student:
            return print("Студент не найден.")
            
        filename = f"student_report_{student_id}.csv"
        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Курс", "Статус", "Оценка"])
            for c in self.courses.values():
                if student_id in c.student_ids and c.status == "активен":
                    writer.writerow([c.title, "Активен", self.calculate_final_grade(c, student_id)])
            for r in student.history:
                writer.writerow([r["course_title"], "Завершён", r["grade"]])
        print(f"Экспорт в {filename} выполнен.")

    def visualize_student_stats(self, student_id):
        if not MATPLOTLIB_AVAILABLE:
            return print("Установите matplotlib: pip install matplotlib")
            
        student = self.students.get(student_id)
        if not student:
            return print("Студент не найден.")
            
        data = {r["course_title"]: r["grade"] for r in student.history}
        for c in self.courses.values():
            if student_id in c.student_ids and c.status == "активен":
                data[f"{c.title}\n(текущ.)"] = self.calculate_final_grade(c, student_id)
        
        if not data:
            return print("Нет оценок для визуализации.")

        plt.figure(figsize=(10, 6))
        bars = plt.bar(data.keys(), data.values(), color='skyblue')
        plt.title(f'Успеваемость: {student.name}')
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), round(bar.get_height(), 2), ha='center')
        plt.show()

    # Вспомогательные методы
    def add_student(self, name, email):
        self.students[self._next_student_id] = Student(self._next_student_id, name, email)
        self._next_student_id += 1
        self.save_data()

    def add_teacher(self, name, specialization):
        self.teachers[self._next_teacher_id] = Teacher(self._next_teacher_id, name, specialization)
        self._next_teacher_id += 1
        self.save_data()

    def create_course(self, title, topic):
        self.courses[self._next_course_id] = Course(self._next_course_id, title, topic)
        self._next_course_id += 1
        self.save_data()

    def enroll_student(self, sid, cid):
        if sid in self.students and cid in self.courses and sid not in self.courses[cid].student_ids:
            self.courses[cid].student_ids.append(sid)
            self.save_data()

    def assign_teacher(self, tid, cid):
        if tid in self.teachers and cid in self.courses:
            self.courses[cid].teacher_id = tid
            self.save_data()