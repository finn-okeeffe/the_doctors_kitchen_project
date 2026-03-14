CREATE TABLE diet (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);

CREATE TABLE recipe (
    id SERIAL PRIMARY KEY,
    url VARCHAR(512) not null,
    title varchar(512) not null,
    description varchar(1024),
    diet_id INT,
    num_servings smallint,
    prep_time smallint,
    cook_time smallint,
    method text,
    last_update timestamp not null,
    foreign key (diet_id) references diet (id)
);

CREATE TABLE meal (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    recipe_id INT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON DELETE CASCADE
);

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE recipe_equipment (
    id SERIAL PRIMARY KEY,
    recipe_id INT NOT NULL,
    equipment_id INT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment (id) ON DELETE CASCADE
);

create table  equipment_synonym (
	equipment_id INT,
	synonym VARCHAR(100),
	foreign key (equipment_id) references equipment(id)
);


CREATE TABLE ingredient (
    id SERIAL PRIMARY KEY,
    recipe_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    quantity numeric,
    unit VARCHAR(10),
    preparation VARCHAR(50),
    FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON DELETE CASCADE
);
