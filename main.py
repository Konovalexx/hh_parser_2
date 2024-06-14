"""
Main script to scrape employee and vacancy data from HeadHunter and store it in a PostgreSQL
database.
"""

from src.config import config
from src.dbmanager import DBManager
from src.hh_parser import get_employees, get_employees_vacancies, save_database
from src.utils import printing

def main():
    """
    Main function that orchestrates the scraping and storing process.
    """
    params = config()
    dbmanager = DBManager('hh_vacancy', params)

    dbmanager.create_db()
    dbmanager.create_table()
    dbmanager.close_connection()

    companies = [
        "Яндекс", "Skyeng", "Ozon", "СБЕР", "СКБ Приморья Примсоцбанк", "Додо Пицца", "Банк Приморье",
        "Светофор, Сеть магазинов низких цен", "DNS Головной офис", "Авито"
    ]

    for company_name in companies:
        employer_id = get_employees(company_name)

        if employer_id:
            print(f"Company ID: {employer_id}")
            vacancies = get_employees_vacancies(employer_id)

            if vacancies:
                save_database(company_name, vacancies, 'hh_vacancy', params)
                print(f"Data for {company_name} saved successfully.")
            else:
                print(f"No vacancies found for {company_name}.")
        else:
            print(f"{company_name} not found.")

    printing(dbmanager)

if __name__ == "__main__":
    main()