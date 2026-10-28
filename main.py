import os

# Пути к файлам данных
INPUT_FILE = "participants.txt"
REPORT_FILE = "tournament_report.txt"

# Списки для хранения корректных участников и лога ошибок
participants = []
errors = []

def get_category(total_score):
    """Определение категории по итоговому баллу"""
    if 240 <= total_score <= 300:
        return "Отличный результат"
    elif 180 <= total_score <= 239:
        return "Хороший результат"
    elif 120 <= total_score <= 179:
        return "Удовлетворительный результат"
    else:
        return "Требуется подготовка"

def load_data():
    """Загрузка и валидация данных из файла"""
    global participants, errors
    participants.clear()
    errors.clear()
    
    if not os.path.exists(INPUT_FILE):
        print(f"Ошибка: Файл {INPUT_FILE} не найден!")
        return

    existing_ids = set()
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # Пропускаем пустые строки
                continue
                
            fields = [f.strip() for f in line.split(";")]
            
            # 1. Проверка количества полей
            if len(fields) != 6:
                errors.append(f"Строка {line_num}: неверное количество полей.")
                continue
                
            p_id, name, group, s1, s2, s3 = fields
            
            # 2. Проверка номера участника (положительное целое число)
            if not p_id.isdigit() or int(p_id) <= 0:
                errors.append(f"Строка {line_num}: номер участника должен быть положительным целым числом.")
                continue
            p_id = int(p_id)
            
            # 3. Проверка уникальности номера
            if p_id in existing_ids:
                errors.append(f"Строка {line_num}: повторяющийся номер участника {p_id}.")
                continue
                
            # 4-5. Проверка пустых строк в имени и группе
            if not name:
                errors.append(f"Строка {line_num}: имя участника не может быть пустым.")
                continue
            if not group:
                errors.append(f"Строка {line_num}: название группы не может быть пустым.")
                continue
                
            # 6-7. Проверка баллов
            try:
                scores = [int(s1), int(s2), int(s3)]
                if any(s < 0 or s > 100 for s in scores):
                    errors.append(f"Строка {line_num}: балл должен находиться в диапазоне от 0 до 100.")
                    continue
            except ValueError:
                errors.append(f"Строка {line_num}: баллы за задачи должны быть целыми числами.")
                continue
                
            # Если все проверки пройдены, сохраняем участника
            existing_ids.add(p_id)
            total_score = sum(scores)
            avg_score = round(total_score / 3, 2)
            
            participants.append({
                "id": p_id,
                "name": name,
                "group": group,
                "scores": scores,
                "total": total_score,
                "avg": avg_score,
                "category": get_category(total_score)
            })

def print_participant(p):
    """Красивый вывод одного участника"""
    print(f"№{p['id']} | {p['name']} | Группа: {p['group']} | Баллы: {p['scores']} | "
          f"Всего: {p['total']} | Ср. балл: {p['avg']} | Категория: {p['category']}")

def show_all():
    """1. Показать всех участников"""
    if not participants:
        print("Список участников пуст.")
        return
    print("\n--- Список всех участников ---")
    for p in participants:
        print_participant(p)

def get_sorted_rating():
    """Построение отсортированного рейтинга без изменения исходного списка"""
    return sorted(participants, key=lambda x: (-x['total'], x['name'].lower()))

def show_rating():
    """2. Показать общий рейтинг"""
    if not participants:
        print("Нет данных для построения рейтинга.")
        return
    print("\n--- Общий рейтинг участников ---")
    for idx, p in enumerate(get_sorted_rating(), 1):
        print(f"{idx}. ", end="")
        print_participant(p)

def filter_by_group():
    """3. Найти участников по группе"""
    group_query = input("Введите название учебной группы: ").strip().lower()
    found = [p for p in participants if p['group'].lower() == group_query]
    
    if not found:
        print(f"Участников из группы с названием '{group_query}' не найдено.")
        return
    print(f"\n--- Участники группы ---")
    for p in found:
        print_participant(p)

def search_by_name():
    """4. Найти участников по части имени"""
    name_query = input("Введите часть имени для поиска: ").strip().lower()
    found = [p for p in participants if name_query in p['name'].lower()]
    
    if not found:
        print("Участники с таким именем не найдены.")
        return
    print("\n--- Результаты поиска по имени ---")
    for p in found:
        print_participant(p)

def get_selected_participants():
    """Получение участников, прошедших отбор"""
    return [p for p in participants if p['total'] >= 180 and all(s >= 50 for s in p['scores'])]

def show_selected():
    """5. Показать участников, прошедших отбор"""
    found = get_selected_participants()
    if not found:
        print("Ни один участник не прошел отбор.")
        return
    print("\n--- Участники, прошедшие отбор ---")
    for p in found:
        print_participant(p)

