"""
Database management class for creating and interacting with a PostgreSQL database.
"""

import psycopg2
import logging

class DBManager:
    """
    Initializes the DBManager instance with database name and connection parameters.

    :param database_name: Name of the database to connect to.
    :param params: Dictionary of database connection parameters.
    """
    def __init__(self, database_name, params):
        self.params = params
        self.database_name = database_name
        self._connection = None
        # Исправляем использование disabled вместо disable
        logging.getLogger(__name__).disabled = True

    def create_db(self, database_name='hh_vacancy'):
        """
        Creates a new PostgreSQL database.

        :param database_name: Name of the database to create.
        """
        conn = psycopg2.connect(**self.params)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
            cur.execute(f"CREATE DATABASE {database_name}")

    def create_table(self):
        """
        Creates tables for storing company and vacancy data in the database.
        """
        self.params['dbname'] = 'hh_vacancy'
        conn = psycopg2.connect(**self.params)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE company (
                    company_id SERIAL PRIMARY KEY,
                    employer VARCHAR(50) NOT NULL
                )
            """)

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE vacancy(
                    vacancy_id SERIAL PRIMARY KEY,
                    company_id INT REFERENCES company(company_id),
                    name_vacancy VARCHAR NOT NULL,
                    publish_date DATE,
                    url TEXT,
                    salary_from INTEGER,
                    salary_to INTEGER
                )
            """)
        conn.commit()
        conn.close()

    def create_connection(self):
        """
        Establishes a connection to the database.

        :return: Connection object.
        """
        if self._connection is None:
            with psycopg2.connect(**self.params) as conn:
                self._connection = conn
        return self._connection

    def get_companies_and_vacancies_count(self):
        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute("""
            SELECT company.employer, COUNT(vacancy.vacancy_id) as vacancies_count
            FROM company 
            JOIN vacancy  ON company.company_id = vacancy.company_id
            GROUP BY company.employer
            ORDER BY vacancies_count DESC
            """)

        companies_vacancies_count = cur.fetchall()
        cur.close()
        conn.close()

        return companies_vacancies_count

    def get_all_vacancies(self):
        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute("""
            SELECT employer, name_vacancy, salary_from, salary_to,url 
            FROM vacancy
            JOIN company  ON company.company_id = vacancy.company_id
            ORDER BY salary_from DESC
            """)
        all_vacancies = cur.fetchall()
        cur.close()
        conn.close()
        return all_vacancies

    def get_avg_salary(self):
        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute("SELECT AVG(salary_from)::float FROM vacancy")
        avg_salary = cur.fetchone()[0]
        cur.close()
        conn.close()
        return avg_salary

    def get_vacancies_with_higher_salary(self):
        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        avg_salary = self.get_avg_salary()
        cur.execute("SELECT name_vacancy, salary_from, salary_to, url FROM vacancy WHERE salary_from > %s", (avg_salary,))
        vacancies = cur.fetchall()

        cur.close()
        conn.close()

        return vacancies

    def get_vacancies_with_keyword(self, keyword):
        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute("SELECT name_vacancy, salary_from, salary_to, url FROM vacancy WHERE name_vacancy LIKE %s", ('%' + keyword + '%',))
        vacancies = cur.fetchall()
        cur.close()
        conn.close()
        return vacancies

    def close_connection(self):
        """
        Closes the current database connection.
        """
        conn = self.create_connection()
        conn.close()