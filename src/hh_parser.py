"""
Module contains functions for interacting with the HH API and saving data to the database.
"""

import requests
import psycopg2

def get_employees(company_name):
    """
    Retrieves the employer ID based on the company name through the HH API.

    :param company_name: Name of the company to search for
    :return: Employer ID or None if the company is not found
    """
    url = 'https://api.hh.ru/employers'
    params = {'text': company_name}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        employers_data = response.json()
        if 'items' in employers_data and len(employers_data['items']) > 0:
            for employer in employers_data['items']:
                if employer['name'] == company_name:
                    return employer['id']
        else:
            print("Company not found.")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def get_employees_vacancies(employer_id):
    """
    Retrieves a list of vacancies for a given employer ID through the HH API.

    :param employer_id: ID of the employer
    :return: List of dictionaries with vacancy data or None upon error
    """
    all_vacancies = []
    url = 'https://api.hh.ru/vacancies'
    page = 0
    per_page = 100
    while page < 20:
        params = {'employer_id': employer_id, 'per_page': per_page, 'page': page}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            vacancies_data = response.json()
            if vacancies_data['items']:
                all_vacancies.extend(vacancies_data['items'])
                page += 1
            else:
                break
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    return all_vacancies

def save_database(company_name, data, database_name, params):
    """
    Saves vacancy data to the database.

    :param company_name: Name of the company
    :param data: List of dictionaries with vacancy data
    :param database_name: Name of the database
    :param params: Database connection parameters
    """
    conn = psycopg2.connect(**params)

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO company (employer)
            VALUES (%s)
            RETURNING  company_id
            """, (company_name,))
        company_id = cur.fetchone()[0]
        for vacancy_data in data:
            if vacancy_data['salary'] is None:
                cur.execute("""
                    INSERT INTO vacancy (company_id, name_vacancy, publish_date, url, salary_from, salary_to)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (company_id, vacancy_data['name'], vacancy_data['published_at'], vacancy_data['alternate_url'], 0, 0))
                continue
            elif vacancy_data['salary'] is not None:
                if vacancy_data['salary']['from'] is not None:
                    if vacancy_data['salary']['to'] is not None:
                        cur.execute("""
                            INSERT INTO vacancy (company_id, name_vacancy, publish_date, url, salary_from, salary_to)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (company_id, vacancy_data['name'], vacancy_data['published_at'], vacancy_data['alternate_url'], vacancy_data['salary']['from'], vacancy_data['salary']['to']))
                        continue
                    elif vacancy_data['salary']['to'] is None:
                        cur.execute("""
                            INSERT INTO vacancy (company_id, name_vacancy, publish_date, url, salary_from, salary_to)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (company_id, vacancy_data['name'], vacancy_data['published_at'], vacancy_data['alternate_url'], vacancy_data['salary']['from'], 0))
                        continue
                elif vacancy_data['salary']['to'] is not None:
                    cur.execute("""
                        INSERT INTO vacancy (company_id, name_vacancy, publish_date, url, salary_from, salary_to)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (company_id, vacancy_data['name'], vacancy_data['published_at'], vacancy_data['alternate_url'], 0, vacancy_data['salary']['to']))
                    continue

    conn.commit()
    conn.close()