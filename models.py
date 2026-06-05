from datetime import datetime

class Lesson:
    def __init__(self, lesson_id, title):
        self.id = lesson_id
        self.title = title
        # student_id (int) -> оценка за ДЗ (int)
        self.homework_grades = {}

    def to_dict(self):
        return {"id": self.id, "title": self.title, "homework_grades": self.homework_grades}

    @classmethod
    def from_dict(cls, data):
        lesson = cls(data["id"], data["title"])
        # Восстанавливаем ключи словаря как int
        lesson.homework_grades = {int(k): v for k, v in data.get("homework_grades", {}).items()}
        return lesson


class Module:
    def __init__(self, module_id, title, lessons=None):
        self.id = module_id
        self.title = title
        self.lessons = lessons if lessons is not None else []

    def to_dict(self):
        return {
            "id": self.id, 
            "title": self.title, 
            "lessons": [l.to_dict() for l in self.lessons]
        }

    @classmethod
    def from_dict(cls, data):
        lessons = [Lesson.from_dict(l_data) for l_data in data.get("lessons", [])]
        return cls(data["id"], data["title"], lessons)


class Student:
    def __init__(self, student_id, name, email, history=None):
        self.id = student_id
        self.name = name
        self.email = email
        self.history = history if history is not None else []

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "history": self.history}

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["name"], data["email"], data.get("history", []))


class Teacher:
    def __init__(self, teacher_id, name, specialization):
        self.id = teacher_id
        self.name = name
        self.specialization = specialization

    def to_dict(self):
        return {"id": self.id, "name": self.name, "specialization": self.specialization}

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["name"], data["specialization"])


class Course:
    def __init__(self, course_id, title, topic, status="активен", teacher_id=None, student_ids=None, modules=None, end_date=None):
        self.id = course_id
        self.title = title
        self.topic = topic
        self.status = status
        self.teacher_id = teacher_id
        self.student_ids = student_ids if student_ids is not None else []
        self.modules = modules if modules is not None else []
        self.end_date = end_date

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "topic": self.topic, "status": self.status,
            "teacher_id": self.teacher_id, "student_ids": self.student_ids, 
            "modules": [m.to_dict() for m in self.modules],
            "end_date": self.end_date
        }

    @classmethod
    def from_dict(cls, data):
        modules = [Module.from_dict(m_data) for m_data in data.get("modules", [])]
        return cls(
            data["id"], data["title"], data["topic"], data.get("status", "активен"),
            data.get("teacher_id"), data.get("student_ids", []), modules, data.get("end_date")
        )