def get_group_stats():
    """Расчет статистики по группам"""
    groups = set(p['group'] for p in participants)
    stats = {}
    for g in sorted(groups):
        g_participants = [p for p in participants if p['group'] == g]
        totals = [p['total'] for p in g_participants]
        max_total = max(totals)
        leaders = [p['name'] for p in g_participants if p['total'] == max_total]
        
        stats[g] = {
            "count": len(g_participants),
            "avg_total": round(sum(totals) / len(g_participants), 2),
            "max_total": max_total,
            "leaders": leaders
        }
    return stats

def get_task_stats():
    """Расчет статистики по трем задачам"""
    stats = []
    for i in range(3):
        task_scores = [p['scores'][i] for p in participants]
        stats.append({
            "avg": round(sum(task_scores) / len(participants), 2),
            "min": min(task_scores),
            "max": max(task_scores)
        })
    return stats

def show_stats():
    """6. Показать статистику"""
    if not participants:
        print("Нет данных для расчета статистики.")
        return
        
    print("\n--- Статистика по группам ---")
    for g, s in get_group_stats().items():
        print(f"Группа {g}: Участников: {s['count']}, Ср. балл: {s['avg_total']}, "
              f"Макс. балл: {s['max_total']}, Лидер(ы): {', '.join(s['leaders'])}")
              
    print("\n--- Статистика по задачам ---")
    for idx, s in enumerate(get_task_stats(), 1):
        print(f"Задача {idx}: Средний балл: {s['avg']}, Мин: {s['min']}, Max: {s['max']}")

def save_report():
    """7. Сохранить отчёт в файл"""
    if not participants and not errors:
        print("Нет данных для сохранения отчета.")
        return
        
    unique_groups = sorted(list(set(p['group'] for p in participants)))
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("=== ИТОГОВЫЙ ОТЧЕТ О ТУРНИРЕ ===\n\n")
        f.write(f"Количество корректных записей: {len(participants)}\n")
        f.write(f"Количество некорректных записей: {len(errors)}\n\n")
        
        f.write("Перечень уникальных групп:\n")
        for g in unique_groups:
            f.write(f" - {g}\n")
        f.write("\n")
        
        f.write("Общий рейтинг участников:\n")
        for idx, p in enumerate(get_sorted_rating(), 1):
            f.write(f" {idx}. №{p['id']} | {p['name']} | Группа: {p['group']} | Итог: {p['total']}\n")
        f.write("\n")
        
        f.write("Перечень участников, прошедших отбор:\n")
        for p in get_selected_participants():
            f.write(f" - {p['name']} (Группа: {p['group']}, Балл: {p['total']})\n")
        f.write("\n")
        
        f.write("Статистика по группам:\n")
        for g, s in get_group_stats().items():
            f.write(f" Группа {g}: Участников: {s['count']}, Ср. балл: {s['avg_total']}, "
                    f"Макс: {s['max_total']}, Лидер(ы): {', '.join(s['leaders'])}\n")
        f.write("\n")
        
        f.write("Статистика по задачам:\n")
        for idx, s in enumerate(get_task_stats(), 1):
            f.write(f" Задача {idx}: Ср. балл: {s['avg']}, Мин: {s['min']}, Макс: {s['max']}\n")
        f.write("\n")
        
        f.write("Список ошибок входных данных:\n")
        if errors:
            for err in errors:
                f.write(f" {err}\n")
        else:
            f.write(" Ошибок не обнаружено.\n")
            
    print(f"Отчет успешно сохранен в файл {REPORT_FILE}!")

def main_menu():
    """Консольное меню программы"""
    load_data()  # Автоматическая загрузка данных при старте
    
    while True:
        print("\n================ МЕНЮ ================")
        print("1. Показать всех участников")
        print("2. Показать общий рейтинг")
        print("3. Найти участников по группе")
        print("4. Найти участников по части имени")
        print("5. Показать участников, прошедших отбор")
        print("6. Показать статистику")
        print("7. Сохранить отчёт")
        print("0. Завершить программу")
        print("======================================")
        
        choice = input("Выберите пункт меню: ").strip()
        
        if choice == "1":
            show_all()
        elif choice == "2":
            show_rating()
        elif choice == "3":
            filter_by_group()
        elif choice == "4":
            search_by_name()
        elif choice == "5":
            show_selected()
        elif choice == "6":
            show_stats()
        elif choice == "7":
            save_report()
        elif choice == "0":
            print("Программа завершена. Всего доброго!")
            break
        else:
            print("Ошибка: Неизвестный пункт меню! Попробуйте снова.")
if __name__ == "__main__":
    main_menu()