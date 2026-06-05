import json
import os
import csv
from datetime import datetime
from models import Student, Teacher, Course, Module, Lesson

# Пытаемся импортировать библиотеку для графиков
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

    # Сохранение и загрузка
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
        with open(self.filename, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                self.students = {int(k): Student.from_dict(v) for k, v in data.get("students", {}).items()}
                self.teachers = {int(k): Teacher.from_dict(v) for k, v in data.get("teachers", {}).items()}
                self.courses = {int(k): Course.from_dict(v) for k, v in data.get("courses", {}).items()}
                
                counters = data.get("counters", {})
                self._next_student_id = counters.get("student_id", 1)
                self._next_teacher_id = counters.get("teacher_id", 1)
                self._next_course_id = counters.get("course_id", 1)
                self._next_module_id = counters.get("module_id", 1)
                self._next_lesson_id = counters.get("lesson_id", 1)
                return True
            except json.JSONDecodeError:
                return False

    # Модули и Уроки
    def add_module_to_course(self, course_id, title):
        if course_id not in self.courses:
            print("Курс не найден.")
            return
        module = Module(self._next_module_id, title)
        self.courses[course_id].modules.append(module)
        self._next_module_id += 1
        self.save_data()
        print(f"Модуль '{title}' добавлен в курс.")

    def add_lesson_to_module(self, course_id, module_id, title):
        if course_id not in self.courses:
            return print("Курс не найден.")
        course = self.courses[course_id]
        for module in course.modules:
            if module.id == module_id:
                lesson = Lesson(self._next_lesson_id, title)
                module.lessons.append(lesson)
                self._next_lesson_id += 1
                self.save_data()
                return print(f"Урок '{title}' добавлен в модуль '{module.title}'.")
        print("Модуль не найден.")

    # Система ДЗ
    def assign_homework_grade(self, course_id, module_id, lesson_id, student_id, grade):
        if course_id not in self.courses or student_id not in self.students:
            return print("Курс или студент не найдены.")
        course = self.courses[course_id]
        if student_id not in course.student_ids:
            return print("Студент не зачислен на этот курс.")
        
        for module in course.modules:
            if module.id == module_id:
                for lesson in module.lessons:
                    if lesson.id == lesson_id:
                        lesson.homework_grades[student_id] = grade
                        self.save_data()
                        return print(f"Оценка {grade} выставлена студенту за ДЗ в уроке '{lesson.title}'.")
        print("Модуль или урок не найдены.")

    def calculate_final_grade(self, course, student_id):
        total_grades = []
        for module in course.modules:
            for lesson in module.lessons:
                if student_id in lesson.homework_grades:
                    total_grades.append(lesson.homework_grades[student_id])
        if not total_grades:
            return 0
        return round(sum(total_grades) / len(total_grades), 2)

    def complete_course(self, course_id):
        if course_id not in self.courses: return print("Курс не найден.")
        course = self.courses[course_id]
        if course.status == "завершён": return print("Курс уже завершён.")

        course.status = "завершён"
        course.end_date = datetime.now().strftime("%Y-%m-%d")
        
        for student_id in course.student_ids:
            student = self.students.get(student_id)
            if student:
                final_grade = self.calculate_final_grade(course, student_id)
                student.history.append({
                    "course_id": course.id,
                    "course_title": course.title,
                    "grade": final_grade
                })
        self.save_data()
        print(f"Курс '{course.title}' завершён. Итоговые оценки рассчитаны на основе ДЗ.")

    # Отчет по преподавателю
    def show_teacher_report(self, teacher_id):
        if teacher_id not in self.teachers:
            return print("Преподаватель не найден.")
        teacher = self.teachers[teacher_id]
        teacher_courses = [c for c in self.courses.values() if c.teacher_id == teacher_id]
        
        active_courses = [c for c in teacher_courses if c.status == "активен"]
        completed_courses = [c for c in teacher_courses if c.status == "завершён"]
        
        print(f"\n--- Отчёт по преподавателю: {teacher.name} ({teacher.specialization}) ---")
        print(f"Количество активных курсов: {len(active_courses)}")
        
        print("\nЗавершённые курсы:")
        if not completed_courses: print("  Нет завершённых курсов.")
        for c in completed_courses:
            avg_grade = 0
            if c.student_ids:
                grades = [self.calculate_final_grade(c, sid) for sid in c.student_ids]
                avg_grade = round(sum(grades) / len(grades), 2) if grades else 0
            print(f"  - {c.title} (Завершён: {c.end_date}) | Средняя успеваемость: {avg_grade}")
        print("---------------------------------------------------------")

    # Экспорт в CSV
    def export_student_report_csv(self, student_id):
        if student_id not in self.students: return print("Студент не найден.")
        student = self.students[student_id]
        filename = f"student_report_{student_id}.csv"
        
        with open(filename, mode="w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["Курс", "Статус", "Итоговая Оценка/Текущая (по ДЗ)"])
            
            # Активные курсы
            for c in self.courses.values():
                if student_id in c.student_ids and c.status == "активен":
                    current_grade = self.calculate_final_grade(c, student_id)
                    writer.writerow([c.title, "Активен", current_grade])
            
            # Завершенные
            for record in student.history:
                writer.writerow([record["course_title"], "Завершён", record["grade"]])
                
        print(f"Отчёт успешно экспортирован в файл {filename}")

    # Визуализация
    def visualize_student_stats(self, student_id):
        if not MATPLOTLIB_AVAILABLE:
            return print("Для визуализации необходимо установить библиотеку matplotlib (pip install matplotlib)")
        
        if student_id not in self.students: return print("Студент не найден.")
        student = self.students[student_id]
        
        courses = []
        grades = []
        
        # Собираем историю
        for record in student.history:
            courses.append(record["course_title"])
            grades.append(record["grade"])
            
        # Собираем активные (по текущим ДЗ)
        for c in self.courses.values():
            if student_id in c.student_ids and c.status == "активен":
                courses.append(c.title + "\n(текущ.)")
                grades.append(self.calculate_final_grade(c, student_id))
                
        if not courses:
            return print("У студента нет оценок для визуализации.")

        plt.figure(figsize=(10, 6))
        bars = plt.bar(courses, grades, color='skyblue')
        plt.xlabel('Курсы')
        plt.ylabel('Оценка')
        plt.title(f'Успеваемость студента: {student.name}')
        plt.ylim(0, 5.5)

        # Подписи значений над колонками
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom')

        plt.tight_layout()
        plt.show()

    # Вспомогательные методы
    def add_student(self, name, email):
        student = Student(self._next_student_id, name, email)
        self.students[self._next_student_id] = student
        self._next_student_id += 1
        self.save_data()

    def add_teacher(self, name, specialization):
        teacher = Teacher(self._next_teacher_id, name, specialization)
        self.teachers[self._next_teacher_id] = teacher
        self._next_teacher_id += 1
        self.save_data()

    def create_course(self, title, topic):
        course = Course(self._next_course_id, title, topic)
        self.courses[self._next_course_id] = course
        self._next_course_id += 1
        self.save_data()

    def enroll_student(self, student_id, course_id):
        if student_id in self.students and course_id in self.courses:
            if student_id not in self.courses[course_id].student_ids:
                self.courses[course_id].student_ids.append(student_id)
                self.save_data()

    def assign_teacher(self, teacher_id, course_id):
        if teacher_id in self.teachers and course_id in self.courses:
            self.courses[course_id].teacher_id = teacher_id
            self.save_data()