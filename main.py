from manager import SchoolManager

def seed_database(manager):
    """Заполнение базы начальными данными (Задание 6)"""
    print("Инициализация базовых данных...")
    
    # 5 преподавателей
    teachers = [("Иван Крутой", "Python"), ("Анна Нормальная", "Frontend"), 
                ("Сергей Неплохой", "DevOps"), ("Мария Хорошая", "Дизайн"), ("Олег Лучший", "QA")]
    for t in teachers: manager.add_teacher(t[0], t[1])
        
    # 5 студентов
    students = [("Алексей", "al@mail.com"), ("Борис", "b@mail.com"), 
                ("Виктор", "v@mail.com"), ("Галина", "g@mail.com"), ("Дарья", "d@mail.com")]
    for s in students: manager.add_student(s[0], s[1])
        
    # 5 курсов с модулями и уроками
    for i in range(1, 6):
        manager.create_course(f"Курс {i}", f"Тема {i}")
        manager.assign_teacher(i, i) # Назначаем преподавателей 1-1, 2-2 и тд.
        manager.enroll_student(i, i) # Зачисляем студентов
        
        manager.add_module_to_course(i, f"Модуль 1 (Курс {i})")
        manager.add_lesson_to_module(i, manager._next_module_id - 1, f"Введение (Курс {i})")
        manager.add_lesson_to_module(i, manager._next_module_id - 1, f"Практика (Курс {i})")
        
    print("База успешно заполнена тестовыми данными!\n")

def main():
    manager = SchoolManager()

    # Если база пустая (первый запуск), заполняем её
    if not manager.students and not manager.teachers:
        seed_database(manager)

    while True:
        print("\n=== УПРАВЛЕНИЕ ОНЛАЙН-ШКОЛОЙ v2.0 ===")
        print("1. Добавить модуль к курсу")
        print("2. Добавить урок в модуль")
        print("3. Оценить домашнее задание студента")
        print("4. Завершить курс (расчет итоговой оценки)")
        print("5. Отчёт по преподавателю (Аналитика)")
        print("6. Экспорт отчёта по студенту в CSV")
        print("7. Визуализировать успеваемость студента (График)")
        print("0. Выход")
        
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                cid = int(input("ID курса: "))
                title = input("Название модуля: ")
                manager.add_module_to_course(cid, title)
            elif choice == "2":
                cid = int(input("ID курса: "))
                mid = int(input("ID модуля: "))
                title = input("Название урока: ")
                manager.add_lesson_to_module(cid, mid, title)
            elif choice == "3":
                cid = int(input("ID курса: "))
                mid = int(input("ID модуля: "))
                lid = int(input("ID урока: "))
                sid = int(input("ID студента: "))
                grade = int(input("Оценка за ДЗ (число): "))
                manager.assign_homework_grade(cid, mid, lid, sid, grade)
            elif choice == "4":
                cid = int(input("ID курса: "))
                manager.complete_course(cid)
            elif choice == "5":
                tid = int(input("ID преподавателя: "))
                manager.show_teacher_report(tid)
            elif choice == "6":
                sid = int(input("ID студента: "))
                manager.export_student_report_csv(sid)
            elif choice == "7":
                sid = int(input("ID студента: "))
                manager.visualize_student_stats(sid)
            elif choice == "0":
                manager.save_data()
                print("Данные сохранены. Выход...")
                break
            else:
                print("Неверный ввод. Можно вводить только предложенные цифры.")
        except ValueError:
            print("Ошибка: ожидается корректный ввод (число). Попробуйте снова.")

if __name__ == "__main__":
    main()