CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Memberships (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(id),
    start_date DATE,
    end_date DATE
);