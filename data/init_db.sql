-----------------------------------------------------
-- TYPE : User Status
-----------------------------------------------------

DROP TYPE IF EXISTS user_status CASCADE;
CREATE TYPE user_status AS ENUM ('admin', 'user');

-----------------------------------------------------
-- TABLE : User
-----------------------------------------------------

DROP TABLE IF EXISTS user CASCADE;
CREATE TABLE user (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status user_status DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-----------------------------------------------------
-- TABLE : Stock
-----------------------------------------------------

DROP TABLE IF EXISTS stock CASCADE;
CREATE TABLE stock (
    stock_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-----------------------------------------------------
-- TABLE : Ingredient
-----------------------------------------------------

DROP TABLE IF EXISTS ingredient CASCADE;
CREATE TABLE ingredient (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(50)
);

-----------------------------------------------------
-- TABLE : Recipe
-----------------------------------------------------

DROP TABLE IF EXISTS recipe CASCADE;
CREATE TABLE recipe (
    recipe_id SERIAL PRIMARY KEY,
    fk_user_id INT REFERENCES user(user_id) ON DELETE SET NULL,
    name VARCHAR(150) NOT NULL,
    status VARCHAR(50),
    prep_time INT CHECK (prep_time >= 0),          -- temps de préparation en minutes
    portion INT CHECK (portion > 0),               -- nombre de portions
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-----------------------------------------------------
-- TABLE : Tag
-----------------------------------------------------

DROP TABLE IF EXISTS tag CASCADE;
CREATE TABLE tag (
    tag_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-----------------------------------------------------
-- TABLE : User_Stock
-----------------------------------------------------

DROP TABLE IF EXISTS user_stock CASCADE;
CREATE TABLE user_stock (
    fk_user_id INT NOT NULL,
    fk_stock_id INT NOT NULL,
    PRIMARY KEY (fk_user_id, fk_stock_id),
    FOREIGN KEY (fk_user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_stock_id) REFERENCES stock(stock_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- TABLE : Stock_Ingredient
-----------------------------------------------------

DROP TABLE IF EXISTS stock_ingredient CASCADE;
CREATE TABLE stock_ingredient (
    fk_stock_id INT NOT NULL,
    fk_ingredient_id INT NOT NULL,
    quantity NUMERIC(10,2),
    expiration_date DATE,
    PRIMARY KEY (fk_stock_id, fk_ingredient_id),
    FOREIGN KEY (fk_stock_id) REFERENCES stock(stock_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- TABLE : Recipe_Ingredient
-----------------------------------------------------

DROP TABLE IF EXISTS recipe_ingredient CASCADE;
CREATE TABLE recipe_ingredient (
    fk_recipe_id INT NOT NULL,
    fk_ingredient_id INT NOT NULL,
    quantity NUMERIC(10,2),
    PRIMARY KEY (fk_recipe_id, fk_ingredient_id),
    FOREIGN KEY (fk_recipe_id) REFERENCES recipe(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- TABLE : Recipe_Tag
-----------------------------------------------------

DROP TABLE IF EXISTS recipe_tag CASCADE;
CREATE TABLE recipe_tag (
    fk_recipe_id INT NOT NULL,
    fk_tag_id INT NOT NULL,
    PRIMARY KEY (fk_recipe_id, fk_tag_id),
    FOREIGN KEY (fk_recipe_id) REFERENCES recipe(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- TABLE : Ingredient_Tag
-----------------------------------------------------

DROP TABLE IF EXISTS ingredient_tag CASCADE;
CREATE TABLE ingredient_tag (
    fk_ingredient_id INT NOT NULL,
    fk_tag_id INT NOT NULL,
    PRIMARY KEY (fk_ingredient_id, fk_tag_id),
    FOREIGN KEY (fk_ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_tag_id) REFERENCES tag(tag_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- TABLE : Ingredient Substitution
-----------------------------------------------------

DROP TABLE IF EXISTS ingredient_substitution CASCADE;
CREATE TABLE ingredient_substitution (
    fk_ingredient_id INT NOT NULL,
    fk_substitute_id INT NOT NULL,
    ratio NUMERIC(5,2),  -- ratio de substitution (ex: 0.8)
    PRIMARY KEY (fk_ingredient_id, fk_substitute_id),
    FOREIGN KEY (fk_ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_substitute_id) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE,
    CHECK (fk_ingredient_id <> fk_substitute_id)
);

-----------------------------------------------------
-- INDEX
-----------------------------------------------------

CREATE INDEX idx_recipe_name ON recipe(name);
CREATE INDEX idx_ingredient_name ON ingredient(name);
CREATE INDEX idx_tag_name ON tag(name);
