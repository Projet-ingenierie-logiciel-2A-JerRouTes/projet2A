SET search_path TO projet_dao, public;

-----------------------------------------------------
-- INSERT : Users (Généré avec le script dans les tests)
-----------------------------------------------------

INSERT INTO users (username, email, password_hash, status)
VALUES
('alice', 'alice@example.com', '$2b$12$3AT9XjBMYC7SSxzDMWB8SOPwo7h1kbXDGEQbIT3RQyIPE4hdW0VGm', 'user'),
('bob', 'bob@example.com', '$2b$12$.kxjZWdtgCgAnnsaWqZ3Du4izzNhWYFwRyUL.eoi9AEl2EisUiUx.', 'user'),
('admin', 'admin@example.com', '$2b$12$0kpkiPvqOdfvxrm1FfSxCeF5zviYlQ.ulSxYsAqEzLnNzmCahuvC.', 'admin');

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
('Egg', 'pcs'),
('Milk', 'ml'),
('Flour', 'g'),
('Sugar', 'g'),
('Butter', 'g'),
('Salt', 'g');

INSERT INTO ingredient (name, unit) VALUES
('Pasta', 'g'),
('Guanciale', 'g'),
('Pecorino', 'g'),
('Chicken Breast', 'g'),
('Romaine Lettuce', 'pcs'),
('Beef', 'g'),
('Broccoli', 'g'),
('Soy Sauce', 'ml'),
('Chickpeas', 'g'),
('Coconut Milk', 'ml'),
('Mixed Berries', 'g'),
('Avocado', 'pcs'),
('Arborio Rice', 'g'),
('Mushrooms', 'g'),
('Bread Slice', 'pcs'),
('Cheddar', 'g'),
('Lentils', 'g');

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
-- INSERT : Stock_Item (gestion par lots)
-----------------------------------------------------

INSERT INTO stock_item (fk_stock_id, fk_ingredient_id, quantity, expiration_date) VALUES
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


INSERT INTO recipe (fk_user_id, name, status, prep_time, portion, description) VALUES
(1, 'Spaghetti Carbonara', 'published', 20, 2, 'Traditional Italian pasta with guanciale and pecorino'),
(1, 'Chicken Caesar Salad', 'published', 15, 1, 'Fresh romaine lettuce with grilled chicken and croutons'),
(1, 'Beef Stir-fry', 'draft', 25, 3, 'Quick wok-seared beef with seasonal vegetables'),
(1, 'Vegetable Curry', 'published', 40, 4, 'Spicy and hearty chickpea and coconut milk curry'),
(1, 'Berry Smoothie Bowl', 'draft', 5, 1, 'Frozen mixed berries blended with almond milk and topped with granola'),
(1, 'Guacamole', 'published', 10, 2, 'Creamy avocado dip with lime and cilantro'),
(1, 'Mushroom Risotto', 'draft', 45, 2, 'Slow-cooked arborio rice with earthy mushrooms'),
(1, 'Grilled Cheese Sandwich', 'published', 8, 1, 'Sourdough bread with melted cheddar and butter'),
(1, 'Lentil Soup', 'published', 50, 4, 'Warm protein-rich soup with carrots and cumin'),
(1, 'Chocolate Lava Cake', 'draft', 15, 2, 'Rich chocolate dessert with a melting heart');

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

-- Recipe 3: Beef Stir-fry
INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(3, 12, 300), -- Beef
(3, 13, 150), -- Broccoli
(3, 14, 30);  -- Soy Sauce

-- Recipe 4: Vegetable Curry
INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(4, 15, 400), -- Chickpeas
(4, 16, 200), -- Coconut Milk
(4, 6, 5);    -- Salt

-- Recipe 5: Berry Smoothie Bowl
INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(5, 17, 150), -- Mixed Berries
(5, 2, 100);  -- Milk

-- Recipe 6: Guacamole
INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(6, 18, 2),   -- Avocado
(6, 6, 2);    -- Salt

-- Recipe 7: Mushroom Risotto
INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(7, 19, 200), -- Arborio Rice
(7, 20, 100), -- Mushrooms
(7, 5, 30);   -- Butter

-- Recipe 8: Grilled Cheese Sandwich
INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(8, 21, 2),   -- Bread
(8, 22, 40),  -- Cheddar
(8, 5, 10);   -- Butter

-- Recipe 9: Lentil Soup
INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(9, 23, 200), -- Lentils
(9, 6, 5);    -- Salt

-- Recipe 10: Chocolate Lava Cake
INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity) VALUES
(10, 5, 50),  -- Butter
(10, 1, 2),   -- Egg
(10, 4, 40),  -- Sugar
(10, 3, 20);  -- Flour


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
