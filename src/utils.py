def printing(dbmanager):
    """
    Provides an interface for selecting and displaying various kinds of information from the database.

    :param dbmanager: Instance of DBManager for working with the database
    """
    filters = {
        1: ("Получает список всех работодателей и подсчитывает количество вакансий у каждого из них.", dbmanager.get_companies_and_vacancies_count),
        2: ("Собирает информацию обо всех вакансиях, включая название компании, название позиции, зарплату и ссылку на вакансию.", dbmanager.get_all_vacancies),
        3: ("Определяет среднюю зарплату среди всех вакансий.", dbmanager.get_avg_salary),
        4: ("Фильтрует вакансии, зарплата которых превышает среднюю зарплату по всему набору вакансий.", dbmanager.get_vacancies_with_higher_salary),
        5: ("Находит все вакансии, в названиях которых присутствуют определенные слова, указанные пользователем.", dbmanager.get_vacancies_with_keyword)
    }

    print('Доступные режимы вывода и фильтрации информации из базы данных')
    print()
    for key, (description, method) in filters.items():
        print(key, description)

    while True:
        user_input = input('Выберите номер фильтрации, который вас интересует: ')
        if user_input.lower() == 'exit' or user_input.lower() == 'quit':
            print("Exiting...")
            break
        elif user_input in ['1', '2', '3', '4', '5']:
            if user_input == '5':
                keyword = input('Введите параметр поиска: ')
                method = filters[int(user_input)][1]
                result = method(keyword)
                for row in result:
                    print(*row)
                user_input_continue = input('Для продолжения нажмите любую клавишу или "exit" для выхода: ')
                if user_input_continue.lower() == 'exit':
                    break
            else:
                method = filters[int(user_input)][1]
                result = method()
                if isinstance(result, float):  # Проверяем, является ли результат числом с плавающей точкой
                    print(result)  # Просто печатаем результат, если это число
                else:
                    for row in result:
                        print(*row)  # Иначе итерируем по результату как обычно
                user_input_continue = input('Для продолжения нажмите любую клавишу или "exit" для выхода: ')
                if user_input_continue.lower() == 'exit':
                    break
        else:
            print('Пожалуйста, введите число от 1 до 5 или "exit" для выхода.')

    print("Конец работы функции printing")