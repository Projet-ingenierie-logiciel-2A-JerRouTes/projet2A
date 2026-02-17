-----------------------------------------------------
-- INITIALISATION DU SCHÉMA
-----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS projet_test_dao;
SET search_path TO projet_test_dao, public;

-----------------------------------------------------
-- TYPE : User Status
-----------------------------------------------------

DROP TYPE IF EXISTS user_status CASCADE;
CREATE TYPE user_status AS ENUM ('admin', 'user');

-----------------------------------------------------
-- TABLE : User
-----------------------------------------------------

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status user_status DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username);
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);

-----------------------------------------------------
-- TABLE : User Session (refresh tokens)
-----------------------------------------------------

DROP TABLE IF EXISTS user_session CASCADE;
CREATE TABLE user_session (
    session_id SERIAL PRIMARY KEY,
    fk_user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP NULL,
    last_seen_at TIMESTAMP NULL,
    ip VARCHAR(64),
    user_agent TEXT
);

CREATE INDEX idx_user_session_user_id ON user_session(fk_user_id);
CREATE INDEX idx_user_session_expires_at ON user_session(expires_at);

ALTER TABLE user_session
ADD CONSTRAINT uq_user_session_refresh_token_hash UNIQUE (refresh_token_hash);

-----------------------------------------------------
-- TABLE : Stock
-----------------------------------------------------

DROP TABLE IF EXISTS stock CASCADE;
CREATE TABLE stock (
    stock_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-----------------------------------------------------
-- TYPE : Unit Type
-----------------------------------------------------

DROP TYPE IF EXISTS unit_type CASCADE;
CREATE TYPE unit_type AS ENUM (
    'g', 'kg', 'mg', 'oz', 'lb',
    'ml', 'L', 'fl_oz',
    'cm', 'm',
    'pcs'
);

-----------------------------------------------------
-- TABLE : Ingredient
-----------------------------------------------------

DROP TABLE IF EXISTS ingredient CASCADE;
CREATE TABLE ingredient (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit unit_type
);

CREATE UNIQUE INDEX uq_ingredient_name_lower
ON ingredient (LOWER(name));

-----------------------------------------------------
-- TABLE : Recipe
-----------------------------------------------------

DROP TABLE IF EXISTS recipe CASCADE;
CREATE TABLE recipe (
    recipe_id SERIAL PRIMARY KEY,
    fk_user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
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
    FOREIGN KEY (fk_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_stock_id) REFERENCES stock(stock_id) ON DELETE CASCADE
);

-----------------------------------------------------
-- TABLE : Stock_Item  (LOTS)
-- 1 ligne = 1 lot d’un ingrédient dans un stock
-----------------------------------------------------

DROP TABLE IF EXISTS stock_item CASCADE;
CREATE TABLE stock_item (
    stock_item_id SERIAL PRIMARY KEY,
    fk_stock_id INT NOT NULL REFERENCES stock(stock_id) ON DELETE CASCADE,
    fk_ingredient_id INT NOT NULL REFERENCES ingredient(ingredient_id) ON DELETE CASCADE,
    quantity NUMERIC(10,2) NOT NULL CHECK (quantity >= 0),
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index utiles (recherche par stock, par ingrédient, et tri FEFO)
CREATE INDEX idx_stock_item_stock ON stock_item(fk_stock_id);
CREATE INDEX idx_stock_item_ingredient ON stock_item(fk_ingredient_id);
CREATE INDEX idx_stock_item_stock_ingredient ON stock_item(fk_stock_id, fk_ingredient_id);
CREATE INDEX idx_stock_item_stock_expiration ON stock_item(fk_stock_id, expiration_date);

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
