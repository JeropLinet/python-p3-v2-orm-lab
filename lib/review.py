from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances"""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances"""
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        self.validate_year(self.year)
        self.validate_summary_length(self.summary)

        sql = '''
            INSERT INTO reviews(year,summary,employee_id)
            VALUES(?,?,?)
        '''
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save the object to the database. Return the new instance."""
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        # Check the dictionary for an existing instance using the row's primary key
        review = cls.all.get(row[0])
        if review:
            # Update the existing instance's attributes if it exists
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            # Create a new instance if it doesn't exist in the dictionary
            review = cls(row[1], row[2], row[3])
            review.id = row[0]
            cls.all[review.id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance corresponding to its db row retrieved by id."""
        sql = """
            SELECT *
            FROM reviews
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update an instance's corresponding database record to match its new attribute values."""
        self.validate_year(self.year)
        self.validate_summary_length(self.summary)

        sql = """
            UPDATE reviews
            SET year=?, summary=?, employee_id=?
            WHERE id=?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete an instance's corresponding database record."""
        sql = """
            DELETE FROM reviews
            WHERE id=?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

    @classmethod
    def get_all(cls):
        """Return a list of Review instances for every record in the db."""
        sql = """
            SELECT *
            FROM reviews
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def validate_year(cls, year):
     """Validate that the year property length is greater than or equal to 2000."""
     if  not isinstance(year, int):
        raise TypeError("Year must be an integer.")
     elif year < 2000:
         raise ValueError("Year must be greater than or equal to 2000.")
     else:
         return True


    @classmethod
    def validate_summary_length(cls, summary):
        """Validate that the summary property length is greater than 0."""
        if len(summary) == 0:
            raise ValueError("Summary must have a length greater than 0.")
        
    def validate_employee_id(self, employee_id):
        """Validate that the employee ID exists."""
        if not Employee.exists(employee_id):
            raise ValueError("Employee ID does not exist.")