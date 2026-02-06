-----------------------------------------------------
-- INSERT : Users
-----------------------------------------------------

INSERT INTO users (username, email, password_hash, status) VALUES
('admin', 'admin@mail.com', 'mdpAdmin123', 'admin'),
('alice', 'alice@mail.com', 'mdpAlice123', 'user'),
('bob', 'bob@mail.com', 'mdpBob123', 'user');

-----------------------------------------------------
-- INSERT : Stock
-----------------------------------------------------

INSERT INTO stock (name) VALUES
('Fridge'),
('Pantry');

-----------------------------------------------------
-- INSERT : Ingredient
-----------------------------------------------------

INSERT INTO ingredient (name, unit) VALUES
('Egg', 'piece'),
('Milk', 'ml'),
('Flour', 'g'),
('Sugar', 'g'),
('Butter', 'g'),
('Salt', 'g');

-----------------------------------------------------
-- INSERT : Tag
-----------------------------------------------------

INSERT INTO tag (name) VALUES
('Vegetarian'),
('Dessert'),
('Quick'),
('Breakfast');

-----------------------------------------------------
-- INSERT : User_Stock
-----------------------------------------------------

INSERT INTO user_stock (fk_user_id, fk_stock_id) VALUES
(2, 1),
(2, 2),
(3, 2);

-----------------------------------------------------
-- INSERT : Stock_Ingredient
-----------------------------------------------------

INSERT INTO stock_ingredient (fk_stock_id, fk_ingredient_id, quantity, expiration_date) VALUES
(1, 1, 6, '2026-03-01'),
(1, 2, 1000, '2026-02-20'),
(1, 5, 250, '2026-02-25'),
(2, 3, 1000, '2026-12-31'),
(2, 4, 500, '2026-12-31'),
(2, 6, 100, '2027-01-01');

-----------------------------------------------------
-- INSERT : Recipe
-----------------------------------------------------

INSERT INTO recipe (fk_user_id, name, status, prep_time, portion, description) VALUES
(2, 'Pancakes', 'published', 15, 4, 'Simple fluffy pancakes'),
(3, 'Scrambled Eggs', 'draft', 10, 2, 'Classic breakfast eggs');

-----------------------------------------------------
-- INSERT : Recipe_Ingredient
-----------------------------------------------------

INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(1, 1, 2),
(1, 2, 300),
(1, 3, 200),
(1, 4, 30),
(1, 5, 20),
(2, 1, 3),
(2, 5, 10),
(2, 6, 2);

-----------------------------------------------------
-- INSERT : Recipe_Tag
-----------------------------------------------------

INSERT INTO recipe_tag (fk_recipe_id, fk_tag_id) VALUES
(1, 2),
(1, 4),
(2, 4),
(2, 3);

-----------------------------------------------------
-- INSERT : Ingredient_Tag
-----------------------------------------------------

INSERT INTO ingredient_tag (fk_ingredient_id, fk_tag_id) VALUES
(1, 4),
(2, 4),
(3, 2),
(4, 2);

-----------------------------------------------------
-- INSERT : Ingredient Substitution
-----------------------------------------------------

INSERT INTO ingredient_substitution (fk_ingredient_id, fk_substitute_id, ratio) VALUES
(5, 2, 0.8),   -- beurre remplacé par lait
(4, 3, 0.9);   -- sucre remplacé par farine
