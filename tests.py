import unittest
import os
from manager import SchoolManager
from models import Student, Teacher, Course

class TestSchoolManager(unittest.TestCase):
    def setUp(self):
        """Создаем тестовый менеджер перед каждым тестом"""
        self.test_db = "test_data.json"
        self.manager = SchoolManager(self.test_db)

    def tearDown(self):
        """Удаляем тестовый файл после тестов"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_add_student(self):
        self.manager.add_student("Иван", "ivan@test.com")
        self.assertEqual(len(self.manager.students), 1)
        self.assertEqual(self.manager.students[1].name, "Иван")

    def test_create_course(self):
        self.manager.create_course("Python", "Программирование")
        self.assertEqual(len(self.manager.courses), 1)
        self.assertEqual(self.manager.courses[1].title, "Python")

    def test_enroll_student(self):
        self.manager.add_student("Петр", "petr@test.com")
        self.manager.create_course("Java", "Код")
        self.manager.enroll_student(1, 1)
        self.assertIn(1, self.manager.courses[1].student_ids)

    def test_assign_teacher(self):
        self.manager.add_teacher("Мария", "Математика")
        self.manager.create_course("Алгебра", "Наука")
        self.manager.assign_teacher(1, 1)
        self.assertEqual(self.manager.courses[1].teacher_id, 1)

if __name__ == '__main__':
    unittest.main()